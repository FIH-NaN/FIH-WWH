from typing import Optional

from sqlalchemy.orm import Session

from src.server.db.tables.wallet import AccountConnection, ExternalHolding, SyncJob


def get_account_by_id(db: Session, user_id: int, account_id: int) -> Optional[AccountConnection]:
    return db.query(AccountConnection).filter(
        AccountConnection.id == account_id,
        AccountConnection.user_id == user_id,
    ).first()


def get_sync_job(db: Session, user_id: int, job_id: int) -> Optional[SyncJob]:
    return db.query(SyncJob).filter(
        SyncJob.id == job_id,
        SyncJob.user_id == user_id,
    ).first()


def get_account_holdings(db: Session, user_id: int, account_id: int) -> list[ExternalHolding]:
    return db.query(ExternalHolding).filter(
        ExternalHolding.user_id == user_id,
        ExternalHolding.account_connection_id == account_id,
    ).all()
