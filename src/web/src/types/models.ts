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

export type AssetType = 'cash' | 'stock' | 'fund' | 'crypto' | 'property' | 'other'

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
