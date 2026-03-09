from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import Field


# Enums
class AssetTypeEnum(str, Enum):
    DEPOSIT_ACCOUNT = "deposit_account"
    STOCK = "stock"
    ETF = "etf"
    MUTUAL_FUND = "mutual_fund"
    BOND = "bond"
    REAL_ESTATE = "real_estate"
    COMMODITY = "commodity"
    DIGITAL_ASSET = "digital_asset"
    CASH = "cash"
    OTHER = "other"

    # Legacy values kept for backward compatibility with existing clients.
    CRYPTO = "crypto"
    FUND = "fund"
    PROPERTY = "property"


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


class WellnessFactor(BaseModel):
    name: str
    score: int
    weight: float
    detail: str


class AllocationSlice(BaseModel):
    bucket: str
    value_usd: float
    weight_pct: float


class DataQualitySnapshot(BaseModel):
    connected_accounts: int
    holdings_count: int
    manual_assets_count: int
    last_synced_at: Optional[str] = None


class WealthOverviewPayload(BaseModel):
    total_portfolio_usd: float
    overall_score: int
    grade: str
    factors: List[WellnessFactor]
    allocation: List[AllocationSlice]
    recommendations: List[str]
    insight_source: str = "pending"
    insight_provider: str = "minimax"
    insight_error: Optional[str] = None
    data_quality: DataQualitySnapshot


class WealthInsightsPayload(BaseModel):
    recommendations: List[str] = Field(default_factory=list)
    insight_source: str = "cached"
    insight_provider: str = "minimax"
    insight_status: str = "success"
    insight_error: Optional[str] = None
    generated_at: Optional[datetime] = None
    duration_ms: Optional[int] = None


class WealthInsightsHistoryItem(BaseModel):
    id: int
    insight_source: str = "cached"
    insight_provider: str = "minimax"
    insight_status: str = "success"
    recommendations: List[str] = Field(default_factory=list)
    insight_error: Optional[str] = None
    generated_at: Optional[datetime] = None
    duration_ms: Optional[int] = None


class WealthInsightsHistoryPayload(BaseModel):
    items: List[WealthInsightsHistoryItem] = Field(default_factory=list)


class PortfolioCompositionItem(BaseModel):
    bucket: str
    label: str
    value_usd: float
    weight_pct: float
    color: str


class PortfolioPerformancePoint(BaseModel):
    month_key: str
    month: str
    total_value_usd: float
    income_usd: float = 0.0
    expense_usd: float = 0.0
    pnl_usd: float
    pnl_pct: float


class FrontierPoint(BaseModel):
    risk: float
    return_: float = Field(alias="return")

    class Config:
        populate_by_name = True


class PortfolioPosition(BaseModel):
    risk: float
    return_: float = Field(alias="return")
    name: str

    class Config:
        populate_by_name = True


class PortfolioAnalysisPayload(BaseModel):
    total_value_usd: float
    ytd_pnl_usd: float
    avg_monthly_pnl_usd: float
    performance_source: str = "snapshots"
    composition: List[PortfolioCompositionItem]
    performance_12m: List[PortfolioPerformancePoint]
    efficient_frontier: List[FrontierPoint]
    sub_optimal_points: List[FrontierPoint]
    user_position: PortfolioPosition
    optimization_insight: str


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


class PlaidLinkTokenResponse(BaseModel):
    link_token: str
    expiration: Optional[str] = None
    request_id: Optional[str] = None


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
