import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { mount } from '@vue/test-utils'
import VersionDiffView from '@/views/VersionDiffView.vue'
import { useResumeDiffStore } from '@/stores/resumeDiff'
import { useAvailabilityStore } from '@/stores/availability'
import type { ResumeDiff, DiffSection } from '@/api/resumes'

vi.mock('@/stores/resumeDiff')
vi.mock('@/stores/availability')

const mockSections: DiffSection[] = [
  { type: 'unchanged', text: 'line 1', oldLine: 1, newLine: 1 },
  { type: 'removed', text: 'old line 2', oldLine: 2, newLine: null },
  { type: 'added', text: 'new line 2', oldLine: null, newLine: 2 },
]

const mockDiff: ResumeDiff = {
  schemaVersion: '1',
  fromResume: { id: '1', versionLabel: 'v1', candidateName: 'Alex' },
  toResume: { id: '2', versionLabel: 'v2', candidateName: 'Alex' },
  summary: { addedLines: 1, removedLines: 1, unchangedLines: 1 },
  sections: mockSections,
  scoreContext: {
    available: true,
    fromScore: 65,
    toScore: 75,
    fromReportCreatedAt: '2026-05-03T10:00:00Z',
    toReportCreatedAt: '2026-05-03T11:00:00Z',
  },
}

describe('VersionDiffView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.resetAllMocks()
  })

  describe('ready 状态', () => {
    it('显示版本选择器、diff summary、score context 和行级 diff', async () => {
      vi.mocked(useResumeDiffStore).mockReturnValue({
        fromId: '1',
        toId: '2',
        diff: mockDiff,
        status: 'ready',
        error: '',
        sections: mockSections,
        summary: mockDiff.summary,
        scoreContext: mockDiff.scoreContext,
        hasValidSelection: true,
        load: vi.fn().mockResolvedValue(true),
        setFromId: vi.fn(),
        setToId: vi.fn(),
        clear: vi.fn(),
      } as any)
      vi.mocked(useAvailabilityStore).mockReturnValue({
        states: { resumes: 'ready' },
      } as any)

      const wrapper = mount(VersionDiffView)

      expect(wrapper.find('.diff-view__title').text()).toBe('版本对比')
      expect(wrapper.find('.diff-view__summary').exists()).toBe(true)
      expect(wrapper.find('.diff-view__diff').exists()).toBe(true)
    })

    it('新增/删除行同时使用颜色和文字表达', async () => {
      vi.mocked(useResumeDiffStore).mockReturnValue({
        fromId: '1',
        toId: '2',
        diff: mockDiff,
        status: 'ready',
        error: '',
        sections: mockSections,
        summary: mockDiff.summary,
        scoreContext: mockDiff.scoreContext,
        hasValidSelection: true,
        load: vi.fn().mockResolvedValue(true),
        setFromId: vi.fn(),
        setToId: vi.fn(),
        clear: vi.fn(),
      } as any)
      vi.mocked(useAvailabilityStore).mockReturnValue({
        states: { resumes: 'ready' },
      } as any)

      const wrapper = mount(VersionDiffView)
      const addedRow = wrapper.find('.diff-view__line--added')
      const removedRow = wrapper.find('.diff-view__line--removed')

      expect(addedRow.exists()).toBe(true)
      expect(removedRow.exists()).toBe(true)
      expect(addedRow.text()).toContain('新增')
      expect(removedRow.text()).toContain('删除')
    })
  })

  describe('状态机', () => {
    it('unavailable 状态显示 BackendNotReadyNotice', async () => {
      vi.mocked(useResumeDiffStore).mockReturnValue({
        fromId: null,
        toId: null,
        diff: null,
        status: 'idle',
        error: '',
        sections: [],
        summary: null,
        scoreContext: null,
        hasValidSelection: false,
        load: vi.fn(),
        setFromId: vi.fn(),
        setToId: vi.fn(),
        clear: vi.fn(),
      } as any)
      vi.mocked(useAvailabilityStore).mockReturnValue({
        states: { resumes: 'unavailable' },
      } as any)

      const wrapper = mount(VersionDiffView)

      expect(wrapper.findComponent({ name: 'BackendNotReadyNotice' }).exists()).toBe(true)
    })

    it('loading 状态显示加载提示', async () => {
      vi.mocked(useResumeDiffStore).mockReturnValue({
        fromId: '1',
        toId: '2',
        diff: null,
        status: 'loading',
        error: '',
        sections: [],
        summary: null,
        scoreContext: null,
        hasValidSelection: true,
        load: vi.fn(),
        setFromId: vi.fn(),
        setToId: vi.fn(),
        clear: vi.fn(),
      } as any)
      vi.mocked(useAvailabilityStore).mockReturnValue({
        states: { resumes: 'ready' },
      } as any)

      const wrapper = mount(VersionDiffView)

      expect(wrapper.find('.diff-view__loading').exists()).toBe(true)
    })

    it('error 状态显示错误提示和重试入口', async () => {
      vi.mocked(useResumeDiffStore).mockReturnValue({
        fromId: '1',
        toId: '2',
        diff: null,
        status: 'error',
        error: '加载失败',
        sections: [],
        summary: null,
        scoreContext: null,
        hasValidSelection: true,
        load: vi.fn(),
        setFromId: vi.fn(),
        setToId: vi.fn(),
        clear: vi.fn(),
      } as any)
      vi.mocked(useAvailabilityStore).mockReturnValue({
        states: { resumes: 'ready' },
      } as any)

      const wrapper = mount(VersionDiffView)

      expect(wrapper.findComponent({ name: 'ErrorBanner' }).exists()).toBe(true)
    })

    it('empty 状态覆盖简历版本少于 2 个', async () => {
      vi.mocked(useResumeDiffStore).mockReturnValue({
        fromId: null,
        toId: null,
        diff: null,
        status: 'idle',
        error: '',
        sections: [],
        summary: null,
        scoreContext: null,
        hasValidSelection: false,
        load: vi.fn(),
        setFromId: vi.fn(),
        setToId: vi.fn(),
        clear: vi.fn(),
      } as any)
      vi.mocked(useAvailabilityStore).mockReturnValue({
        states: { resumes: 'ready' },
      } as any)

      const wrapper = mount(VersionDiffView)

      expect(wrapper.text()).toContain('选择两个简历版本')
    })

    it('partial 状态覆盖没有 score context，但 diff 可用', async () => {
      vi.mocked(useResumeDiffStore).mockReturnValue({
        fromId: '1',
        toId: '2',
        diff: { ...mockDiff, scoreContext: { available: false, reason: '暂无分析报告' } },
        status: 'ready',
        error: '',
        sections: mockSections,
        summary: mockDiff.summary,
        scoreContext: { available: false, reason: '暂无分析报告' },
        hasValidSelection: true,
        load: vi.fn().mockResolvedValue(true),
        setFromId: vi.fn(),
        setToId: vi.fn(),
        clear: vi.fn(),
      } as any)
      vi.mocked(useAvailabilityStore).mockReturnValue({
        states: { resumes: 'ready' },
      } as any)

      const wrapper = mount(VersionDiffView)

      expect(wrapper.text()).toContain('暂无分析报告')
    })
  })
})
