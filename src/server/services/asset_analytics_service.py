from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from models import Asset


def calculate_asset_summary(db: Session, user_id: int) -> dict:
    """Calculate portfolio summary and lightweight 7-day trend signal."""
    assets = db.query(Asset).filter(Asset.user_id == user_id).all()
    total_value = float(sum(a.value for a in assets))

    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)
    fourteen_days_ago = now - timedelta(days=14)

    recent_assets = [a for a in assets if a.created_at and a.created_at >= seven_days_ago]
    prior_assets = [
        a
        for a in assets
        if a.created_at and fourteen_days_ago <= a.created_at < seven_days_ago
    ]
    recent_value = float(sum(a.value for a in recent_assets))
    prior_value = float(sum(a.value for a in prior_assets))
    trend_7d_value = recent_value - prior_value

    return {
        "total_value": total_value,
        "asset_count": len(assets),
        "net_worth": total_value,
        "currency": "USD",
        "trend_7d_value": trend_7d_value,
    }


def calculate_asset_distribution(db: Session, user_id: int) -> dict:
    """Calculate distribution by asset type."""
    assets = db.query(Asset).filter(Asset.user_id == user_id).all()
    distribution = {}

    for asset in assets:
        asset_type = asset.asset_type.value
        if asset_type not in distribution:
            distribution[asset_type] = {"count": 0, "value": 0.0}
        distribution[asset_type]["count"] += 1
        distribution[asset_type]["value"] += float(asset.value)

    return distribution
