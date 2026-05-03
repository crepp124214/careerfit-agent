import { requestJson } from './client'

export interface AgentNode {
  name: string
  status: 'running' | 'success' | 'failed'
  duration: number
  summary: string
  length: number
  field_names: string[]
  error?: string
  raw_jd?: string
  raw_resume?: string
}

export interface AgentRun {
  id: string
  taskId: string
  nodes: AgentNode[]
}

export async function fetchAgentRun(taskId: string) {
  return requestJson<AgentRun>(`/agent-runs/${taskId}`)
}
