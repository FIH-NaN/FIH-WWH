type RequestOptions = {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  token?: string | null
  body?: unknown
}

type ApiErrorPayload = {
  detail?: unknown
  message?: unknown
}

function stringifyUnknown(value: unknown): string {
  if (typeof value === 'string') return value
  if (typeof value === 'number' || typeof value === 'boolean') return String(value)
  if (value === null || value === undefined) return ''
  try {
    return JSON.stringify(value)
  } catch {
    return String(value)
  }
}

function parseFastApiDetail(detail: unknown): string {
  if (typeof detail === 'string') return detail

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (item && typeof item === 'object') {
          const record = item as Record<string, unknown>
          const loc = Array.isArray(record.loc) ? record.loc.join('.') : stringifyUnknown(record.loc)
          const msg = stringifyUnknown(record.msg)
          if (loc && msg) return `${loc}: ${msg}`
          return msg || stringifyUnknown(item)
        }
        return stringifyUnknown(item)
      })
      .filter((text) => text.length > 0)

    if (messages.length > 0) {
      return messages.join(' | ')
    }
  }

  if (detail && typeof detail === 'object') {
    const asRecord = detail as Record<string, unknown>
    if (typeof asRecord.message === 'string') {
      return asRecord.message
    }
  }

  return stringifyUnknown(detail)
}

function extractApiErrorMessage(payload: ApiErrorPayload): string {
  const detailMessage = parseFastApiDetail(payload.detail)
  if (detailMessage) return detailMessage

  const fallbackMessage = stringifyUnknown(payload.message)
  if (fallbackMessage) return fallbackMessage

  return 'Request failed'
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

  const data = (await response.json().catch(() => ({}))) as ApiErrorPayload

  if (!response.ok) {
    throw new Error(extractApiErrorMessage(data))
  }

  return data as T
}
