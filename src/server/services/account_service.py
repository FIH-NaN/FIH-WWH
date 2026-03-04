from datetime import datetime

from sqlalchemy.orm import Session

from models import Asset, AssetType, ConnectedAccount


def create_mock_assets_for_connected_account(
    db: Session,
    user_id: int,
    account_name: str,
    account_type: str,
) -> None:
    """Create deterministic mock assets for connected non-crypto accounts."""
    if account_type not in ["bank", "brokerage"]:
        return

    mock_assets = [
        {
            "name": f"{account_name} - Savings",
            "asset_type": AssetType.CASH,
            "value": 10000,
            "category": "Connected",
        },
        {
            "name": f"{account_name} - Investment",
            "asset_type": AssetType.STOCK,
            "value": 25000,
            "category": "Connected",
        },
    ]

    for item in mock_assets:
        db.add(
            Asset(
                user_id=user_id,
                name=item["name"],
                asset_type=item["asset_type"],
                value=item["value"],
                category=item["category"],
                currency="USD",
            )
        )


def sync_account_and_build_recommendations(
    db: Session,
    account: ConnectedAccount,
) -> dict:
    """Update sync timestamp and return simple next-best-action recommendations."""
    account.last_synced = datetime.utcnow()
    db.commit()

    actions = [
        {
            "priority": "High Impact",
            "title": "Review Concentration Risk",
            "detail": "If one connected account dominates, consider diversifying across asset types.",
        },
        {
            "priority": "Quick Win",
            "title": "Increase Emergency Cash Buffer",
            "detail": "Target 3-6 months of essential expenses in liquid cash assets.",
        },
    ]

    return {
        "message": "Sync completed",
        "synced_at": account.last_synced,
        "next_actions": actions,
    }
