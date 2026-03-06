from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from src.server.db.database import Base
from src.server.core.entities.transaction import TransactionType


class Transaction(Base):
    """
    The transaction table 
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), index=True)
    transaction_type = Column(SQLEnum(TransactionType))
    amount = Column(Float)
    category = Column(String)
    description = Column(String, nullable=True)
    transaction_date = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="transactions")
    asset = relationship("Asset", back_populates="transactions")


