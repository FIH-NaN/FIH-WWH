"""One-time cleanup utility for low-value EVM external holdings."""

from __future__ import annotations

import argparse

from sqlalchemy.orm import Session

from src.server.db.database import SessionLocal
from src.server.db.tables.assets import Asset
from src.server.db.tables.wallet import AccountConnection, AccountProvider, ExternalHolding
from src.server.services.wallet_sync.constants import MIN_VISIBLE_TOKEN_USD


def cleanup_dust_holdings(db: Session, threshold: float, dry_run: bool) -> tuple[int, int]:
    """Delete low-value EVM holdings and orphaned linked assets.

    Returns:
        tuple[int, int]: (deleted_holdings_count, deleted_assets_count)
    """
    dust_rows = (
        db.query(ExternalHolding)
        .join(AccountConnection, ExternalHolding.account_connection_id == AccountConnection.id)
        .filter(
            AccountConnection.provider == AccountProvider.EVM,
            ExternalHolding.value_usd < threshold,
        )
        .all()
    )

    asset_keys = {
        (int(getattr(item, "user_id")), int(getattr(item, "asset_id")))
        for item in dust_rows
        if getattr(item, "asset_id") is not None
    }
    dust_ids = {int(getattr(item, "id")) for item in dust_rows}

    if dry_run:
        orphan_asset_count = 0
        for user_id, asset_id in asset_keys:
            refs = db.query(ExternalHolding.id).filter(
                ExternalHolding.user_id == user_id,
                ExternalHolding.asset_id == asset_id,
            ).all()
            has_other_refs = any(int(ref_id) not in dust_ids for (ref_id,) in refs)
            if not has_other_refs:
                orphan_asset_count += 1
        return len(dust_rows), orphan_asset_count

    for row in dust_rows:
        db.delete(row)

    db.flush()

    removed_assets = 0
    for user_id, asset_id in asset_keys:
        has_other_refs = (
            db.query(ExternalHolding.id)
            .filter(
                ExternalHolding.user_id == user_id,
                ExternalHolding.asset_id == asset_id,
            )
            .first()
            is not None
        )
        if has_other_refs:
            continue

        deleted = (
            db.query(Asset)
            .filter(
                Asset.user_id == user_id,
                Asset.id == asset_id,
            )
            .delete(synchronize_session=False)
        )
        removed_assets += int(deleted)

    return len(dust_rows), removed_assets


def main() -> None:
    parser = argparse.ArgumentParser(description="Cleanup low-value EVM holdings and orphaned assets")
    parser.add_argument(
        "--threshold",
        type=float,
        default=MIN_VISIBLE_TOKEN_USD,
        help=f"Delete holdings with value_usd below this threshold (default: {MIN_VISIBLE_TOKEN_USD})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be deleted without modifying the database",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        holdings_deleted, assets_deleted = cleanup_dust_holdings(db, threshold=float(args.threshold), dry_run=args.dry_run)
        if args.dry_run:
            print(f"[DRY RUN] dust_holdings={holdings_deleted}, orphan_assets={assets_deleted}, threshold={args.threshold}")
            return

        db.commit()
        print(f"Cleanup complete: deleted_holdings={holdings_deleted}, deleted_assets={assets_deleted}, threshold={args.threshold}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
