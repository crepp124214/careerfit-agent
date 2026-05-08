import { requestJson } from './client'

export type LearningTaskStatus = 'not_started' | 'doing' | 'done' | 'paused' | 'in_progress' | 'completed'

export interface LearningTask {
  schema_version: string
  id: number
  source_task_id: number
  source_report_id: number
  title: string
  dimension?: string | null
  rationale: string
  status: LearningTaskStatus
  evidence_refs: Array<Record<string, unknown>>
  
  // 面试准备计划特有字段（来自后端，snake_case）
  skill?: string | null
  target_question?: string | null
  specific_actions?: string[] | null
  time_investment?: string | null
  expected_outcome?: string | null
  is_interview_prep?: boolean
  
  created_at: string
  updated_at: string
  
  // 前端计算属性（方便模板使用）
  timeInvestment?: string        // alias for time_investment
  expectedOutcome?: string       // alias for expected_outcome
  specificActions?: string[]      // alias for specific_actions
  isInterviewPrep?: boolean      // alias for is_interview_prep
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
