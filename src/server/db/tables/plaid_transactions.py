from datetime import date, datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint

from src.server.db.database import Base


class PlaidTransaction(Base):
    __tablename__ = "plaid_transactions"
    __table_args__ = (
        UniqueConstraint("account_connection_id", "transaction_id", name="uq_plaid_txn_connection_txn"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    account_connection_id = Column(Integer, ForeignKey("account_connections.id"), index=True, nullable=False)
    transaction_id = Column(String, index=True, nullable=False)
    account_id = Column(String, index=True, nullable=True)
    date_posted = Column(Date, index=True, nullable=True)
    amount = Column(Float, nullable=False, default=0.0)
    currency = Column(String, nullable=False, default="USD")
    name = Column(String, nullable=False, default="")
    merchant_name = Column(String, nullable=True)
    category_primary = Column(String, nullable=True)
    pending = Column(Boolean, nullable=False, default=False)
    is_removed = Column(Boolean, nullable=False, default=False)
    raw_payload = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
