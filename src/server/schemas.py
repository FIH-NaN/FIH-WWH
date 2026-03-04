from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List, Any
from enum import Enum


# Enums
class AssetTypeEnum(str, Enum):
    CASH = "cash"
    STOCK = "stock"
    FUND = "fund"
    CRYPTO = "crypto"
    PROPERTY = "property"
    OTHER = "other"


class TransactionTypeEnum(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


# ==================== User Schemas ====================
class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Auth Schemas ====================
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


# ==================== Asset Schemas ====================
class AssetBase(BaseModel):
    name: str
    asset_type: AssetTypeEnum
    value: float
    currency: Optional[str] = "USD"
    category: Optional[str] = None
    description: Optional[str] = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    value: Optional[float] = None
    description: Optional[str] = None


class AssetResponse(AssetBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Transaction Schemas ====================
class TransactionBase(BaseModel):
    asset_id: int
    transaction_type: TransactionTypeEnum
    amount: float
    category: Optional[str] = None
    description: Optional[str] = None


class TransactionCreate(TransactionBase):
    transaction_date: Optional[datetime] = None


class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    transaction_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionImportItem(BaseModel):
    asset_id: int
    transaction_type: TransactionTypeEnum
    amount: float
    category: Optional[str] = None
    transaction_date: Optional[datetime] = None


class TransactionImportRequest(BaseModel):
    transactions: List[TransactionImportItem]


# ==================== Category Schemas ====================
class CategoryBase(BaseModel):
    name: str
    category_type: str  # "asset" or "transaction"
    icon: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Summary Schemas ====================
class AssetSummary(BaseModel):
    total_value: float
    asset_count: int
    net_worth: float
    currency: str = "USD"


class HealthScoreFactor(BaseModel):
    name: str
    score: int
    weight: Optional[float] = None
    evidence: Optional[str] = None
    recommendation: Optional[str] = None


class HealthScore(BaseModel):
    score: int
    grade: str
    factors: List[HealthScoreFactor]
    methodology: Optional[str] = None


# ==================== Account Schemas ====================
class AccountTypeEnum(str, Enum):
    BANK = "bank"
    BROKERAGE = "brokerage"
    CRYPTO_WALLET = "crypto_wallet"


class ProviderEnum(str, Enum):
    PLAID = "plaid"
    MOCK_BANK = "mock_bank"
    METAMASK = "metamask"
    RAINBOW = "rainbow"
    COINBASE = "coinbase"


class NetworkEnum(str, Enum):
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"


class AccountConnectRequest(BaseModel):
    account_type: AccountTypeEnum
    provider: ProviderEnum
    name: str
    wallet_address: Optional[str] = None
    network: Optional[NetworkEnum] = None


class ConnectedAccountResponse(BaseModel):
    id: int
    user_id: int
    account_type: str
    provider: str
    name: str
    status: str
    wallet_address: Optional[str] = None
    network: Optional[str] = None
    last_synced: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SyncRequest(BaseModel):
    account_id: int


# ==================== Response Wrappers ====================
class SuccessResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool
    error: str
    message: Optional[str] = None
