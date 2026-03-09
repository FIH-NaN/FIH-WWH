from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import json
import math
import re
import time
from typing import Dict, List
import requests

from sqlalchemy.orm import Session

from src.server.config import get_settings
from src.server.db.tables.assets import Asset
from src.server.db.tables.insights import AIInsightSnapshot
from src.server.db.tables.plaid_transactions import PlaidTransaction
from src.server.db.tables.portfolio_snapshot import PortfolioSnapshot
from src.server.db.tables.wallet import AccountConnection, AccountProvider, AccountType, ExternalHolding


@dataclass
class _Factor:
    name: str
    score: int
    weight: float
    detail: str


class WellnessMetricsService:
    """Builds deterministic, explainable wealth wellness metrics from current DB state."""

    _BUCKETS = ("cash", "stocks", "bonds", "crypto", "real_estate", "other")

    @classmethod
    def build_overview(cls, db: Session, user_id: int) -> Dict:
        context = cls._portfolio_context(db=db, user_id=user_id)

        return {
            "total_portfolio_usd": round(context["total_portfolio_usd"], 2),
            "overall_score": context["overall_score"],
            "grade": cls._score_to_grade(context["overall_score"]),
            "factors": [
                {
                    "name": f.name,
                    "score": f.score,
                    "weight": f.weight,
                    "detail": f.detail,
                }
                for f in context["factors"]
            ],
            "allocation": cls._build_allocation(context["bucket_values"], context["total_portfolio_usd"]),
            "recommendations": [],
            "insight_source": "pending",
            "insight_provider": "minimax",
            "insight_error": None,
            "data_quality": {
                "connected_accounts": len(context["connections"]),
                "holdings_count": len(context["holdings"]),
                "manual_assets_count": context["manual_assets_included"],
                "last_synced_at": cls._last_sync_iso(context["connections"]),
            },
        }

    @classmethod
    def record_daily_snapshot(cls, db: Session, user_id: int, source: str = "sync") -> None:
        """Upsert today's portfolio valuation snapshot for trend analytics."""
        context = cls._portfolio_context(db=db, user_id=user_id)
        cls._upsert_snapshot(
            db=db,
            user_id=user_id,
            snapshot_date=date.today(),
            total_value_usd=float(context["total_portfolio_usd"]),
            bucket_values=context["bucket_values"],
            source=source,
        )

    @classmethod
    def build_portfolio_analysis(cls, db: Session, user_id: int) -> Dict:
        context = cls._portfolio_context(db=db, user_id=user_id)
        total_value = float(context["total_portfolio_usd"])
        composition = cls._build_portfolio_composition(context["bucket_values"], total_value)
        performance, performance_source = cls._build_12_month_performance(db=db, user_id=user_id, current_total=total_value)
        frontier = cls._build_frontier_analysis(context=context, monthly_performance=performance)

        ytd_points = [point for point in performance if str(point["month_key"]).startswith(f"{date.today().year}-")]
        ytd_pnl = sum(float(point["pnl_usd"]) for point in ytd_points)
        avg_monthly = (sum(float(point["pnl_usd"]) for point in performance) / len(performance)) if performance else 0.0

        return {
            "total_value_usd": round(total_value, 2),
            "ytd_pnl_usd": round(ytd_pnl, 2),
            "avg_monthly_pnl_usd": round(avg_monthly, 2),
            "performance_source": performance_source,
            "composition": composition,
            "performance_12m": [
                {
                    "month_key": point["month_key"],
                    "month": point["month"],
                    "total_value_usd": point["total_value_usd"],
                    "income_usd": point.get("income_usd", 0.0),
                    "expense_usd": point.get("expense_usd", 0.0),
                    "pnl_usd": point["pnl_usd"],
                    "pnl_pct": point["pnl_pct"],
                }
                for point in performance
            ],
            "efficient_frontier": frontier["efficient_frontier"],
            "sub_optimal_points": frontier["sub_optimal_points"],
            "user_position": frontier["user_position"],
            "optimization_insight": frontier["optimization_insight"],
        }

    @classmethod
    def build_ai_insights(cls, db: Session, user_id: int) -> Dict:
        latest_success = (
            db.query(AIInsightSnapshot)
            .filter(
                AIInsightSnapshot.user_id == user_id,
                AIInsightSnapshot.status == "success",
            )
            .order_by(AIInsightSnapshot.generated_at.desc(), AIInsightSnapshot.id.desc())
            .first()
        )

        if latest_success is None:
            return {
                "recommendations": [],
                "insight_source": "cached",
                "insight_provider": "minimax",
                "insight_status": "empty",
                "insight_error": "No cached AI insights yet. Click refresh to generate.",
                "generated_at": None,
                "duration_ms": None,
            }

        recommendations = cls._deserialize_recommendations(getattr(latest_success, "recommendations_json"))
        return {
            "recommendations": recommendations,
            "insight_source": "cached",
            "insight_provider": str(getattr(latest_success, "provider") or "minimax"),
            "insight_status": str(getattr(latest_success, "status") or "success"),
            "insight_error": getattr(latest_success, "error_message"),
            "generated_at": getattr(latest_success, "generated_at"),
            "duration_ms": getattr(latest_success, "duration_ms"),
        }

    @classmethod
    def refresh_ai_insights(cls, db: Session, user_id: int) -> Dict:
        context = cls._portfolio_context(db=db, user_id=user_id)
        started_at = datetime.utcnow()
        t0 = time.perf_counter()

        recommendations, error_message = cls._generate_minimax_recommendations(
            buckets=context["bucket_values"],
            total=context["total_portfolio_usd"],
            factors=context["factors"],
        )
        duration_ms = int((time.perf_counter() - t0) * 1000)

        status = "success" if recommendations else "error"
        if error_message and "timeout" in error_message.lower():
            status = "timeout"

        settings = get_settings()
        snapshot = AIInsightSnapshot(
            user_id=user_id,
            provider="minimax",
            model=(settings.MINIMAX_MODEL or "MiniMax-M2.5").strip(),
            status=status,
            recommendations_json=json.dumps(recommendations or []),
            source_context_json=json.dumps(
                {
                    "total_portfolio_usd": round(float(context["total_portfolio_usd"]), 2),
                    "factor_scores": {f.name: f.score for f in context["factors"]},
                }
            ),
            error_message=error_message,
            duration_ms=duration_ms,
            generated_at=started_at,
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)

        return {
            "recommendations": recommendations or [],
            "insight_source": "ai" if status == "success" else "error",
            "insight_provider": "minimax",
            "insight_status": status,
            "insight_error": error_message,
            "generated_at": getattr(snapshot, "generated_at"),
            "duration_ms": duration_ms,
        }

    @classmethod
    def list_ai_insights_history(cls, db: Session, user_id: int, limit: int = 10) -> Dict:
        rows = (
            db.query(AIInsightSnapshot)
            .filter(AIInsightSnapshot.user_id == user_id)
            .order_by(AIInsightSnapshot.generated_at.desc(), AIInsightSnapshot.id.desc())
            .limit(max(1, min(limit, 50)))
            .all()
        )

        items = []
        for row in rows:
            items.append(
                {
                    "id": int(getattr(row, "id")),
                    "insight_source": "cached" if str(getattr(row, "status") or "") == "success" else "error",
                    "insight_provider": str(getattr(row, "provider") or "minimax"),
                    "insight_status": str(getattr(row, "status") or "error"),
                    "recommendations": cls._deserialize_recommendations(getattr(row, "recommendations_json")),
                    "insight_error": getattr(row, "error_message"),
                    "generated_at": getattr(row, "generated_at"),
                    "duration_ms": getattr(row, "duration_ms"),
                }
            )

        return {"items": items}

    @staticmethod
    def _deserialize_recommendations(raw_payload: object) -> List[str]:
        if isinstance(raw_payload, str):
            try:
                parsed = json.loads(raw_payload)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except (TypeError, ValueError):
                return []
        if isinstance(raw_payload, list):
            return [str(item).strip() for item in raw_payload if str(item).strip()]
        return []

    @classmethod
    def _portfolio_context(cls, db: Session, user_id: int) -> Dict:
        manual_assets = db.query(Asset).filter(Asset.user_id == user_id).all()
        holdings = (
            db.query(ExternalHolding)
            .join(AccountConnection, ExternalHolding.account_connection_id == AccountConnection.id)
            .filter(ExternalHolding.user_id == user_id)
            .all()
        )
        connections = db.query(AccountConnection).filter(AccountConnection.user_id == user_id).all()

        linked_asset_ids = {
            int(getattr(holding, "asset_id"))
            for holding in holdings
            if getattr(holding, "asset_id", None) is not None
        }

        bucket_values = {bucket: 0.0 for bucket in cls._BUCKETS}
        manual_assets_included = 0

        for asset in manual_assets:
            if int(asset.id) in linked_asset_ids:
                continue
            bucket = cls._map_manual_asset_bucket(str(asset.asset_type))
            bucket_values[bucket] += float(asset.value or 0.0)
            manual_assets_included += 1

        for holding in holdings:
            bucket = cls._map_external_holding_bucket(holding)
            bucket_values[bucket] += float(getattr(holding, "value_usd") or 0.0)

        total_portfolio_usd = sum(bucket_values.values())
        factors = cls._compute_factors(bucket_values, total_portfolio_usd, connections)
        overall_score = cls._weighted_score(factors)

        return {
            "bucket_values": bucket_values,
            "total_portfolio_usd": total_portfolio_usd,
            "factors": factors,
            "overall_score": overall_score,
            "manual_assets_included": manual_assets_included,
            "holdings": holdings,
            "connections": connections,
        }

    @classmethod
    def _map_manual_asset_bucket(cls, asset_type: str) -> str:
        key = asset_type.lower()
        if any(token in key for token in ("cash", "deposit")):
            return "cash"
        if "bond" in key:
            return "bonds"
        if any(token in key for token in ("stock", "etf", "fund")):
            return "stocks"
        if "digital" in key or "crypto" in key:
            return "crypto"
        if "real_estate" in key or "property" in key:
            return "real_estate"
        return "other"

    @classmethod
    def _map_external_holding_bucket(cls, holding: ExternalHolding) -> str:
        connection = holding.connection
        if not connection:
            return "other"
        if connection.provider == AccountProvider.EVM:
            return "crypto"
        if connection.provider == AccountProvider.PLAID:
            security_type = cls._plaid_security_type_from_payload(getattr(holding, "raw_payload", None))
            if security_type in {"fixed income", "fixed_income"}:
                return "bonds"
            if security_type in {"equity", "etf", "mutual fund", "mutual_fund"}:
                return "stocks"
            if security_type == "cash":
                return "cash"
            if security_type == "cryptocurrency":
                return "crypto"

            plaid_type = cls._plaid_account_type_from_payload(getattr(holding, "raw_payload", None))
            if plaid_type in {"investment", "brokerage", "securities"}:
                return "stocks"
            if plaid_type in {"depository", "cash", "bank"}:
                return "cash"
            if connection.account_type == AccountType.BROKERAGE:
                return "stocks"
            if connection.account_type == AccountType.BANK:
                return "cash"
        return "other"

    @staticmethod
    def _plaid_security_type_from_payload(raw_payload: object) -> str:
        data: dict
        if isinstance(raw_payload, str):
            try:
                parsed = json.loads(raw_payload)
                data = parsed if isinstance(parsed, dict) else {}
            except (TypeError, ValueError):
                return ""
        elif isinstance(raw_payload, dict):
            data = raw_payload
        else:
            return ""

        security_type = data.get("security_type")
        if security_type:
            return str(security_type).strip().lower()
        raw_security = data.get("security")
        security = raw_security if isinstance(raw_security, dict) else {}
        return str(security.get("type") or "").strip().lower()

    @staticmethod
    def _plaid_account_type_from_payload(raw_payload: object) -> str:
        data: dict
        if isinstance(raw_payload, str):
            try:
                parsed = json.loads(raw_payload)
                data = parsed if isinstance(parsed, dict) else {}
            except (TypeError, ValueError):
                return ""
        elif isinstance(raw_payload, dict):
            data = raw_payload
        else:
            return ""

        account = data.get("account") if isinstance(data.get("account"), dict) else data
        account_type = account.get("type") if isinstance(account, dict) else None
        return str(account_type or "").strip().lower()

    @classmethod
    def _build_allocation(cls, buckets: Dict[str, float], total: float) -> List[Dict]:
        if total <= 0:
            return [
                {"bucket": bucket, "value_usd": 0.0, "weight_pct": 0.0}
                for bucket in cls._BUCKETS
            ]

        return [
            {
                "bucket": bucket,
                "value_usd": round(buckets[bucket], 2),
                "weight_pct": round((buckets[bucket] / total) * 100, 2),
            }
            for bucket in cls._BUCKETS
        ]

    @classmethod
    def _compute_factors(
        cls,
        buckets: Dict[str, float],
        total: float,
        connections: List[AccountConnection],
    ) -> List[_Factor]:
        diversification = cls._diversification_score(buckets, total)
        liquidity = cls._liquidity_score(buckets, total)
        risk = cls._risk_balance_score(buckets, total)
        freshness = cls._freshness_score(connections)

        return [
            _Factor("Diversification", diversification, 0.30, cls._diversification_detail(buckets, total)),
            _Factor("Liquidity", liquidity, 0.25, cls._liquidity_detail(buckets, total)),
            _Factor("Risk Balance", risk, 0.25, cls._risk_detail(buckets, total)),
            _Factor("Data Freshness", freshness, 0.20, cls._freshness_detail(connections)),
        ]

    @staticmethod
    def _weighted_score(factors: List[_Factor]) -> int:
        if not factors:
            return 0
        weighted = sum(f.score * f.weight for f in factors)
        return max(0, min(100, int(round(weighted))))

    @staticmethod
    def _score_to_grade(score: int) -> str:
        if score >= 85:
            return "A"
        if score >= 70:
            return "B"
        if score >= 55:
            return "C"
        return "D"

    @classmethod
    def _diversification_score(cls, buckets: Dict[str, float], total: float) -> int:
        if total <= 0:
            return 0
        weights = [value / total for value in buckets.values() if value > 0]
        if len(weights) <= 1:
            return 25
        hhi = sum(w * w for w in weights)
        max_concentration = 1.0
        min_concentration = 1.0 / len(cls._BUCKETS)
        normalized = (max_concentration - hhi) / (max_concentration - min_concentration)
        return int(max(0, min(100, round(normalized * 100))))

    @staticmethod
    def _liquidity_score(buckets: Dict[str, float], total: float) -> int:
        if total <= 0:
            return 0
        liquid = buckets["cash"] + (0.85 * buckets["stocks"]) + (0.75 * buckets["bonds"]) + (0.65 * buckets["crypto"])
        ratio = liquid / total
        return int(max(0, min(100, round(ratio * 100))))

    @staticmethod
    def _risk_balance_score(buckets: Dict[str, float], total: float) -> int:
        if total <= 0:
            return 0
        crypto_share = buckets["crypto"] / total
        cash_share = buckets["cash"] / total
        score = 85
        if crypto_share > 0.55:
            score -= int((crypto_share - 0.55) * 180)
        if cash_share < 0.08:
            score -= int((0.08 - cash_share) * 220)
        if buckets["real_estate"] / total > 0.65:
            score -= 8
        return max(20, min(100, score))

    @staticmethod
    def _freshness_score(connections: List[AccountConnection]) -> int:
        if not connections:
            return 35
        timestamps = [c.last_synced_at for c in connections if c.last_synced_at is not None]
        if not timestamps:
            return 40
        newest = max(timestamps)
        now = datetime.now(timezone.utc)
        if newest.tzinfo is None:
            newest = newest.replace(tzinfo=timezone.utc)
        age_hours = max(0.0, (now - newest).total_seconds() / 3600)
        if age_hours <= 6:
            return 95
        if age_hours <= 24:
            return 85
        if age_hours <= 72:
            return 70
        if age_hours <= 168:
            return 55
        return 40

    @classmethod
    def _generate_minimax_recommendations(
        cls,
        buckets: Dict[str, float],
        total: float,
        factors: List[_Factor],
    ) -> tuple[List[str] | None, str | None]:
        settings = get_settings()
        api_key = (settings.MINIMAX_API_KEY or "").strip()
        model = (settings.MINIMAX_MODEL or "MiniMax-M2.5").strip()
        api_url = (settings.MINIMAX_API_URL or "https://api.minimaxi.com/anthropic/v1/messages").strip()
        if not api_key:
            return None, "MINIMAX_API_KEY is not configured"
        if total <= 0:
            return None, "No portfolio data"

        factor_text = ", ".join(f"{f.name}:{f.score}" for f in factors)
        allocation_text = ", ".join(
            f"{bucket}={((value / total) * 100):.1f}%" for bucket, value in buckets.items() if total > 0
        )
        prompt = (
            "You are a financial wellness assistant. Based on current portfolio diagnostics, "
            "return 2 to 4 concise, actionable recommendations in plain English. "
            "Avoid markdown, and do not include disclaimers. "
            "Respond as a JSON array of strings only.\n"
            f"Total portfolio (USD): {total:.2f}.\n"
            f"Allocation: {allocation_text}.\n"
            f"Factors: {factor_text}."
        )

        payload = {
            "model": model,
            "system": "You are a financial wellness assistant.",
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            "temperature": 0.4,
            # Coding Plan M2.5 may emit long thinking blocks before final text.
            # Use a larger token budget to avoid text being truncated away.
            "max_tokens": 1000,
        }

        try:
            resp = requests.post(
                api_url,
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60,
            )
            if resp.status_code != 200:
                try:
                    err_obj = resp.json()
                    err_text = str(err_obj.get("error") or err_obj.get("message") or "")
                except Exception:
                    err_text = resp.text[:200]
                return None, f"HTTP {resp.status_code}: {err_text}".strip()

            body = resp.json()
            if not isinstance(body, dict):
                return None, "MiniMax returned non-object response"

            base_resp = body.get("base_resp")
            if isinstance(base_resp, dict):
                status_code = int(base_resp.get("status_code") or 0)
                status_msg = str(base_resp.get("status_msg") or "")
                if status_code != 0:
                    return None, f"MiniMax {status_code}: {status_msg or 'provider error'}"

            text = cls._extract_minimax_text(body)

            if not text:
                stop_reason = str(body.get("stop_reason") or "")
                raw_content = body.get("content")
                content_blocks: List[object] = raw_content if isinstance(raw_content, list) else []
                has_thinking = any(
                    isinstance(block, dict) and str(block.get("type") or "") == "thinking"
                    for block in content_blocks
                )
                if stop_reason == "max_tokens" and has_thinking:
                    return None, "MiniMax exhausted tokens in thinking before text output"
                return None, f"MiniMax returned no text content (keys: {','.join(body.keys())})"

            cleaned = text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.strip("`")
                if cleaned.lower().startswith("json"):
                    cleaned = cleaned[4:].strip()

            normalized = cls._parse_recommendation_list(cleaned)
            if not normalized:
                return None, "MiniMax returned empty recommendations"
            return normalized[:4], None
        except Exception as exc:
            return None, str(exc)

    @staticmethod
    def _extract_minimax_text(body: Dict[str, object]) -> str:
        # Anthropic-compatible format: {content:[{type:"text", text:"..."}, ...]}
        content_blocks = body.get("content")
        if isinstance(content_blocks, list):
            for block in content_blocks:
                if isinstance(block, dict) and str(block.get("type") or "") == "text":
                    value = str(block.get("text") or "").strip()
                    if value:
                        return value

        # OpenAI-like fallback format: {choices:[{message:{content:"..."}}]}
        choices = body.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                message = first.get("message")
                if isinstance(message, dict):
                    content = message.get("content")
                    if isinstance(content, str) and content.strip():
                        return content.strip()
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and str(item.get("type") or "") == "text":
                                value = str(item.get("text") or "").strip()
                                if value:
                                    return value

        # Some providers return direct text fields.
        for key in ("output_text", "text", "response"):
            raw = body.get(key)
            if isinstance(raw, str) and raw.strip():
                return raw.strip()

        return ""

    @staticmethod
    def _parse_recommendation_list(cleaned_text: str) -> List[str]:
        # Prefer strict JSON array parsing.
        try:
            parsed = json.loads(cleaned_text)
            if isinstance(parsed, dict):
                parsed = parsed.get("recommendations", [])
            if isinstance(parsed, list):
                values = [str(item).strip() for item in parsed if str(item).strip()]
                if values:
                    return values
        except Exception:
            pass

        # Fallback: parse bullet/numbered lines from plain text.
        lines = [line.strip() for line in cleaned_text.splitlines() if line.strip()]
        values: List[str] = []
        for line in lines:
            normalized = re.sub(r"^[-*\d\.)\s]+", "", line).strip().strip('"')
            if normalized:
                values.append(normalized)
        return values

    @staticmethod
    def _month_sequence(count: int = 12) -> List[date]:
        today = date.today()
        months: List[date] = []
        for offset in range(count - 1, -1, -1):
            year = today.year
            month = today.month - offset
            while month <= 0:
                month += 12
                year -= 1
            months.append(date(year, month, 1))
        return months

    @classmethod
    def _build_12_month_performance(cls, db: Session, user_id: int, current_total: float) -> tuple[List[Dict[str, float | str]], str]:
        transaction_points = cls._build_transactions_12_month_performance(db=db, user_id=user_id)
        if transaction_points and any(abs(float(point.get("pnl_usd") or 0.0)) > 0.01 for point in transaction_points):
            return transaction_points, "transactions"

        months = cls._month_sequence(12)
        first_month = months[0]

        rows = (
            db.query(PortfolioSnapshot)
            .filter(
                PortfolioSnapshot.user_id == user_id,
                PortfolioSnapshot.snapshot_date >= first_month,
            )
            .order_by(PortfolioSnapshot.snapshot_date.asc(), PortfolioSnapshot.updated_at.asc())
            .all()
        )

        last_before_window = (
            db.query(PortfolioSnapshot)
            .filter(
                PortfolioSnapshot.user_id == user_id,
                PortfolioSnapshot.snapshot_date < first_month,
            )
            .order_by(PortfolioSnapshot.snapshot_date.desc(), PortfolioSnapshot.updated_at.desc())
            .first()
        )

        monthly_totals: Dict[str, float] = {}
        for row in rows:
            key = f"{row.snapshot_date.year:04d}-{row.snapshot_date.month:02d}"
            monthly_totals[key] = float(getattr(row, "total_value_usd") or 0.0)

        carry = float(getattr(last_before_window, "total_value_usd", None) or current_total or 0.0)
        if not rows and current_total > 0:
            carry = current_total

        points: List[Dict[str, float | str]] = []
        prev = carry
        for month_start in months:
            key = f"{month_start.year:04d}-{month_start.month:02d}"
            total = monthly_totals.get(key, carry)
            carry = total
            pnl = total - prev
            pnl_pct = (pnl / prev * 100) if prev > 0 else 0.0
            points.append(
                {
                    "month_key": key,
                    "month": month_start.strftime("%b"),
                    "total_value_usd": round(total, 2),
                    "income_usd": 0.0,
                    "expense_usd": 0.0,
                    "pnl_usd": round(pnl, 2),
                    "pnl_pct": round(pnl_pct, 2),
                }
            )
            prev = total

        return points, "snapshots"

    @classmethod
    def _build_transactions_12_month_performance(cls, db: Session, user_id: int) -> List[Dict[str, float | str]]:
        months = cls._month_sequence(12)
        first_month = months[0]

        rows = (
            db.query(PlaidTransaction)
            .filter(
                PlaidTransaction.user_id == user_id,
                PlaidTransaction.is_removed == False,  # noqa: E712
                PlaidTransaction.pending == False,  # noqa: E712
                PlaidTransaction.date_posted >= first_month,
            )
            .all()
        )

        aggregates: Dict[str, Dict[str, float]] = {}
        for row in rows:
            posted = getattr(row, "date_posted")
            if posted is None:
                continue
            key = f"{posted.year:04d}-{posted.month:02d}"
            if key not in aggregates:
                aggregates[key] = {"income": 0.0, "expense": 0.0}

            amount = float(getattr(row, "amount") or 0.0)
            if amount >= 0:
                aggregates[key]["expense"] += amount
            else:
                aggregates[key]["income"] += abs(amount)

        points: List[Dict[str, float | str]] = []
        for month_start in months:
            key = f"{month_start.year:04d}-{month_start.month:02d}"
            income = round(float(aggregates.get(key, {}).get("income", 0.0)), 2)
            expense = round(float(aggregates.get(key, {}).get("expense", 0.0)), 2)
            profit = round(income - expense, 2)
            pnl_pct = round(((profit / income) * 100) if income > 0 else 0.0, 2)
            points.append(
                {
                    "month_key": key,
                    "month": month_start.strftime("%b"),
                    "total_value_usd": 0.0,
                    "income_usd": income,
                    "expense_usd": expense,
                    "pnl_usd": profit,
                    "pnl_pct": pnl_pct,
                }
            )

        return points

    @classmethod
    def _build_portfolio_composition(cls, buckets: Dict[str, float], total: float) -> List[Dict[str, float | str]]:
        labels = {
            "cash": "Cash",
            "stocks": "Stocks",
            "bonds": "Bonds",
            "crypto": "Crypto",
            "real_estate": "Real Estate",
            "other": "Other",
        }
        colors = {
            "cash": "#64748b",
            "stocks": "#2563eb",
            "bonds": "#0ea5e9",
            "crypto": "#f59e0b",
            "real_estate": "#8b5cf6",
            "other": "#14b8a6",
        }
        items: List[Dict[str, float | str]] = []
        for bucket in cls._BUCKETS:
            value = float(buckets.get(bucket, 0.0) or 0.0)
            weight = (value / total * 100) if total > 0 else 0.0
            if value <= 0:
                continue
            items.append(
                {
                    "bucket": bucket,
                    "label": labels.get(bucket, "Other"),
                    "value_usd": round(value, 2),
                    "weight_pct": round(weight, 2),
                    "color": colors.get(bucket, "#14b8a6"),
                }
            )
        return sorted(items, key=lambda item: float(item["value_usd"]), reverse=True)

    @classmethod
    def _build_frontier_analysis(cls, context: Dict, monthly_performance: List[Dict[str, float | str]]) -> Dict:
        total = float(context["total_portfolio_usd"])
        buckets = context["bucket_values"]
        scores = {factor.name: factor.score for factor in context["factors"]}
        if total <= 0:
            return {
                "efficient_frontier": [],
                "sub_optimal_points": [],
                "user_position": {"risk": 0.0, "return": 0.0, "name": "Your Portfolio"},
                "optimization_insight": "Connect accounts and sync holdings to unlock optimization analysis.",
            }

        shares = {bucket: (float(value) / total if total > 0 else 0.0) for bucket, value in buckets.items()}
        risk = (
            4.0
            + shares.get("cash", 0.0) * 1.5
            + shares.get("stocks", 0.0) * 14.0
            + shares.get("bonds", 0.0) * 7.0
            + shares.get("crypto", 0.0) * 26.0
            + shares.get("real_estate", 0.0) * 10.0
            + shares.get("other", 0.0) * 8.0
        )

        momentum = 0.0
        nonzero_months = [float(point["pnl_pct"]) for point in monthly_performance if abs(float(point["pnl_pct"])) > 0]
        if nonzero_months:
            momentum = sum(nonzero_months[-3:]) / min(3, len(nonzero_months))

        expected_return = (
            1.5
            + shares.get("cash", 0.0) * 2.0
            + shares.get("stocks", 0.0) * 7.0
            + shares.get("bonds", 0.0) * 4.0
            + shares.get("crypto", 0.0) * 11.0
            + shares.get("real_estate", 0.0) * 5.0
            + shares.get("other", 0.0) * 4.0
            + (scores.get("Diversification", 50) - 50) * 0.02
            + (scores.get("Risk Balance", 50) - 50) * 0.02
            + momentum * 0.1
        )

        frontier_points = []
        for point_risk in [6, 8, 10, 12, 15, 18, 21, 24, 27, 30]:
            frontier_return = 0.8 + (0.72 * point_risk) - (0.0115 * math.pow(point_risk, 2))
            frontier_points.append({"risk": round(point_risk, 2), "return": round(max(1.0, frontier_return), 2)})

        sub_optimal = [
            {"risk": 11.0, "return": 4.7},
            {"risk": 14.5, "return": 5.8},
            {"risk": 19.5, "return": 7.1},
            {"risk": 24.5, "return": 8.4},
        ]

        user_risk = max(3.0, min(32.0, round(risk, 2)))
        user_return = max(0.5, min(15.0, round(expected_return, 2)))

        nearest = min(frontier_points, key=lambda point: abs(float(point["risk"]) - user_risk))
        gap = round(float(nearest["return"]) - user_return, 2)
        if gap > 0.4:
            insight = (
                f"Your portfolio sits about {gap:.1f}% below the efficient frontier at similar risk. "
                "Rebalancing toward higher-quality diversification could improve return potential."
            )
        else:
            insight = (
                "Your current allocation is near the efficient frontier. "
                "Maintain risk discipline and rebalance periodically to preserve efficiency."
            )

        return {
            "efficient_frontier": frontier_points,
            "sub_optimal_points": sub_optimal,
            "user_position": {"risk": user_risk, "return": user_return, "name": "Your Portfolio"},
            "optimization_insight": insight,
        }

    @staticmethod
    def _upsert_snapshot(
        db: Session,
        user_id: int,
        snapshot_date: date,
        total_value_usd: float,
        bucket_values: Dict[str, float],
        source: str,
    ) -> None:
        row = (
            db.query(PortfolioSnapshot)
            .filter(
                PortfolioSnapshot.user_id == user_id,
                PortfolioSnapshot.snapshot_date == snapshot_date,
            )
            .first()
        )
        payload = json.dumps({k: round(float(v), 2) for k, v in bucket_values.items()})
        if row is None:
            row = PortfolioSnapshot(
                user_id=user_id,
                snapshot_date=snapshot_date,
                total_value_usd=round(float(total_value_usd), 2),
                bucket_values_json=payload,
                source=source,
            )
            db.add(row)
        else:
            row.total_value_usd = round(float(total_value_usd), 2)
            row.bucket_values_json = payload
            row.source = source

    @classmethod
    def _diversification_detail(cls, buckets: Dict[str, float], total: float) -> str:
        if total <= 0:
            return "No allocation data available yet."
        dominant_bucket = max(buckets.items(), key=lambda item: item[1])[0]
        dominant_pct = (buckets[dominant_bucket] / total) * 100
        return f"Largest bucket is {dominant_bucket} at {dominant_pct:.1f}% of portfolio."

    @staticmethod
    def _liquidity_detail(buckets: Dict[str, float], total: float) -> str:
        if total <= 0:
            return "No holdings detected for liquidity analysis."
        liquid_pct = ((buckets["cash"] + buckets["stocks"] + buckets["bonds"] + buckets["crypto"]) / total) * 100
        return f"Approx. {liquid_pct:.1f}% of assets are in liquid or near-liquid instruments."

    @staticmethod
    def _risk_detail(buckets: Dict[str, float], total: float) -> str:
        if total <= 0:
            return "Risk profile unavailable until assets are connected."
        crypto_pct = (buckets["crypto"] / total) * 100
        cash_pct = (buckets["cash"] / total) * 100
        return f"Crypto share {crypto_pct:.1f}% and cash buffer {cash_pct:.1f}% drive current risk balance."

    @staticmethod
    def _freshness_detail(connections: List[AccountConnection]) -> str:
        if not connections:
            return "No linked accounts yet."
        timestamps = [c.last_synced_at for c in connections if c.last_synced_at is not None]
        if not timestamps:
            return "Accounts linked, but no completed sync timestamp recorded."
        newest = max(timestamps)
        return f"Latest completed sync: {newest.isoformat()}"

    @staticmethod
    def _last_sync_iso(connections: List[AccountConnection]) -> str | None:
        timestamps = [c.last_synced_at for c in connections if c.last_synced_at is not None]
        if not timestamps:
            return None
        return max(timestamps).isoformat()
