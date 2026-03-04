import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const login = (email: string, password: string) => api.post('/auth/login', { email, password })
export const register = (email: string, password: string, name: string) =>
  api.post('/auth/register', { email, password, name })
export const getMe = () => api.get('/auth/me')

export const getAssets = () => api.get('/assets')
export const getAssetSummary = () => api.get('/assets/summary')
export const getAssetDistribution = () => api.get('/assets/distribution')
export const getHealthScore = () => api.get('/assets/health-score')
export const createAsset = (data: any) => api.post('/assets', data)
export const deleteAsset = (id: number) => api.delete(`/assets/${id}`)

export const getAccounts = () => api.get('/accounts')
export const connectAccount = (data: any) => api.post('/accounts/connect', data)
export const syncAccount = (accountId: number) => api.post('/accounts/sync', { account_id: accountId })
export const deleteAccount = (id: number) => api.delete(`/accounts?id=${id}`)

export const getTransactions = () => api.get('/transactions')

export default api
