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
