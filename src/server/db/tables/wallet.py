from datetime import datetime
import enum

from sqlalchemy import Column, DateTime, Enum as SQLEnum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.server.db.database import Base


class AccountProvider(str, enum.Enum):
    PLAID = "plaid"
    EVM = "evm"


class AccountType(str, enum.Enum):
    BANK = "bank"
    BROKERAGE = "brokerage"
    CRYPTO_WALLET = "crypto_wallet"


class SyncJobStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"


class AccountConnection(Base):
    __tablename__ = "account_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    provider = Column(SQLEnum(AccountProvider), index=True, nullable=False)
    account_type = Column(SQLEnum(AccountType), nullable=False)
    provider_account_id = Column(String, index=True, nullable=False)
    provider_item_id = Column(String, index=True, nullable=True)
    name = Column(String, nullable=False)
    network = Column(String, nullable=True)
    wallet_address = Column(String, nullable=True)
    status = Column(String, default="active", index=True)
    last_synced_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="account_connections")
    credentials = relationship("AccountCredential", back_populates="connection", cascade="all, delete-orphan")
    sync_jobs = relationship("SyncJob", back_populates="connection", cascade="all, delete-orphan")
    holdings = relationship("ExternalHolding", back_populates="connection", cascade="all, delete-orphan")


class AccountCredential(Base):
    __tablename__ = "account_credentials"

    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(Integer, ForeignKey("account_connections.id"), index=True, nullable=False)
    credential_type = Column(String, nullable=False)
    value = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    connection = relationship("AccountConnection", back_populates="credentials")


class SyncJob(Base):
    __tablename__ = "sync_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    account_connection_id = Column(Integer, ForeignKey("account_connections.id"), index=True, nullable=True)
    status = Column(SQLEnum(SyncJobStatus), default=SyncJobStatus.PENDING, index=True)
    sync_mode = Column(String, default="quick", nullable=False)
    error_message = Column(Text, nullable=True)
    new_assets_count = Column(Integer, default=0)
    updated_assets_count = Column(Integer, default=0)
    chains_scanned = Column(Integer, default=0)
    tokens_imported = Column(Integer, default=0)
    warnings_json = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    connection = relationship("AccountConnection", back_populates="sync_jobs")


class ExternalHolding(Base):
    __tablename__ = "external_holdings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    account_connection_id = Column(Integer, ForeignKey("account_connections.id"), index=True, nullable=False)
    asset_id = Column(Integer, index=True, nullable=True)
    external_holding_id = Column(String, index=True, nullable=False)
    symbol = Column(String, nullable=True)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False, default=0.0)
    price_usd = Column(Float, nullable=False, default=0.0)
    value_usd = Column(Float, nullable=False, default=0.0)
    currency = Column(String, default="USD")
    raw_payload = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    connection = relationship("AccountConnection", back_populates="holdings")
