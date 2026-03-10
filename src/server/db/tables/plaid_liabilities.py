from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint

from src.server.db.database import Base


class PlaidLiability(Base):
    __tablename__ = "plaid_liabilities"
    __table_args__ = (
        UniqueConstraint("account_connection_id", "account_id", name="uq_plaid_liability_connection_account"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    account_connection_id = Column(Integer, ForeignKey("account_connections.id"), index=True, nullable=False)
    account_id = Column(String, index=True, nullable=False)
    liability_type = Column(String, index=True, nullable=False)  # credit|loan
    subtype = Column(String, nullable=True)
    name = Column(String, nullable=False, default="")
    current_balance = Column(Float, nullable=False, default=0.0)
    currency = Column(String, nullable=False, default="USD")
    minimum_payment = Column(Float, nullable=True)
    last_payment_amount = Column(Float, nullable=True)
    interest_rate = Column(Float, nullable=True)
    raw_payload = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
