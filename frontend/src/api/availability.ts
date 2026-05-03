import { requestJson } from './client'

export interface Capabilities {
  jobs: boolean
  resumes: boolean
  analysis: boolean
  reports: boolean
  agentRuns: boolean
  learning: boolean
}

export async function fetchBackendCapabilities(): Promise<
  { ok: true; capabilities: Capabilities } | { ok: false; unavailable: true }
> {
  const res = await requestJson<Capabilities>('/capabilities')
  if (!res.ok) {
    return { ok: false, unavailable: true }
  }
  return { ok: true, capabilities: res.data }
}
