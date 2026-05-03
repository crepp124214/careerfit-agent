import { requestJson } from './client'

export interface AnalysisTask {
  id: string
  jobId: string
  resumeId: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  createdAt: string
}

export interface CreateAnalysisPayload {
  jobId: string
  resumeId: string
}

export async function createAnalysis(payload: CreateAnalysisPayload) {
  return requestJson<AnalysisTask>('/analyses', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function fetchAnalysis(id: string) {
  return requestJson<AnalysisTask>(`/analyses/${id}`)
}
