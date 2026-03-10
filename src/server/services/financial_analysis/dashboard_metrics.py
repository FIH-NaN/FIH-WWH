from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
import json
from typing import Dict, List, Tuple

import requests
from sqlalchemy.orm import Session

from src.server.db.tables.budget import BudgetItem
from src.server.db.tables.plaid_liabilities import PlaidLiability
from src.server.db.tables.plaid_transactions import PlaidTransaction
from src.server.db.tables.wallet import AccountConnection, AccountType, ExternalHolding
from src.server.services.financial_analysis.wellness_metrics import WellnessMetricsService


@dataclass
class MonthlyTransactionItem:
    id: str
    date: str
    amount: float
    category: str
    description: str


class DashboardMetricsService:
    _MARKET_CACHE_TTL_SECONDS = 300
    _market_cache_data: Dict | None = None
    _market_cache_at: datetime | None = None

    MARKET_GROUPS = {
        "macro_core": ["SPY", "QQQ", "^TNX", "DX-Y.NYB"],
        "multi_asset": ["BTC-USD", "ETH-USD", "GC=F", "CL=F"],
        "risk_pulse": ["^VIX", "^TNX", "BTC-USD", "GC=F"],
    }

    # Demo-safe fallback values to avoid empty 0.00 panel when provider is rate-limited.
    MARKET_FALLBACK_QUOTES = {
        "SPY": 665.0,
        "QQQ": 605.0,
        "^TNX": 4.25,
        "DX-Y.NYB": 103.5,
        "BTC-USD": 69000.0,
        "ETH-USD": 3600.0,
        "GC=F": 5180.0,
        "CL=F": 88.0,
        "^VIX": 17.5,
    }

    @classmethod
    def build_balance_sheet(cls, db: Session, user_id: int) -> Dict:
        context = WellnessMetricsService._portfolio_context(db=db, user_id=user_id)
        bucket_values = context["bucket_values"]

        cash = float(bucket_values.get("cash", 0.0))
        investments = float(bucket_values.get("stocks", 0.0)) + float(bucket_values.get("bonds", 0.0)) + float(bucket_values.get("crypto", 0.0)) + float(bucket_values.get("other", 0.0))
        real_estate = float(bucket_values.get("real_estate", 0.0))

        liabilities_rows = (
            db.query(PlaidLiability)
            .join(AccountConnection, PlaidLiability.account_connection_id == AccountConnection.id)
            .filter(
                PlaidLiability.user_id == user_id,
                AccountConnection.user_id == user_id,
                AccountConnection.status == "active",
            )
            .all()
        )
        credit_total = 0.0
        loans_total = 0.0
        for row in liabilities_rows:
            amount = float(getattr(row, "current_balance") or 0.0)
            if str(getattr(row, "liability_type") or "").lower() == "credit":
                credit_total += amount
            else:
                loans_total += amount

        total_assets = cash + investments + real_estate
        total_liabilities = credit_total + loans_total
        net_worth = total_assets - total_liabilities

        return {
            "net_worth": round(net_worth, 2),
            "assets": [
                {"category": "Cash", "amount": round(cash, 2)},
                {"category": "Investments", "amount": round(investments, 2)},
                {"category": "Real Estate", "amount": round(real_estate, 2)},
            ],
            "liabilities": [
                {"category": "Credit", "amount": round(credit_total, 2)},
                {"category": "Loans", "amount": round(loans_total, 2)},
            ],
            "totals": {
                "assets": round(total_assets, 2),
                "liabilities": round(total_liabilities, 2),
            },
        }

    @classmethod
    def _classify_flow(cls, txn: PlaidTransaction) -> str:
        # Plaid amount > 0 usually means money leaving account.
        amount = float(getattr(txn, "amount") or 0.0)
        return "expense" if amount > 0 else "income"

    @classmethod
    def _txn_amount_abs(cls, txn: PlaidTransaction) -> float:
        return abs(float(getattr(txn, "amount") or 0.0))

    @classmethod
    def _query_transactions_12m(cls, db: Session, user_id: int) -> List[PlaidTransaction]:
        start_date = date.today() - timedelta(days=370)
        return (
            db.query(PlaidTransaction)
            .join(AccountConnection, PlaidTransaction.account_connection_id == AccountConnection.id)
            .filter(
                PlaidTransaction.user_id == user_id,
                AccountConnection.user_id == user_id,
                AccountConnection.status == "active",
                PlaidTransaction.is_removed == False,  # noqa: E712
                PlaidTransaction.pending == False,  # noqa: E712
                PlaidTransaction.date_posted >= start_date,
            )
            .all()
        )

    @classmethod
    def _this_month_key(cls) -> str:
        return date.today().strftime("%Y-%m")

    @classmethod
    def _transaction_category(cls, txn: PlaidTransaction) -> str:
        primary = str(getattr(txn, "category_primary") or "").strip()
        if primary:
            return primary.replace("_", " ").title()
        return "Uncategorized"

    @classmethod
    def build_totals(cls, db: Session, user_id: int) -> Dict:
        txns = cls._query_transactions_12m(db=db, user_id=user_id)
        income = 0.0
        expense = 0.0
        for txn in txns:
            amount = cls._txn_amount_abs(txn)
            if cls._classify_flow(txn) == "income":
                income += amount
            else:
                expense += amount
        savings_rate = ((income - expense) / income * 100.0) if income > 0 else 0.0
        return {
            "total_income": round(income, 2),
            "total_expense": round(expense, 2),
            "savings_rate": round(savings_rate, 2),
        }

    @classmethod
    def build_income_statement(cls, db: Session, user_id: int) -> Dict:
        txns = cls._query_transactions_12m(db=db, user_id=user_id)
        month_key = cls._this_month_key()

        income_actual: Dict[str, float] = defaultdict(float)
        expense_actual: Dict[str, float] = defaultdict(float)

        for txn in txns:
            posted = getattr(txn, "date_posted")
            if not posted or posted.strftime("%Y-%m") != month_key:
                continue
            cat = cls._transaction_category(txn)
            if cls._classify_flow(txn) == "income":
                income_actual[cat] += cls._txn_amount_abs(txn)
            else:
                expense_actual[cat] += cls._txn_amount_abs(txn)

        budget_rows = db.query(BudgetItem).filter(BudgetItem.user_id == user_id, BudgetItem.month_key == month_key).all()
        income_budget: Dict[str, float] = defaultdict(float)
        expense_budget: Dict[str, float] = defaultdict(float)
        for row in budget_rows:
            if str(getattr(row, "flow_type") or "") == "income":
                income_budget[str(getattr(row, "category") or "Uncategorized")] += float(getattr(row, "amount") or 0.0)
            else:
                expense_budget[str(getattr(row, "category") or "Uncategorized")] += float(getattr(row, "amount") or 0.0)

        income_categories = sorted(set(income_actual.keys()) | set(income_budget.keys()))
        expense_categories = sorted(set(expense_actual.keys()) | set(expense_budget.keys()))

        income_items = [
            {
                "category": cat,
                "actual": round(income_actual.get(cat, 0.0), 2),
                "budgeted": round(income_budget.get(cat, 0.0), 2),
            }
            for cat in income_categories
        ]
        expense_items = [
            {
                "category": cat,
                "actual": round(expense_actual.get(cat, 0.0), 2),
                "budgeted": round(expense_budget.get(cat, 0.0), 2),
            }
            for cat in expense_categories
        ]

        total_income = sum(item["actual"] for item in income_items)
        total_expense = sum(item["actual"] for item in expense_items)

        return {
            "income_items": income_items,
            "expense_items": expense_items,
            "remaining_balance": round(total_income - total_expense, 2),
        }

    @classmethod
    def build_accounting_current_month(cls, db: Session, user_id: int, flow: str) -> Dict:
        month_key = cls._this_month_key()
        txns = cls._query_transactions_12m(db=db, user_id=user_id)
        rows: List[MonthlyTransactionItem] = []

        for txn in txns:
            posted = getattr(txn, "date_posted")
            if not posted or posted.strftime("%Y-%m") != month_key:
                continue
            if cls._classify_flow(txn) != flow:
                continue
            rows.append(
                MonthlyTransactionItem(
                    id=str(getattr(txn, "transaction_id") or getattr(txn, "id")),
                    date=posted.isoformat(),
                    amount=round(cls._txn_amount_abs(txn), 2),
                    category=cls._transaction_category(txn),
                    description=str(getattr(txn, "merchant_name") or getattr(txn, "name") or "Transaction"),
                )
            )

        rows = sorted(rows, key=lambda item: item.date, reverse=True)
        total = round(sum(item.amount for item in rows), 2)
        return {
            "transactions": [item.__dict__ for item in rows],
            "count": len(rows),
            "total": total,
        }

    @classmethod
    def build_accounting_series_12m(cls, db: Session, user_id: int, flow: str) -> Dict:
        txns = cls._query_transactions_12m(db=db, user_id=user_id)
        buckets: Dict[str, float] = defaultdict(float)

        today = date.today().replace(day=1)
        month_keys: List[str] = []
        current = today
        for _ in range(12):
            key = current.strftime("%Y-%m")
            month_keys.append(key)
            if current.month == 1:
                current = current.replace(year=current.year - 1, month=12)
            else:
                current = current.replace(month=current.month - 1)
        month_keys.reverse()

        for txn in txns:
            posted = getattr(txn, "date_posted")
            if not posted:
                continue
            key = posted.strftime("%Y-%m")
            if key not in month_keys:
                continue
            if cls._classify_flow(txn) != flow:
                continue
            buckets[key] += cls._txn_amount_abs(txn)

        data = [{"date": key, "amount": round(float(buckets.get(key, 0.0)), 2)} for key in month_keys]
        average = sum(item["amount"] for item in data) / len(data) if data else 0.0
        return {"data": data, "average": round(average, 2)}

    @classmethod
    def build_portfolio_summary(cls, db: Session, user_id: int) -> Dict:
        balance_sheet = cls.build_balance_sheet(db=db, user_id=user_id)
        context = WellnessMetricsService._portfolio_context(db=db, user_id=user_id)
        liabilities_rows = (
            db.query(PlaidLiability)
            .join(AccountConnection, PlaidLiability.account_connection_id == AccountConnection.id)
            .filter(
                PlaidLiability.user_id == user_id,
                AccountConnection.user_id == user_id,
                AccountConnection.status == "active",
            )
            .all()
        )

        assets = [
            {"name": "Cash", "value": float(context["bucket_values"].get("cash", 0.0))},
            {
                "name": "Investments",
                "value": float(context["bucket_values"].get("stocks", 0.0))
                + float(context["bucket_values"].get("bonds", 0.0))
                + float(context["bucket_values"].get("crypto", 0.0))
                + float(context["bucket_values"].get("other", 0.0)),
            },
            {"name": "Real Estate", "value": float(context["bucket_values"].get("real_estate", 0.0))},
        ]

        liabilities = [
            {
                "name": str(getattr(row, "name") or getattr(row, "subtype") or "Liability"),
                "amount": float(getattr(row, "current_balance") or 0.0),
                "type": str(getattr(row, "liability_type") or "loan"),
            }
            for row in liabilities_rows
        ]

        return {
            "net_worth": balance_sheet["net_worth"],
            "assets": assets,
            "liabilities": liabilities,
        }

    @staticmethod
    def _raw_payload_to_dict(raw_payload: object) -> Dict:
        if isinstance(raw_payload, dict):
            return raw_payload
        if isinstance(raw_payload, str):
            try:
                parsed = json.loads(raw_payload)
                if isinstance(parsed, dict):
                    return parsed
            except (TypeError, ValueError):
                return {}
        return {}

    @classmethod
    def build_investment_holdings_distribution(cls, db: Session, user_id: int, top_n: int = 8) -> Dict:
        rows = (
            db.query(ExternalHolding)
            .join(AccountConnection, ExternalHolding.account_connection_id == AccountConnection.id)
            .filter(
                ExternalHolding.user_id == user_id,
                AccountConnection.user_id == user_id,
                AccountConnection.status == "active",
            )
            .all()
        )

        items: List[Dict] = []
        total_value = 0.0
        for row in rows:
            value_usd = float(getattr(row, "value_usd") or 0.0)
            if value_usd <= 0:
                continue

            payload = cls._raw_payload_to_dict(getattr(row, "raw_payload", None))
            plaid_source = str(payload.get("plaid_source") or "").strip().lower()
            connection = row.connection

            # Keep true investment positions only, not balance snapshots.
            is_investment = plaid_source == "investments_holdings" or (
                connection is not None and connection.account_type == AccountType.BROKERAGE
            )
            if not is_investment:
                continue

            raw_account = payload.get("account")
            account: Dict[str, object] = raw_account if isinstance(raw_account, dict) else {}
            account_name = str(account.get("name") or getattr(connection, "name", None) or "Investment Account")
            symbol = str(getattr(row, "symbol") or "").strip()
            name = str(getattr(row, "name") or symbol or "Investment")

            items.append(
                {
                    "name": name,
                    "symbol": symbol,
                    "account_name": account_name,
                    "value_usd": round(value_usd, 2),
                }
            )
            total_value += value_usd

        items.sort(key=lambda item: float(item.get("value_usd") or 0.0), reverse=True)
        if top_n > 0 and len(items) > top_n:
            head = items[:top_n]
            tail = items[top_n:]
            other_value = round(sum(float(item.get("value_usd") or 0.0) for item in tail), 2)
            if other_value > 0:
                head.append(
                    {
                        "name": "Other Holdings",
                        "symbol": "OTHER",
                        "account_name": "Multiple Accounts",
                        "value_usd": other_value,
                    }
                )
            items = head

        safe_total = total_value if total_value > 0 else 0.0
        holdings = []
        for item in items:
            value_usd = float(item.get("value_usd") or 0.0)
            weight = (value_usd / safe_total * 100.0) if safe_total > 0 else 0.0
            holdings.append(
                {
                    "name": item.get("name"),
                    "symbol": item.get("symbol"),
                    "account_name": item.get("account_name"),
                    "value_usd": round(value_usd, 2),
                    "weight_pct": round(weight, 2),
                }
            )

        return {
            "total_value_usd": round(total_value, 2),
            "holdings": holdings,
        }

    @classmethod
    def _fetch_symbol_quote(cls, symbol: str) -> Tuple[float, str]:
        # Yahoo public chart endpoint for lightweight quote fetch.
        endpoint = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        response = requests.get(
            endpoint,
            params={"interval": "1d", "range": "1d"},
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept": "application/json",
            },
            timeout=8,
        )
        response.raise_for_status()
        payload = response.json()

        result = ((payload.get("chart") or {}).get("result") or [None])[0]
        if not isinstance(result, dict):
            raise ValueError("No quote data")

        meta_obj = result.get("meta")
        meta = meta_obj if isinstance(meta_obj, dict) else {}
        value = meta.get("regularMarketPrice")
        if value is None:
            value = meta.get("previousClose")
        if value is None:
            raise ValueError("Missing market price")

        unit = ""
        if symbol.endswith("=F"):
            unit = " USD"
        if symbol.endswith("-USD"):
            unit = " USD"
        return float(value), unit

    @classmethod
    def build_market_indicators(cls) -> Dict:
        now = datetime.utcnow()
        if cls._market_cache_data is not None and cls._market_cache_at is not None:
            age = (now - cls._market_cache_at).total_seconds()
            if age < cls._MARKET_CACHE_TTL_SECONDS:
                return cls._market_cache_data

        stale_lookup: Dict[str, Dict] = {}
        if cls._market_cache_data:
            for item in cls._market_cache_data.get("indicators", []):
                symbol = str(item.get("symbol") or "")
                if symbol:
                    stale_lookup[symbol] = item

        groups: List[Dict] = []
        for group_name, symbols in cls.MARKET_GROUPS.items():
            indicators: List[Dict] = []
            for symbol in symbols:
                try:
                    value, unit = cls._fetch_symbol_quote(symbol)
                    indicators.append({"symbol": symbol, "name": symbol, "value": value, "unit": unit})
                except Exception:
                    stale_item = stale_lookup.get(symbol)
                    if stale_item is not None:
                        indicators.append(
                            {
                                "symbol": symbol,
                                "name": symbol,
                                "value": float(stale_item.get("value") or 0.0),
                                "unit": str(stale_item.get("unit") or ""),
                                "status": "stale",
                            }
                        )
                        continue

                    fallback = float(cls.MARKET_FALLBACK_QUOTES.get(symbol, 0.0))
                    status_value = "fallback" if fallback > 0 else "unavailable"
                    indicators.append({"symbol": symbol, "name": symbol, "value": fallback, "unit": "", "status": status_value})
            groups.append({"group": group_name, "indicators": indicators})

        flat = [item for group in groups for item in group["indicators"]]
        payload = {"groups": groups, "indicators": flat, "as_of": now.isoformat()}
        cls._market_cache_data = payload
        cls._market_cache_at = now
        return payload
