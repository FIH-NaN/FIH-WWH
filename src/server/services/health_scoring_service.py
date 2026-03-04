from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from models import Asset, AssetType, Transaction, TransactionType


def _clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))


def _diversification_score(assets: list[Asset]) -> tuple[int, str]:
    if not assets:
        return 0, "No assets recorded yet"

    total_value = sum(float(a.value) for a in assets)
    if total_value <= 0:
        return 0, "Portfolio total value is zero"

    # HHI concentration index: lower concentration means higher diversification.
    hhi = sum((float(a.value) / total_value) ** 2 for a in assets)
    score = int(_clamp((1 - hhi) * 100))
    return score, f"HHI concentration={hhi:.2f}"


def _liquidity_score(assets: list[Asset]) -> tuple[int, str]:
    if not assets:
        return 0, "No assets recorded yet"

    weights = {
        AssetType.CASH: 100,
        AssetType.FUND: 70,
        AssetType.STOCK: 65,
        AssetType.CRYPTO: 50,
        AssetType.OTHER: 45,
        AssetType.PROPERTY: 20,
    }

    total_value = sum(float(a.value) for a in assets)
    if total_value <= 0:
        return 0, "Portfolio total value is zero"

    weighted = sum(float(a.value) * weights.get(a.asset_type, 40) for a in assets)
    score = int(_clamp(weighted / total_value))
    cash_ratio = sum(float(a.value) for a in assets if a.asset_type == AssetType.CASH) / total_value
    return score, f"Cash ratio={cash_ratio:.2%}"


def _resilience_score(db: Session, user_id: int, assets: list[Asset]) -> tuple[int, str]:
    ninety_days_ago = datetime.utcnow() - timedelta(days=90)
    txs = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id, Transaction.transaction_date >= ninety_days_ago)
        .all()
    )

    inflow = sum(float(t.amount) for t in txs if t.transaction_type == TransactionType.INCOME)
    outflow = sum(float(t.amount) for t in txs if t.transaction_type == TransactionType.EXPENSE)
    monthly_outflow = outflow / 3 if outflow > 0 else 0
    cash_value = sum(float(a.value) for a in assets if a.asset_type == AssetType.CASH)

    if inflow <= 0 and outflow <= 0:
        return 50, "No recent cashflow; neutral baseline applied"

    savings_rate = (inflow - outflow) / max(inflow, 1.0)
    savings_score = _clamp((savings_rate + 0.5) * 100)

    buffer_months = cash_value / monthly_outflow if monthly_outflow > 0 else 6
    buffer_score = _clamp((buffer_months / 6) * 100)

    score = int(_clamp(0.4 * savings_score + 0.6 * buffer_score))
    return score, f"Savings rate={savings_rate:.2f}, cash buffer={buffer_months:.1f} months"


def calculate_health_score(db: Session, user_id: int) -> dict:
    """Calculate explainable health score for the current portfolio."""
    assets = db.query(Asset).filter(Asset.user_id == user_id).all()

    diversification, diversification_evidence = _diversification_score(assets)
    liquidity, liquidity_evidence = _liquidity_score(assets)
    resilience, resilience_evidence = _resilience_score(db, user_id, assets)

    overall = int(_clamp(0.4 * diversification + 0.3 * liquidity + 0.3 * resilience))
    grade = "A" if overall >= 80 else "B" if overall >= 65 else "C" if overall >= 50 else "D"

    return {
        "score": overall,
        "grade": grade,
        "methodology": "weighted(diversification 40%, liquidity 30%, resilience 30%)",
        "factors": [
            {
                "name": "Diversification",
                "score": diversification,
                "weight": 0.4,
                "evidence": diversification_evidence,
                "recommendation": "Reduce single-asset concentration if this score is low.",
            },
            {
                "name": "Liquidity",
                "score": liquidity,
                "weight": 0.3,
                "evidence": liquidity_evidence,
                "recommendation": "Increase liquid assets to improve short-term flexibility.",
            },
            {
                "name": "Resilience",
                "score": resilience,
                "weight": 0.3,
                "evidence": resilience_evidence,
                "recommendation": "Build a stronger emergency buffer and stabilize savings rate.",
            },
        ],
    }
