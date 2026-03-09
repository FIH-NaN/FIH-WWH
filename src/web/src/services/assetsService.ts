import { apiRequest } from './api'
import type {
  ApiEnvelope,
  Asset,
  AssetCreateInput,
  AssetsListPayload,
  PortfolioAnalysisPayload,
  WealthInsightsHistoryPayload,
  WealthInsightsPayload,
  WealthOverviewPayload,
} from '../types/models'

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

export async function getWealthOverview(token: string) {
  return apiRequest<ApiEnvelope<WealthOverviewPayload>>('/assets/wealth-overview', { token })
}

export async function getWealthInsights(token: string) {
  return apiRequest<ApiEnvelope<WealthInsightsPayload>>('/assets/wealth-overview/insights', { token })
}

export async function refreshWealthInsights(token: string) {
  return apiRequest<ApiEnvelope<WealthInsightsPayload>>('/assets/wealth-overview/insights/refresh', {
    method: 'POST',
    token,
  })
}

export async function getWealthInsightsHistory(token: string, limit = 10) {
  return apiRequest<ApiEnvelope<WealthInsightsHistoryPayload>>(`/assets/wealth-overview/insights/history?limit=${limit}`, { token })
}

export async function getPortfolioAnalysis(token: string) {
  return apiRequest<ApiEnvelope<PortfolioAnalysisPayload>>('/assets/portfolio-analysis', { token })
}
