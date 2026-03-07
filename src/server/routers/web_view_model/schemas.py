from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import Field


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


class HealthScore(BaseModel):
    score: int
    grade: str
    factors: List[HealthScoreFactor]


# ==================== Response Wrappers ====================
class SuccessResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool
    error: str
    message: Optional[str] = None


# ==================== Accounts Schemas ====================
class AccountConnectRequest(BaseModel):
    type: str
    provider: str
    credentials: Optional[dict] = None


class AccountConnectionResponse(BaseModel):
    id: int
    type: str
    provider: str
    name: str
    network: Optional[str] = None
    wallet_address: Optional[str] = None
    last_synced: Optional[datetime] = None
    status: str


class AccountSyncRequest(BaseModel):
    account_id: Optional[int] = None
    mode: str = "quick"


class AccountSyncTriggerResponse(BaseModel):
    job_id: int
    status: str


class AccountSyncStatusResponse(BaseModel):
    job_id: int
    status: str
    sync_mode: str = "quick"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    new_assets_count: int
    updated_assets_count: int
    chains_scanned: int = 0
    tokens_imported: int = 0
    warnings: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None


class WalletSummaryItem(BaseModel):
    account_id: int
    name: str
    provider: str
    type: str
    wallet_address: Optional[str] = None
    network: Optional[str] = None
    total_value_usd: float
    token_count: int
    active_chain_count: int
    last_synced: Optional[datetime] = None
    status: str
    last_error: Optional[str] = None


class WalletSummaryPayload(BaseModel):
    wallets: List[WalletSummaryItem]
    total_portfolio_usd: float


class WalletHoldingItem(BaseModel):
    external_holding_id: str
    name: str
    symbol: str
    amount: float
    value_usd: float
    price_usd: float
    chain_name: Optional[str] = None
    chain_id: Optional[int] = None
    logo_url: Optional[str] = None


class WalletChainGroup(BaseModel):
    chain_name: str
    chain_id: Optional[int] = None
    subtotal_usd: float
    tokens: List[WalletHoldingItem]


class WalletHoldingsPayload(BaseModel):
    account_id: int
    wallet_address: Optional[str] = None
    total_value_usd: float
    chains: List[WalletChainGroup]
