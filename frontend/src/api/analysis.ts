import { requestJson } from './client'

export interface AnalysisTask {
  id: number
  job_id: number
  resume_id: number
  status: 'pending' | 'running' | 'success' | 'completed' | 'failed'
  error_message: string | null
  created_at: string
  updated_at: string
}

export interface CreateAnalysisPayload {
  job_id: number
  resume_id: number
  mode?: 'lite_analysis' | 'full_analysis'
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

export interface NodeProgress {
  node_name: string
  status: string
  duration_ms: number
  execution_meta: Record<string, any>
}

export interface AnalysisProgress {
  task_id: number
  status: string
  completed_nodes: NodeProgress[]
  total_nodes: number
}

export async function fetchAnalysisProgress(taskId: number) {
  return requestJson<AnalysisProgress>(`/analysis/${taskId}/progress`)
}
