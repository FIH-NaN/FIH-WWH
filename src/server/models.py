from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


# Enums
class AssetType(str, enum.Enum):
    CASH = "cash"
    STOCK = "stock"
    FUND = "fund"
    CRYPTO = "crypto"
    PROPERTY = "property"
    OTHER = "other"


class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class AccountType(str, enum.Enum):
    BANK = "bank"
    BROKERAGE = "brokerage"
    CRYPTO_WALLET = "crypto_wallet"


# Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assets = relationship("Asset", back_populates="owner", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="owner", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="owner", cascade="all, delete-orphan")
    connected_accounts = relationship(
        "ConnectedAccount", back_populates="owner", cascade="all, delete-orphan"
    )


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    name = Column(String, index=True)
    asset_type = Column(SQLEnum(AssetType))
    value = Column(Float)
    currency = Column(String, default="USD")
    category = Column(String)  # User-defined category
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="assets")
    transactions = relationship("Transaction", back_populates="asset", cascade="all, delete-orphan")


class Transaction(Base):
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

    # Relationships
    owner = relationship("User", back_populates="transactions")
    asset = relationship("Asset", back_populates="transactions")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    name = Column(String)
    category_type = Column(String)  # "asset" or "transaction"
    icon = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="categories")


class ConnectedAccount(Base):
    __tablename__ = "connected_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    account_type = Column(String)
    provider = Column(String)
    name = Column(String)
    status = Column(String, default="active")
    wallet_address = Column(String, nullable=True)
    network = Column(String, nullable=True)
    last_synced = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="connected_accounts")
