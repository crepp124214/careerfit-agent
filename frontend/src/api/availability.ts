import { requestJson } from './client'

export interface Capabilities {
  jobs: boolean
  resumes: boolean
  analysis: boolean
  reports: boolean
  agentRuns: boolean
  learning: boolean
  knowledge: boolean
  interview: boolean
}

type CapabilityValue = boolean | 'unknown' | 'pending' | 'ready' | 'unavailable'
type CapabilityMap = Partial<Record<keyof Capabilities, CapabilityValue>>

interface CapabilityEnvelope {
  schema_version?: string
  capabilities?: CapabilityMap
}

function isReady(value: CapabilityValue | undefined): boolean {
  return value === true || value === 'ready'
}

function normalizeCapabilities(payload: CapabilityEnvelope | CapabilityMap): Capabilities {
  const source: CapabilityMap =
    'capabilities' in payload && payload.capabilities ? payload.capabilities : (payload as CapabilityMap)
  return {
    jobs: isReady(source.jobs),
    resumes: isReady(source.resumes),
    analysis: isReady(source.analysis),
    reports: isReady(source.reports),
    agentRuns: isReady(source.agentRuns),
    learning: isReady(source.learning),
    knowledge: isReady(source.knowledge),
    interview: isReady(source.interview),
  }
}

export async function fetchBackendCapabilities(): Promise<
  { ok: true; capabilities: Capabilities } | { ok: false; unavailable: true }
> {
  const res = await requestJson<CapabilityEnvelope | CapabilityMap>('/capabilities')
  if (!res.ok) {
    return { ok: false, unavailable: true }
  }
  return { ok: true, capabilities: normalizeCapabilities(res.data) }
}
