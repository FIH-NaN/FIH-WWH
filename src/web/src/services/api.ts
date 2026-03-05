type RequestOptions = {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  token?: string | null
  body?: unknown
}

const rawBase = import.meta.env.VITE_API_BASE_URL ?? '/api'
const API_BASE = rawBase.endsWith('/') ? rawBase.slice(0, -1) : rawBase

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: options.method ?? 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
  })

  const data = (await response.json().catch(() => ({}))) as { detail?: string; message?: string }

  if (!response.ok) {
    throw new Error(data.detail ?? data.message ?? 'Request failed')
  }

  return data as T
}
