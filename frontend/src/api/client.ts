const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'
const DEFAULT_TIMEOUT = 120000  // 增加到 120 秒，因为分析任务创建可能需要时间
const MAX_RETRIES = 2
const RETRY_DELAY = 1000

export enum ApiErrorCode {
  NETWORK_ERROR = 'NETWORK_ERROR',
  TIMEOUT = 'TIMEOUT',
  NOT_FOUND = 'NOT_FOUND',
  NOT_IMPLEMENTED = 'NOT_IMPLEMENTED',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  SERVER_ERROR = 'SERVER_ERROR',
  UNKNOWN = 'UNKNOWN',
}

export interface ApiResult<T> {
  ok: true
  data: T
}

export interface ApiError {
  ok: false
  unavailable: true
  code: ApiErrorCode
  status?: number
  message: string
  detail?: string
  retryable: boolean
}

export type ApiResponse<T> = ApiResult<T> | ApiError

export function isUnavailable<T>(res: ApiResponse<T>): res is ApiError {
  return !res.ok && (res as ApiError).unavailable === true
}

export function isRetryable<T>(res: ApiResponse<T>): boolean {
  if (res.ok) return false
  return (res as ApiError).retryable ?? false
}

function makeError(
  code: ApiErrorCode,
  message: string,
  options: {
    status?: number
    detail?: string
    retryable?: boolean
  } = {},
): ApiError {
  return {
    ok: false,
    unavailable: true,
    code,
    status: options.status,
    message,
    detail: options.detail,
    retryable: options.retryable ?? false,
  }
}

function classifyError(status: number, path: string): ApiError {
  switch (status) {
    case 404:
      return makeError(ApiErrorCode.NOT_FOUND, `资源不存在或接口未实现`, {
        status: 404,
        detail: `请求路径: ${path}`,
        retryable: false,
      })
    case 501:
      return makeError(ApiErrorCode.NOT_IMPLEMENTED, `后端接口尚未实现`, {
        status: 501,
        detail: `请求路径: ${path}`,
        retryable: false,
      })
    case 401:
      return makeError(ApiErrorCode.UNAUTHORIZED, `未授权，请先登录`, {
        status: 401,
        retryable: false,
      })
    case 403:
      return makeError(ApiErrorCode.FORBIDDEN, `没有权限访问此资源`, {
        status: 403,
        retryable: false,
      })
    case 400:
      return makeError(ApiErrorCode.VALIDATION_ERROR, `请求参数有误`, {
        status: 400,
        retryable: false,
      })
    case 422:
      return makeError(ApiErrorCode.VALIDATION_ERROR, `数据验证失败`, {
        status: 422,
        retryable: false,
      })
    case 500:
    case 502:
    case 503:
    case 504:
      return makeError(ApiErrorCode.SERVER_ERROR, `服务器错误 (${status})`, {
        status,
        detail: `请稍后重试，或联系技术支持`,
        retryable: true,
      })
    default:
      return makeError(ApiErrorCode.UNKNOWN, `请求失败: ${status}`, {
        status,
        retryable: status >= 500,
      })
  }
}

async function fetchWithTimeout(
  url: string,
  options: RequestInit,
  timeout: number,
): Promise<Response> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeout)

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    })
    return response
  } finally {
    clearTimeout(timeoutId)
  }
}

async function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export interface RequestOptions {
  timeout?: number
  retries?: number
  retryDelay?: number
}

export async function requestJson<T>(
  path: string,
  options?: RequestInit,
  requestOptions?: RequestOptions,
): Promise<ApiResponse<T>> {
  const timeout = requestOptions?.timeout ?? DEFAULT_TIMEOUT
  const maxRetries = requestOptions?.retries ?? MAX_RETRIES
  const retryDelay = requestOptions?.retryDelay ?? RETRY_DELAY

  let lastError: ApiError | null = null

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    if (attempt > 0) {
      await delay(retryDelay * attempt)
    }

    try {
      const url = `${API_BASE}${path}`
      const response = await fetchWithTimeout(
        url,
        {
          ...options,
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            ...options?.headers,
          },
        },
        timeout,
      )

      if (!response.ok) {
        lastError = classifyError(response.status, path)
        if (!lastError.retryable || attempt === maxRetries) {
          return lastError
        }
        continue
      }

      const data = (await response.json()) as T
      return { ok: true, data }
    } catch (err) {
      if (err instanceof Error) {
        if (err.name === 'AbortError') {
          lastError = makeError(ApiErrorCode.TIMEOUT, `请求超时 (${timeout}ms)`, {
            retryable: true,
          })
        } else if (err.message.includes('fetch')) {
          lastError = makeError(ApiErrorCode.NETWORK_ERROR, `网络连接失败`, {
            detail: err.message,
            retryable: true,
          })
        } else {
          lastError = makeError(ApiErrorCode.UNKNOWN, err.message, {
            retryable: true,
          })
        }
      } else {
        lastError = makeError(ApiErrorCode.UNKNOWN, '未知错误', {
          retryable: true,
        })
      }

      if (attempt === maxRetries) {
        return lastError
      }
    }
  }

  return lastError ?? makeError(ApiErrorCode.UNKNOWN, '未知错误')
}

export const apiClient = {
  get<T>(path: string, options?: RequestOptions): Promise<ApiResponse<T>> {
    return requestJson<T>(path, { method: 'GET' }, options)
  },

  post<T>(path: string, body: unknown, options?: RequestOptions): Promise<ApiResponse<T>> {
    return requestJson<T>(path, { method: 'POST', body: JSON.stringify(body) }, options)
  },

  put<T>(path: string, body: unknown, options?: RequestOptions): Promise<ApiResponse<T>> {
    return requestJson<T>(path, { method: 'PUT', body: JSON.stringify(body) }, options)
  },

  patch<T>(path: string, body: unknown, options?: RequestOptions): Promise<ApiResponse<T>> {
    return requestJson<T>(path, { method: 'PATCH', body: JSON.stringify(body) }, options)
  },

  delete<T>(path: string, options?: RequestOptions): Promise<ApiResponse<T>> {
    return requestJson<T>(path, { method: 'DELETE' }, options)
  },
}
