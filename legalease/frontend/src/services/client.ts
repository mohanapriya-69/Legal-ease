/**
 * Typed API client.
 *
 * The backend returns `{ error: { code, message } }` for every failure, so
 * errors are normalised into an `ApiError` that carries a machine-readable
 * code. Python tracebacks are never shown to the user.
 */

import axios, { type AxiosError, type AxiosInstance, type AxiosRequestConfig } from 'axios'

export const API_BASE_URL: string = (
  import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'
).replace(/\/+$/, '')

export const DEBUG_API = import.meta.env.VITE_DEBUG_API === 'true'

const DEFAULT_TIMEOUT_MS = 180_000

export const ERROR_MESSAGES: Record<string, string> = {
  VALIDATION_ERROR: 'Please correct the highlighted fields and try again.',
  NOT_FOUND: 'We could not find what you were looking for.',
  AI_NOT_CONFIGURED:
    'AI configuration is missing. Add GROQ_API_KEY to backend/.env.',
  AI_TIMEOUT: 'The AI took too long to respond. Please try again.',
  AI_AUTH_FAILED: 'The AI service rejected the configured credentials.',
  AI_QUOTA_EXCEEDED: 'The AI service quota is exhausted. Try again later.',
  AI_INVALID_RESPONSE: 'The AI returned an unreadable response. Please try again.',
  UPLOAD_REJECTED: 'That file could not be accepted.',
  EXPORT_FAILED: 'The document could not be exported. Please try again.',
  INTERNAL_ERROR: 'Something went wrong. Please try again.',
}

export class ApiError extends Error {
  readonly code: string
  readonly status: number
  readonly fields: string[]

  constructor(code: string, message: string, status: number, fields: string[] = []) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
    this.fields = fields
  }

  /** The message safe to show in a toast. */
  get userMessage(): string {
    return this.message || ERROR_MESSAGES[this.code] || 'Something went wrong.'
  }

  get isNetworkError(): boolean {
    return this.code === 'NETWORK_ERROR'
  }

  get isNotConfigured(): boolean {
    return this.code === 'AI_NOT_CONFIGURED'
  }
}

const client: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: DEFAULT_TIMEOUT_MS,
  headers: { Accept: 'application/json' },
})

function extractMessage(payload: unknown, fallbackCode: string): {
  code: string
  message: string
  fields: string[]
} {
  if (payload && typeof payload === 'object' && 'error' in payload) {
    const error = (payload as { error?: unknown }).error
    if (error && typeof error === 'object') {
      const record = error as { code?: unknown; message?: unknown; fields?: unknown }
      const code = typeof record.code === 'string' ? record.code : fallbackCode
      const message =
        typeof record.message === 'string'
          ? record.message
          : (ERROR_MESSAGES[code] ?? 'Something went wrong.')
      const fields = Array.isArray(record.fields)
        ? record.fields.filter((f): f is string => typeof f === 'string')
        : []
      return { code, message, fields }
    }
  }
  return {
    code: fallbackCode,
    message: ERROR_MESSAGES[fallbackCode] ?? 'Something went wrong.',
    fields: [],
  }
}

client.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (axios.isCancel(error) || error.code === 'ERR_CANCELED') {
      return Promise.reject(error)
    }

    if (!error.response) {
      const isTimeout = error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT'
      return Promise.reject(
        new ApiError(
          isTimeout ? 'AI_TIMEOUT' : 'NETWORK_ERROR',
          isTimeout
            ? 'The request timed out. Please try again.'
            : 'Cannot reach the LegalEase API. Is the backend running on port 8000?',
          0,
        ),
      )
    }

    const { code, message, fields } = extractMessage(
      error.response.data,
      error.response.status === 404 ? 'NOT_FOUND' : 'INTERNAL_ERROR',
    )

    if (DEBUG_API) {
      // eslint-disable-next-line no-console
      console.error('[legalease.api]', error.response.status, code, message)
    }

    return Promise.reject(new ApiError(code, message, error.response.status, fields))
  },
)

export const http = {
  get: <T>(url: string, config?: AxiosRequestConfig) =>
    client.get<T>(url, config).then((r) => r.data),
  post: <T>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    client.post<T>(url, data, config).then((r) => r.data),
  put: <T>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    client.put<T>(url, data, config).then((r) => r.data),
  patch: <T>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    client.patch<T>(url, data, config).then((r) => r.data),
  delete: <T>(url: string, config?: AxiosRequestConfig) =>
    client.delete<T>(url, config).then((r) => r.data),
}

/** Absolute URL for a path, used for <img src> and downloads. */
export function assetUrl(path?: string | null): string | undefined {
  if (!path) return undefined
  if (/^https?:\/\//i.test(path)) return path
  return `${API_BASE_URL}${path.startsWith('/') ? '' : '/'}${path}`
}
