import { requestJson } from './client'

export interface Resume {
  id: number
  candidate_name: string
  version_label: string
  raw_text: string
  profile: Record<string, unknown>
  created_at: string
}

export interface CreateResumePayload {
  candidate_name: string
  version_label: string
  raw_text: string
}

export async function fetchResumes() {
  return requestJson<Resume[]>('/resumes')
}

export async function createResume(payload: CreateResumePayload) {
  return requestJson<Resume>('/resumes', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function fetchResume(id: string) {
  return requestJson<Resume>(`/resumes/${id}`)
}

export interface DiffSection {
  type: 'added' | 'removed' | 'unchanged'
  text: string
  oldLine: number | null
  newLine: number | null
}

export interface DiffSummary {
  addedLines: number
  removedLines: number
  unchangedLines: number
}

export interface DiffResumeRef {
  id: string
  versionLabel: string
  candidateName: string
}

export interface ScoreContext {
  available: boolean
  fromScore?: number
  toScore?: number
  fromReportCreatedAt?: string
  toReportCreatedAt?: string
  reason?: string
}

export interface ResumeDiff {
  schemaVersion: string
  fromResume: DiffResumeRef
  toResume: DiffResumeRef
  summary: DiffSummary
  sections: DiffSection[]
  scoreContext: ScoreContext
}

interface BackendDiffSection {
  type: string
  text: string
  old_line: number | null
  new_line: number | null
}

interface BackendDiffSummary {
  added_lines: number
  removed_lines: number
  unchanged_lines: number
}

interface BackendDiffResumeRef {
  id: number
  version_label: string
  candidate_name: string
}

interface BackendScoreContext {
  available: boolean
  from_score?: number
  to_score?: number
  from_report_created_at?: string
  to_report_created_at?: string
  reason?: string
}

interface BackendResumeDiff {
  schema_version: string
  from_resume: BackendDiffResumeRef
  to_resume: BackendDiffResumeRef
  summary: BackendDiffSummary
  sections: BackendDiffSection[]
  score_context: BackendScoreContext
}

function normalizeDiffSection(section: BackendDiffSection): DiffSection {
  return {
    type: section.type as 'added' | 'removed' | 'unchanged',
    text: section.text,
    oldLine: section.old_line,
    newLine: section.new_line,
  }
}

function normalizeDiffResumeRef(ref: BackendDiffResumeRef): DiffResumeRef {
  return {
    id: String(ref.id),
    versionLabel: ref.version_label,
    candidateName: ref.candidate_name,
  }
}

function normalizeScoreContext(ctx: BackendScoreContext): ScoreContext {
  return {
    available: ctx.available,
    fromScore: ctx.from_score,
    toScore: ctx.to_score,
    fromReportCreatedAt: ctx.from_report_created_at,
    toReportCreatedAt: ctx.to_report_created_at,
    reason: ctx.reason,
  }
}

export async function compareResumes(fromId: string, toId: string) {
  const res = await requestJson<BackendResumeDiff>(
    `/resumes/compare?from_id=${fromId}&to_id=${toId}`,
  )
  if (!res.ok) return res

  return {
    ok: true as const,
    data: {
      schemaVersion: res.data.schema_version,
      fromResume: normalizeDiffResumeRef(res.data.from_resume),
      toResume: normalizeDiffResumeRef(res.data.to_resume),
      summary: {
        addedLines: res.data.summary.added_lines,
        removedLines: res.data.summary.removed_lines,
        unchangedLines: res.data.summary.unchanged_lines,
      },
      sections: res.data.sections.map(normalizeDiffSection),
      scoreContext: normalizeScoreContext(res.data.score_context),
    },
  }
}
