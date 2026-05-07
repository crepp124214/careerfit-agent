import { requestJson } from './client'

export interface AgentExecutionMeta {
  agent_role?: string
  execution_mode?: 'llm' | 'rule' | 'rag' | 'deterministic'
  model_name?: string | null
  fallback_used?: boolean
  schema_valid?: boolean
  retry_count?: number
}

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
  execution_meta?: AgentExecutionMeta
}

export interface AgentRun {
  id: string
  taskId: string
  nodes: AgentNode[]
}

interface BackendAgentRun {
  id: number
  task_id: number
  node_name: string
  status: 'running' | 'success' | 'failed'
  input_snapshot?: Record<string, unknown>
  output_snapshot?: Record<string, unknown>
  execution_meta?: AgentExecutionMeta
  started_at?: string
  finished_at?: string
}

function durationMs(startedAt?: string, finishedAt?: string) {
  if (!startedAt || !finishedAt) return 0
  const value = new Date(finishedAt).getTime() - new Date(startedAt).getTime()
  return Number.isFinite(value) && value > 0 ? value : 0
}

function summarizeKeys(value?: Record<string, unknown>) {
  return Object.keys(value ?? {})
}

function normalizeAgentRun(taskId: string, payload: AgentRun | BackendAgentRun[]): AgentRun {
  if (!Array.isArray(payload)) return payload
  return {
    id: `task-${taskId}`,
    taskId,
    nodes: payload.map((node) => {
      const fieldNames = summarizeKeys(node.output_snapshot)
      const meta = node.execution_meta
      let summary = fieldNames.length > 0 ? `输出字段：${fieldNames.join(', ')}` : '节点已完成'
      if (meta) {
        const modeLabel = modeToLabel(meta.execution_mode)
        summary = meta.fallback_used
          ? `${modeLabel}（回退）`
          : modeLabel
        if (fieldNames.length > 0) {
          summary += ` · ${fieldNames.join(', ')}`
        }
      }
      return {
        name: node.node_name,
        status: node.status,
        duration: durationMs(node.started_at, node.finished_at),
        summary,
        length: JSON.stringify(node.output_snapshot ?? {}).length,
        field_names: fieldNames,
        execution_meta: meta,
      }
    }),
  }
}

function modeToLabel(mode?: string) {
  switch (mode) {
    case 'llm':
      return 'LLM'
    case 'rule':
      return '规则'
    case 'rag':
      return 'RAG'
    case 'deterministic':
      return '确定性'
    default:
      return '未知'
  }
}

export async function fetchAgentRun(taskId: string) {
  const res = await requestJson<AgentRun | BackendAgentRun[]>(`/agent-runs/${taskId}`)
  if (!res.ok) return res
  return { ok: true as const, data: normalizeAgentRun(taskId, res.data) }
}
