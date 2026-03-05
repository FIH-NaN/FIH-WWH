import { apiRequest } from './api'
import type { ApiEnvelope, Asset, AssetCreateInput, AssetsListPayload } from '../types/models'

export async function listAssets(token: string) {
  return apiRequest<ApiEnvelope<AssetsListPayload>>('/assets', { token })
}

export async function createAsset(token: string, asset: AssetCreateInput) {
  return apiRequest<ApiEnvelope<Asset>>('/assets', {
    method: 'POST',
    token,
    body: asset,
  })
}
