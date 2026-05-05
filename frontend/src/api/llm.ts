import { requestJson } from './client'

export interface LLMStatus {
  enabled: boolean
  configured: boolean
  connected: boolean
  model_name: string | null
  error: string | null
  response_time_ms: number | null
}

export async function fetchLLMStatus(): Promise<
  { ok: true; status: LLMStatus } | { ok: false; error: string }
> {
  const res = await requestJson<LLMStatus>('/llm/status')
  if (!res.ok) {
    return { ok: false, error: res.message }
  }
  return { ok: true, status: res.data }
}
