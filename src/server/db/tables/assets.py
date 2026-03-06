from __future__ import annotations

from sqlalchemy import ForeignKey, Enum as SQLEnum, PrimaryKeyConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import Optional

from src.server.db.database import Base
from src.server.core.entities.assets import AssetCategory

from src.server.db.tables.user import User
from src.server.db.tables.transaction import Transaction


class Asset(Base):
    """Asset table with composite primary key (user_id, id) for per-user asset counters."""
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    __table_args__ = (PrimaryKeyConstraint('user_id', 'id'),)
    name: Mapped[str] = mapped_column(index=True)
    asset_type: Mapped[AssetCategory] = mapped_column(SQLEnum(AssetCategory))
    value: Mapped[float] = mapped_column()
    currency: Mapped[str] = mapped_column(default="USD")
    category: Mapped[str] = mapped_column()  # User-defined category
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    owner: Mapped[User] = relationship("User", back_populates="assets")
    transactions: Mapped[list[Transaction]] = relationship("Transaction", back_populates="asset", cascade="all, delete-orphan")
