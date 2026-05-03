import { requestJson } from './client'

export type LearningTaskStatus = 'not_started' | 'doing' | 'done' | 'paused'

export interface LearningTask {
  schema_version: string
  id: number
  source_task_id: number
  source_report_id: number
  title: string
  dimension: string
  rationale: string
  status: LearningTaskStatus
  evidence_refs: Array<Record<string, unknown>>
  created_at: string
  updated_at: string
}

export async function fetchLearningTasks() {
  return requestJson<LearningTask[]>('/learning/tasks')
}

export async function generateLearningTasks(taskId: number | string) {
  return requestJson<LearningTask[]>(`/learning/tasks/generate`, {
    method: 'POST',
    body: JSON.stringify({ task_id: Number(taskId) }),
  })
}

export async function updateLearningTaskStatus(id: number, status: LearningTaskStatus) {
  return requestJson<LearningTask>(`/learning/tasks/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  })
}
