import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import { useLearningStore } from '@/stores/learning'
import {
  fetchLearningTasks,
  generateLearningTasks,
  updateLearningTaskStatus,
  type LearningTask,
} from '@/api/learning'
import { ApiErrorCode } from '@/api/client'

vi.mock('@/api/learning', () => ({
  fetchLearningTasks: vi.fn(),
  generateLearningTasks: vi.fn(),
  updateLearningTaskStatus: vi.fn(),
}))

const task: LearningTask = {
  schema_version: '1',
  id: 1,
  source_task_id: 10,
  source_report_id: 20,
  title: '补强 Docker 项目证据',
  dimension: 'Docker',
  rationale: '来自分析报告的学习计划。',
  status: 'not_started',
  evidence_refs: [],
  created_at: '2026-05-03T00:00:00Z',
  updated_at: '2026-05-03T00:00:00Z',
  isInterviewPrep: false,
  timeInvestment: undefined,
  expectedOutcome: undefined,
  specificActions: undefined,
}

describe('learning store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.resetAllMocks()
  })

  it('加载学习任务成功后进入 ready 状态', async () => {
    vi.mocked(fetchLearningTasks).mockResolvedValue({ ok: true, data: [task] })
    const store = useLearningStore()

    await store.loadTasks()

    expect(store.status).toBe('ready')
    expect(store.tasks).toEqual([task])
    expect(store.error).toBeNull()
  })

  it('学习接口不可用时不伪造任务', async () => {
    vi.mocked(fetchLearningTasks).mockResolvedValue({
      ok: false,
      unavailable: true,
      code: ApiErrorCode.NOT_IMPLEMENTED,
      message: '后端接口尚未实现',
      retryable: false,
    })
    const store = useLearningStore()

    await store.loadTasks()

    expect(store.status).toBe('unavailable')
    expect(store.tasks).toEqual([])
    expect(store.error).toContain('后端接口尚未实现')
  })

  it('从分析任务生成学习任务后替换当前列表', async () => {
    vi.mocked(generateLearningTasks).mockResolvedValue({ ok: true, data: [task] })
    const store = useLearningStore()

    await store.generateFromTask(10)

    expect(generateLearningTasks).toHaveBeenCalledWith(10)
    expect(store.status).toBe('ready')
    expect(store.tasks).toEqual([task])
  })

  it('更新任务状态后同步本地列表', async () => {
    const updated: LearningTask = { ...task, status: 'doing' }
    vi.mocked(fetchLearningTasks).mockResolvedValue({ ok: true, data: [task] })
    vi.mocked(updateLearningTaskStatus).mockResolvedValue({ ok: true, data: updated })
    const store = useLearningStore()
    await store.loadTasks()

    await store.updateStatus(1, 'doing')

    expect(updateLearningTaskStatus).toHaveBeenCalledWith(1, 'doing')
    expect(store.tasks[0]).toEqual(updated)
  })
})
