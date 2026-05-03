import { requestJson } from './client'

export interface Evidence {
  jdExcerpt: string
  resumeExcerpt: string
  dimensionName: string
}

export interface Dimension {
  name: string
  score: number
  threshold: number
  reason: string
  riskLevel: 'high' | 'medium' | 'low'
  evidence: Evidence[]
}

export interface Suggestion {
  original: string
  optimized: string
  jdRequirement: string
  resumeEvidence: string
  riskLevel: 'high' | 'medium' | 'low'
  blocked: boolean
}

export interface NextBestAction {
  headline: string
  actionLabel: string
  state: 'ready' | 'blocked' | 'empty'
  waitingReason?: string
}

export interface IntegrityGuardResult {
  blockedCount: number
  summary: string
  blockedItems: string[]
}

export interface Report {
  id: string
  taskId: string
  totalScore: number
  dimensions: Dimension[]
  suggestions: Suggestion[]
  nextBestAction: NextBestAction
  integrityGuard?: IntegrityGuardResult
}

export async function fetchReport(taskId: string) {
  return requestJson<Report>(`/reports/${taskId}`)
}
