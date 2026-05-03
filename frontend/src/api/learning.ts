import { requestJson } from './client'

export interface LearningTask {
  id: string
  goal: string
  dimension: string
  status: 'pending' | 'in_progress' | 'completed'
}

export async function fetchLearningTasks() {
  return requestJson<LearningTask[]>('/learning/tasks')
}

export async function generateLearningTasks(taskId: string) {
  return requestJson<LearningTask[]>(`/learning/tasks/generate`, {
    method: 'POST',
    body: JSON.stringify({ taskId }),
  })
}
