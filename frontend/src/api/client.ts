const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api'

export interface ApiResult<T> {
  ok: true
  data: T
}

export interface ApiUnavailable {
  ok: false
  unavailable: true
  status?: number
  message: string
}

export type ApiResponse<T> = ApiResult<T> | ApiUnavailable

export function isUnavailable<T>(res: ApiResponse<T>): res is ApiUnavailable {
  return !res.ok && (res as ApiUnavailable).unavailable === true
}

function makeUnavailable(status: number, message: string): ApiUnavailable {
  return { ok: false, unavailable: true, status, message }
}

export async function requestJson<T>(
  path: string,
  options?: RequestInit,
): Promise<ApiResponse<T>> {
  try {
    const url = `${API_BASE}${path}`
    const res = await fetch(url, {
      ...options,
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })

    if (res.status === 404 || res.status === 501) {
      return makeUnavailable(res.status, `后端接口 ${path} 尚未实现（${res.status}）`)
    }

    if (!res.ok) {
      return makeUnavailable(res.status, `请求失败：${res.status} ${res.statusText}`)
    }

    const data = (await res.json()) as T
    return { ok: true, data }
  } catch (err) {
    const message = err instanceof Error ? err.message : '网络错误'
    return makeUnavailable(0, `无法连接后端：${message}`)
  }
}
