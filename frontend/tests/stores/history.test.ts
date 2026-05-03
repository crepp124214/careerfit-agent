import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import { useHistoryStore } from '@/stores/history'
import { fetchReportHistory, type HistoryItem } from '@/api/reports'

vi.mock('@/api/reports', () => ({
  fetchReportHistory: vi.fn(),
}))

const item1: HistoryItem = {
  taskId: '1',
  reportId: '101',
  jobId: '201',
  jobTitle: 'Backend Engineer',
  resumeId: '301',
  resumeLabel: 'v1',
  finalScore: 65,
  scoreBreakdown: { skill_score: 70, project_score: 60 },
  gapCount: 3,
  highRiskSuggestionCount: 1,
  createdAt: '2026-05-03T10:00:00Z',
}

const item2: HistoryItem = {
  taskId: '2',
  reportId: '102',
  jobId: '201',
  jobTitle: 'Backend Engineer',
  resumeId: '302',
  resumeLabel: 'v2',
  finalScore: 75,
  scoreBreakdown: { skill_score: 80, project_score: 70 },
  gapCount: 2,
  highRiskSuggestionCount: 0,
  createdAt: '2026-05-03T11:00:00Z',
}

describe('history store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.resetAllMocks()
  })

  it('加载成功后进入 ready 状态', async () => {
    vi.mocked(fetchReportHistory).mockResolvedValue({ ok: true, data: { schemaVersion: '1', items: [item1, item2] } })
    const store = useHistoryStore()

    await store.load()

    expect(store.status).toBe('ready')
    expect(store.items).toHaveLength(2)
    expect(store.error).toBe('')
  })

  it('空列表进入 empty 状态', async () => {
    vi.mocked(fetchReportHistory).mockResolvedValue({ ok: true, data: { schemaVersion: '1', items: [] } })
    const store = useHistoryStore()

    await store.load()

    expect(store.status).toBe('empty')
    expect(store.items).toEqual([])
  })

  it('API 错误进入 error 状态', async () => {
    vi.mocked(fetchReportHistory).mockResolvedValue({
      ok: false,
      unavailable: true,
      message: '后端接口尚未实现',
    })
    const store = useHistoryStore()

    await store.load()

    expect(store.status).toBe('error')
    expect(store.error).toContain('后端接口尚未实现')
  })

  it('latest 返回第一条记录', async () => {
    vi.mocked(fetchReportHistory).mockResolvedValue({ ok: true, data: { schemaVersion: '1', items: [item1, item2] } })
    const store = useHistoryStore()

    await store.load()

    expect(store.latest).toEqual(item1)
  })

  it('scoreDelta 计算最新两条分数差', async () => {
    vi.mocked(fetchReportHistory).mockResolvedValue({ ok: true, data: { schemaVersion: '1', items: [item2, item1] } })
    const store = useHistoryStore()

    await store.load()

    expect(store.scoreDelta).toBe(10)
  })

  it('少于两条记录时 scoreDelta 为 null', async () => {
    vi.mocked(fetchReportHistory).mockResolvedValue({ ok: true, data: { schemaVersion: '1', items: [item1] } })
    const store = useHistoryStore()

    await store.load()

    expect(store.scoreDelta).toBeNull()
  })

  it('hasEnoughData 在两条及以上为 true', async () => {
    vi.mocked(fetchReportHistory).mockResolvedValue({ ok: true, data: { schemaVersion: '1', items: [item1, item2] } })
    const store = useHistoryStore()

    await store.load()

    expect(store.hasEnoughData).toBe(true)
  })

  it('不调用 localStorage 保存响应数据', async () => {
    const setItemSpy = vi.spyOn(Storage.prototype, 'setItem')
    vi.mocked(fetchReportHistory).mockResolvedValue({ ok: true, data: { schemaVersion: '1', items: [item1] } })
    const store = useHistoryStore()

    await store.load()

    expect(setItemSpy).not.toHaveBeenCalled()
    setItemSpy.mockRestore()
  })
})
