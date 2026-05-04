import { requestJson } from './client'

export interface AnalysisTask {
  id: number
  job_id: number
  resume_id: number
  status: 'pending' | 'running' | 'completed' | 'failed'
  error_message: string | null
  created_at: string
  updated_at: string
}

export interface CreateAnalysisPayload {
  job_id: number
  resume_id: number
}

export async function createAnalysis(payload: CreateAnalysisPayload) {
  return requestJson<AnalysisTask>('/analysis', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function fetchAnalysis(id: number) {
  return requestJson<AnalysisTask>(`/analysis/${id}`)
}
