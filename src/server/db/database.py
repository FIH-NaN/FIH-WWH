from typing import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from src.server.config import get_settings


settings = get_settings()


engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    """
    from src.server.db.tables import assets, cash_flow, transaction, user, wallet  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _ensure_sync_job_columns()


def _ensure_sync_job_columns() -> None:
    """Best-effort schema patch for legacy databases without sync job metrics columns."""
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    if "sync_jobs" not in table_names:
        return

    existing_columns = {column["name"] for column in inspector.get_columns("sync_jobs")}
    alter_statements = []

    if "sync_mode" not in existing_columns:
        alter_statements.append("ALTER TABLE sync_jobs ADD COLUMN sync_mode VARCHAR DEFAULT 'quick' NOT NULL")
    if "chains_scanned" not in existing_columns:
        alter_statements.append("ALTER TABLE sync_jobs ADD COLUMN chains_scanned INTEGER DEFAULT 0")
    if "tokens_imported" not in existing_columns:
        alter_statements.append("ALTER TABLE sync_jobs ADD COLUMN tokens_imported INTEGER DEFAULT 0")
    if "warnings_json" not in existing_columns:
        alter_statements.append("ALTER TABLE sync_jobs ADD COLUMN warnings_json TEXT")

    if not alter_statements:
        return

    with engine.begin() as conn:
        for statement in alter_statements:
            conn.execute(text(statement))

