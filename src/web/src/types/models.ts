export type User = {
  id: number
  email: string
  name: string
  created_at: string
}

export type ApiEnvelope<T> = {
  success: boolean
  data: T
  message?: string
}

export type AssetType =
  | 'cash'
  | 'stock'
  | 'bond'
  | 'fund'
  | 'crypto'
  | 'property'
  | 'real_estate'
  | 'digital_asset'
  | 'deposit_account'
  | 'etf'
  | 'mutual_fund'
  | 'commodity'
  | 'other'

export type Asset = {
  id: number
  user_id: number
  name: string
  asset_type: AssetType
  value: number
  currency: string
  category?: string | null
  description?: string | null
  created_at: string
  updated_at: string
}

export type AssetsListPayload = {
  assets: Asset[]
  total: number
  page: number
  limit: number
}

export type WellnessFactor = {
  name: string
  score: number
  weight: number
  detail: string
}

export type AllocationSlice = {
  bucket: string
  value_usd: number
  weight_pct: number
}

export type DataQualitySnapshot = {
  connected_accounts: number
  holdings_count: number
  manual_assets_count: number
  last_synced_at?: string | null
}

export type WealthOverviewPayload = {
  total_portfolio_usd: number
  overall_score: number
  grade: string
  factors: WellnessFactor[]
  allocation: AllocationSlice[]
  recommendations: string[]
  insight_source: 'pending' | 'ai' | 'cached' | 'error'
  insight_provider: string
  insight_status?: string
  insight_error?: string | null
  generated_at?: string | null
  duration_ms?: number | null
  data_quality: DataQualitySnapshot
}

export type WealthInsightsPayload = {
  recommendations: string[]
  insight_source: 'ai' | 'cached' | 'error'
  insight_provider: string
  insight_status: 'success' | 'timeout' | 'error' | 'empty'
  insight_error?: string | null
  generated_at?: string | null
  duration_ms?: number | null
}

export type WealthInsightsHistoryItem = {
  id: number
  insight_source: 'cached' | 'error'
  insight_provider: string
  insight_status: 'success' | 'timeout' | 'error' | 'empty'
  recommendations: string[]
  insight_error?: string | null
  generated_at?: string | null
  duration_ms?: number | null
}

export type WealthInsightsHistoryPayload = {
  items: WealthInsightsHistoryItem[]
}

export type PortfolioCompositionItem = {
  bucket: string
  label: string
  value_usd: number
  weight_pct: number
  color: string
}

export type PortfolioPerformancePoint = {
  month_key: string
  month: string
  total_value_usd: number
  income_usd: number
  expense_usd: number
  pnl_usd: number
  pnl_pct: number
}

export type PortfolioFrontierPoint = {
  risk: number
  return: number
}

export type PortfolioUserPosition = {
  risk: number
  return: number
  name: string
}

export type PortfolioAnalysisPayload = {
  total_value_usd: number
  ytd_pnl_usd: number
  avg_monthly_pnl_usd: number
  performance_source: 'transactions' | 'snapshots'
  composition: PortfolioCompositionItem[]
  performance_12m: PortfolioPerformancePoint[]
  efficient_frontier: PortfolioFrontierPoint[]
  sub_optimal_points: PortfolioFrontierPoint[]
  user_position: PortfolioUserPosition
  optimization_insight: string
}

export type LoginPayload = {
  token: string
  user: User
}

export type RegisterPayload = {
  token: string
  user: User
}

export type AssetCreateInput = {
  name: string
  asset_type: AssetType
  value: number
  currency?: string
  category?: string
  description?: string
}

export type AccountProvider = 'plaid' | 'evm'
export type AccountType = 'bank' | 'brokerage' | 'crypto_wallet'
export type SyncMode = 'quick' | 'deep'

export type AccountConnection = {
  id: number
  type: AccountType
  provider: AccountProvider
  name: string
  network?: string | null
  wallet_address?: string | null
  last_synced?: string | null
  status: string
  last_error?: string | null
}

export type AccountsListPayload = {
  accounts: AccountConnection[]
}

export type ConnectAccountInput = {
  type: AccountType
  provider: AccountProvider
  credentials?: Record<string, unknown>
}

export type PlaidLinkTokenPayload = {
  link_token: string
  expiration?: string | null
  request_id?: string | null
}

export type SyncTriggerPayload = {
  job_id: number
  status: string
}

export type SyncStatusPayload = {
  job_id: number
  status: string
  sync_mode: SyncMode
  started_at?: string | null
  completed_at?: string | null
  new_assets_count: number
  updated_assets_count: number
  chains_scanned: number
  tokens_imported: number
  warnings: string[]
  error_message?: string | null
}

export type WalletSummary = {
  account_id: number
  name: string
  provider: AccountProvider
  type: AccountType
  wallet_address?: string | null
  network?: string | null
  total_value_usd: number
  token_count: number
  active_chain_count: number
  last_synced?: string | null
  status: string
  last_error?: string | null
}

export type WalletsSummaryPayload = {
  wallets: WalletSummary[]
  total_portfolio_usd: number
}

export type WalletHolding = {
  external_holding_id: string
  name: string
  symbol: string
  amount: number
  value_usd: number
  price_usd: number
  chain_name?: string | null
  chain_id?: number | null
  logo_url?: string | null
}

export type WalletChainGroup = {
  chain_name: string
  chain_id?: number | null
  subtotal_usd: number
  tokens: WalletHolding[]
}

export type WalletHoldingsPayload = {
  account_id: number
  wallet_address?: string | null
  total_value_usd: number
  chains: WalletChainGroup[]
}

export type BalanceSheetEntry = {
  category: string
  amount: number
}

export type BalanceSheet = {
  net_worth: number
  assets: BalanceSheetEntry[]
  liabilities: BalanceSheetEntry[]
  totals?: {
    assets: number
    liabilities: number
  }
}

export type IncomeStatementItem = {
  category: string
  actual: number
  budgeted: number
}

export type IncomeStatement = {
  income_items: IncomeStatementItem[]
  expense_items: IncomeStatementItem[]
  remaining_balance: number
}

export type AIAdvice = {
  advice: string
}

export type PortfolioAssetItem = {
  name: string
  value: number
}

export type PortfolioLiabilityItem = {
  name: string
  amount: number
  type?: string
}

export type Portfolio = {
  net_worth: number
  assets: PortfolioAssetItem[]
  liabilities: PortfolioLiabilityItem[]
}

export type InvestmentHolding = {
  name: string
  symbol?: string
  account_name?: string
  value_usd: number
  weight_pct: number
}

export type InvestmentPortfolio = {
  total_value_usd?: number
  holdings: InvestmentHolding[]
}

export type MarketIndicator = {
  symbol: string
  name: string
  value: number
  unit: string
  status?: string
}

export type MarketGroup = {
  group: string
  indicators: MarketIndicator[]
}

export type MarketData = {
  groups: MarketGroup[]
  indicators: MarketIndicator[]
}

export type MonthlyTransaction = {
  id: string
  date: string
  amount: number
  category: string
  description: string
}

export type MonthlyTransactions = {
  transactions: MonthlyTransaction[]
  count: number
  total: number
}

export type TimeSeriesPoint = {
  date: string
  amount: number
}

export type TimeSeries = {
  data: TimeSeriesPoint[]
  average: number
}

export type BudgetItem = {
  id: number
  flow_type: 'income' | 'expense'
  category: string
  amount: number
}

export type BudgetPayload = {
  month_key: string
  items: BudgetItem[]
}

export type AdvisorConversationSummary = {
  id: number
  title: string
  updated_at?: string | null
}

export type AdvisorMessage = {
  id: number
  role: 'user' | 'assistant'
  content: string
  created_at?: string | null
}

export type AdvisorConversation = {
  id: number
  title: string
  messages: AdvisorMessage[]
}
