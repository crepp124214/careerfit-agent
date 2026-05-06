export interface BackendNotReadyError {
  message: string
}

function isBackendNotReadyError(err: unknown): boolean {
  return err instanceof Error && err.message === 'backend_not_ready'
}

export interface InterviewQuestion {
  id: number
  skill: string
  category: string
  difficulty: string
  question: string
  answerHint: string | null
  followUps: string[]
  source: string
  status: string
  notes: string | null
  sortOrder: number
}

export interface InterviewSession {
  id: number
  reportId: number
  jobTitle: string
  status: string
  totalQuestions: number
  completedQuestions: number
  createdAt: string
  updatedAt: string | null
}

export interface InterviewSessionDetail extends InterviewSession {
  questions: InterviewQuestion[]
}

export interface InterviewSessionListResponse {
  schemaVersion: string
  items: InterviewSession[]
}

export interface InterviewSessionCreateResponse {
  schemaVersion: string
  session: InterviewSession
}

const API_BASE = `${import.meta.env.VITE_API_BASE_URL || '/api'}/interview`

// Debug: Log the actual API_BASE being used
console.log('[Interview API] VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL)
console.log('[Interview API] Using API_BASE:', API_BASE)

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  console.log('[Interview API] Request URL:', url)
  const resp = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (resp.status === 502 || resp.status === 503) {
    throw new Error('backend_not_ready') as BackendNotReadyError
  }
  if (!resp.ok) {
    const body = await resp.text()
    // 检查是否是 HTML 错误页面
    if (body.trim().startsWith('<')) {
      throw new Error(`backend_http_error:${resp.status}:后端返回 HTML 错误页面，请检查后端是否正常运行`)
    }
    throw new Error(`interview_api_error:${resp.status}:${body}`)
  }
  
  // 检查响应内容类型
  const contentType = resp.headers.get('content-type')
  if (!contentType || !contentType.includes('application/json')) {
    const text = await resp.text()
    throw new Error(`backend_invalid_response:期望 JSON 但收到 ${contentType || '未知类型'}: ${text.substring(0, 100)}`)
  }
  
  return resp.json()
}

function normalizeSession(raw: Record<string, unknown>): InterviewSession {
  return {
    id: raw.id as number,
    reportId: raw.report_id as number,
    jobTitle: raw.job_title as string,
    status: raw.status as string,
    totalQuestions: raw.total_questions as number,
    completedQuestions: raw.completed_questions as number,
    createdAt: raw.created_at as string,
    updatedAt: (raw.updated_at as string) || null,
  }
}

function normalizeQuestion(raw: Record<string, unknown>): InterviewQuestion {
  return {
    id: raw.id as number,
    skill: raw.skill as string,
    category: raw.category as string,
    difficulty: raw.difficulty as string,
    question: raw.question as string,
    answerHint: (raw.answer_hint as string) || null,
    followUps: (raw.follow_ups as string[]) || [],
    source: raw.source as string,
    status: raw.status as string,
    notes: (raw.notes as string) || null,
    sortOrder: raw.sort_order as number,
  }
}

export async function createSession(
  reportId: number,
  includeRag = true,
): Promise<InterviewSessionCreateResponse> {
  const raw = await request<Record<string, unknown>>(`${API_BASE}/sessions`, {
    method: 'POST',
    body: JSON.stringify({ report_id: reportId, include_rag: includeRag }),
  })
  return {
    schemaVersion: raw.schema_version as string,
    session: normalizeSession(raw.session as Record<string, unknown>),
  }
}

export async function listSessions(
  status?: string,
  limit = 20,
  offset = 0,
): Promise<InterviewSessionListResponse> {
  const params = new URLSearchParams()
  if (status) params.set('status', status)
  params.set('limit', String(limit))
  params.set('offset', String(offset))
  const raw = await request<Record<string, unknown>>(`${API_BASE}/sessions?${params}`)
  const items = (raw.items as Record<string, unknown>[]).map(normalizeSession)
  return { schemaVersion: raw.schema_version as string, items }
}

export async function getSession(id: number): Promise<InterviewSessionDetail> {
  const raw = await request<Record<string, unknown>>(`${API_BASE}/sessions/${id}`)
  const questions = ((raw.questions as Record<string, unknown>[]) || []).map(normalizeQuestion)
  return {
    ...normalizeSession(raw),
    questions,
  }
}

export async function updateQuestion(
  sessionId: number,
  questionId: number,
  data: { status?: string; notes?: string },
): Promise<{ id: number; status: string; notes: string | null }> {
  const raw = await request<Record<string, unknown>>(
    `${API_BASE}/sessions/${sessionId}/questions/${questionId}`,
    {
      method: 'PATCH',
      body: JSON.stringify(data),
    },
  )
  return {
    id: raw.id as number,
    status: raw.status as string,
    notes: (raw.notes as string) || null,
  }
}

export function isInterviewNotReady(err: unknown): boolean {
  return isBackendNotReadyError(err) || (err instanceof Error && err.message.includes('interview_api_error'))
}
