import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import { useResumeDiffStore } from '@/stores/resumeDiff'
import { compareResumes, type ResumeDiff } from '@/api/resumes'

vi.mock('@/api/resumes', () => ({
  compareResumes: vi.fn(),
}))

const mockDiff: ResumeDiff = {
  schemaVersion: '1',
  fromResume: { id: '1', versionLabel: 'v1', candidateName: 'Alex' },
  toResume: { id: '2', versionLabel: 'v2', candidateName: 'Alex' },
  summary: { addedLines: 2, removedLines: 1, unchangedLines: 5 },
  sections: [
    { type: 'unchanged', text: 'line 1', oldLine: 1, newLine: 1 },
    { type: 'removed', text: 'old line 2', oldLine: 2, newLine: null },
    { type: 'added', text: 'new line 2', oldLine: null, newLine: 2 },
    { type: 'added', text: 'new line 3', oldLine: null, newLine: 3 },
  ],
  scoreContext: {
    available: true,
    fromScore: 65,
    toScore: 75,
    fromReportCreatedAt: '2026-05-03T10:00:00Z',
    toReportCreatedAt: '2026-05-03T11:00:00Z',
  },
}

describe('resumeDiff store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.resetAllMocks()
  })

  it('加载成功后保存 summary 与 sections', async () => {
    vi.mocked(compareResumes).mockResolvedValue({ ok: true, data: mockDiff })
    const store = useResumeDiffStore()
    store.setFromId('1')
    store.setToId('2')

    await store.load()

    expect(store.status).toBe('ready')
    expect(store.summary).toEqual(mockDiff.summary)
    expect(store.sections).toHaveLength(4)
  })

  it('缺少版本时给出中文错误', async () => {
    const store = useResumeDiffStore()

    await store.load()

    expect(store.status).toBe('error')
    expect(store.error).toContain('请选择')
  })

  it('相同版本时给出中文错误', async () => {
    const store = useResumeDiffStore()
    store.setFromId('1')
    store.setToId('1')

    await store.load()

    expect(store.status).toBe('error')
    expect(store.error).toContain('不能选择相同的简历版本')
  })

  it('API 错误时给出中文错误', async () => {
    vi.mocked(compareResumes).mockResolvedValue({
      ok: false,
      unavailable: true,
      message: '后端接口尚未实现',
    })
    const store = useResumeDiffStore()
    store.setFromId('1')
    store.setToId('2')

    await store.load()

    expect(store.status).toBe('error')
    expect(store.error).toContain('后端接口尚未实现')
  })

  it('hasValidSelection 判断是否选择了两个不同版本', async () => {
    const store = useResumeDiffStore()

    expect(store.hasValidSelection).toBe(false)

    store.setFromId('1')
    expect(store.hasValidSelection).toBe(false)

    store.setToId('2')
    expect(store.hasValidSelection).toBe(true)

    store.setToId('1')
    expect(store.hasValidSelection).toBe(false)
  })

  it('不调用 localStorage 保存响应数据', async () => {
    const setItemSpy = vi.spyOn(Storage.prototype, 'setItem')
    vi.mocked(compareResumes).mockResolvedValue({ ok: true, data: mockDiff })
    const store = useResumeDiffStore()
    store.setFromId('1')
    store.setToId('2')

    await store.load()

    expect(setItemSpy).not.toHaveBeenCalled()
    setItemSpy.mockRestore()
  })
})
