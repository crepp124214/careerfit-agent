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
  ctaTo?: string
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

interface BackendScoreItem {
  skill: string
  score: number
  jd_evidence?: string[]
  resume_evidence?: string[]
}

interface BackendSuggestion {
  title?: string
  suggestion?: string
  integrity?: {
    risk_level?: 'high' | 'medium' | 'low'
    risk_codes?: string[]
    explanation?: string
  }
}

interface BackendReport {
  id: number
  task_id: number
  final_score: number
  score_breakdown: Record<string, number>
  gaps?: Array<{ skill: string; reason?: string; jd_evidence?: string[] }>
  resume_suggestions?: BackendSuggestion[]
  next_best_action?: {
    title?: string
    description?: string
  }
  evidence?: BackendScoreItem[]
}

function riskFromScore(score: number): 'high' | 'medium' | 'low' {
  if (score < 50) return 'high'
  if (score < 70) return 'medium'
  return 'low'
}

function normalizeReport(payload: Report | BackendReport): Report {
  if ('totalScore' in payload) return payload

  const evidence = payload.evidence ?? []
  const dimensions: Dimension[] = evidence.map((item) => ({
    name: item.skill,
    score: item.score,
    threshold: 70,
    reason: item.resume_evidence?.length
      ? '简历中存在可验证证据。'
      : '简历缺少对应证据。',
    riskLevel: riskFromScore(item.score),
    evidence: [
      {
        jdExcerpt: item.jd_evidence?.[0] ?? '',
        resumeExcerpt: item.resume_evidence?.[0] ?? '',
        dimensionName: item.skill,
      },
    ],
  }))

  const suggestions: Suggestion[] = (payload.resume_suggestions ?? []).map((item) => ({
    original: item.title ?? '简历建议',
    optimized: item.suggestion ?? '',
    jdRequirement: '',
    resumeEvidence: '',
    riskLevel: item.integrity?.risk_level ?? 'low',
    blocked: (item.integrity?.risk_level ?? 'low') === 'high',
  }))

  const blockedSuggestions = suggestions.filter((item) => item.blocked)

  return {
    id: String(payload.id),
    taskId: String(payload.task_id),
    totalScore: payload.final_score,
    dimensions,
    suggestions,
    nextBestAction: {
      headline: payload.next_best_action?.title ?? '当前没有推荐行动',
      actionLabel: '查看下一步',
      state: payload.next_best_action?.title ? 'ready' : 'empty',
      ctaTo: '/learning',
      waitingReason: payload.next_best_action?.description,
    },
    integrityGuard: {
      blockedCount: blockedSuggestions.length,
      summary:
        blockedSuggestions.length > 0
          ? `拦截了 ${blockedSuggestions.length} 条高风险建议`
          : 'Integrity Guard 未发现高风险建议',
      blockedItems: blockedSuggestions.map((item) => item.optimized),
    },
  }
}

export async function fetchReport(taskId: string) {
  const res = await requestJson<Report | BackendReport>(`/reports/${taskId}`)
  if (!res.ok) return res
  return { ok: true as const, data: normalizeReport(res.data) }
}
