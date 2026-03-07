import { apiRequest } from './api'
import type {
  AccountConnection,
  AccountsListPayload,
  ApiEnvelope,
  ConnectAccountInput,
  SyncMode,
  SyncStatusPayload,
  SyncTriggerPayload,
  WalletHoldingsPayload,
  WalletsSummaryPayload,
} from '../types/models'

export async function listAccounts(token: string) {
  return apiRequest<ApiEnvelope<AccountsListPayload>>('/accounts', { token })
}

export async function connectAccount(token: string, payload: ConnectAccountInput) {
  return apiRequest<ApiEnvelope<{ accounts: AccountConnection[] }>>('/accounts/connect', {
    method: 'POST',
    token,
    body: payload,
  })
}

export async function disconnectAccount(token: string, id: number) {
  return apiRequest<ApiEnvelope<unknown>>(`/accounts?id=${id}`, {
    method: 'DELETE',
    token,
  })
}

export async function triggerSync(token: string, accountId?: number, mode: SyncMode = 'quick') {
  return apiRequest<ApiEnvelope<SyncTriggerPayload>>('/accounts/sync', {
    method: 'POST',
    token,
    body: { account_id: accountId ?? null, mode },
  })
}

export async function getSyncStatus(token: string, jobId: number) {
  return apiRequest<ApiEnvelope<SyncStatusPayload>>(`/accounts/sync/${jobId}`, { token })
}

export async function getWalletsSummary(token: string) {
  return apiRequest<ApiEnvelope<WalletsSummaryPayload>>('/accounts/wallets/summary', { token })
}

export async function getWalletHoldings(token: string, accountId: number) {
  return apiRequest<ApiEnvelope<WalletHoldingsPayload>>(`/accounts/wallets/${accountId}/holdings`, { token })
}
