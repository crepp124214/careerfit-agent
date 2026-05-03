import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { mount } from '@vue/test-utils'
import HistoryView from '@/views/HistoryView.vue'
import { useHistoryStore } from '@/stores/history'
import { useAvailabilityStore } from '@/stores/availability'
import type { HistoryItem } from '@/api/reports'

vi.mock('@/stores/history')
vi.mock('@/stores/availability')

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

describe('HistoryView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.resetAllMocks()
  })

  describe('ready 状态', () => {
    it('显示最新分数、分数变化、缺口数量和图表容器', async () => {
      vi.mocked(useHistoryStore).mockReturnValue({
        items: [item2, item1],
        status: 'ready',
        error: '',
        latest: item2,
        scoreDelta: 10,
        hasEnoughData: true,
        load: vi.fn().mockResolvedValue(true),
        clear: vi.fn(),
      } as any)
      vi.mocked(useAvailabilityStore).mockReturnValue({
        states: { reports: 'ready' },
      } as any)

      const wrapper = mount(HistoryView)

      expect(wrapper.find('.history-view__title').text()).toBe('历史趋势')
      expect(wrapper.find('.history-view__latest-score').exists()).toBe(true)
      expect(wrapper.find('.history-view__score-delta').exists()).toBe(true)
      expect(wrapper.find('.history-view__gap-count').exists()).toBe(true)
      expect(wrapper.find('.history-view__chart').exists()).toBe(true)
    })

    it('分数升降同时使用颜色和文字表达', async () => {
      vi.mocked(useHistoryStore).mockReturnValue({
        items: [item2, item1],
        status: 'ready',
        error: '',
        latest: item2,
        scoreDelta: 10,
        hasEnoughData: true,
        load: vi.fn().mockResolvedValue(true),
        clear: vi.fn(),
      } as any)
      vi.mocked(useAvailabilityStore).mockReturnValue({
        states: { reports: 'ready' },
      } as any)

      const wrapper = mount(HistoryView)
      const deltaEl = wrapper.find('.history-view__score-delta')

      expect(deltaEl.text()).toContain('+10')
      expect(deltaEl.classes()).toContain('history-view__score-delta--up')
    })
  })

  describe('状态机', () => {
    it('unavailable 状态显示 BackendNotReadyNotice', async () => {
      vi.mocked(useHistoryStore).mockReturnValue({
        items: [],
        status: 'idle',
        error: '',
        latest: null,
        scoreDelta: null,
        hasEnoughData: false,
        load: vi.fn(),
        clear: vi.fn(),
      } as any)
      vi.mocked(useAvailabilityStore).mockReturnValue({
        states: { reports: 'unavailable' },
      } as any)

      const wrapper = mount(HistoryView)

      expect(wrapper.findComponent({ name: 'BackendNotReadyNotice' }).exists()).toBe(true)
    })

    it('loading 状态显示加载提示', async () => {
      vi.mocked(useHistoryStore).mockReturnValue({
        items: [],
        status: 'loading',
        error: '',
        latest: null,
        scoreDelta: null,
        hasEnoughData: false,
        load: vi.fn(),
        clear: vi.fn(),
      } as any)
      vi.mocked(useAvailabilityStore).mockReturnValue({
        states: { reports: 'ready' },
      } as any)

      const wrapper = mount(HistoryView)

      expect(wrapper.find('.history-view__loading').exists()).toBe(true)
    })

    it('error 状态显示错误提示和重试入口', async () => {
      vi.mocked(useHistoryStore).mockReturnValue({
        items: [],
        status: 'error',
        error: '加载失败',
        latest: null,
        scoreDelta: null,
        hasEnoughData: false,
        load: vi.fn(),
        clear: vi.fn(),
      } as any)
      vi.mocked(useAvailabilityStore).mockReturnValue({
        states: { reports: 'ready' },
      } as any)

      const wrapper = mount(HistoryView)

      expect(wrapper.findComponent({ name: 'ErrorBanner' }).exists()).toBe(true)
    })

    it('empty 状态显示"暂无历史报告"', async () => {
      vi.mocked(useHistoryStore).mockReturnValue({
        items: [],
        status: 'empty',
        error: '',
        latest: null,
        scoreDelta: null,
        hasEnoughData: false,
        load: vi.fn().mockResolvedValue(true),
        clear: vi.fn(),
      } as any)
      vi.mocked(useAvailabilityStore).mockReturnValue({
        states: { reports: 'ready' },
      } as any)

      const wrapper = mount(HistoryView)

      expect(wrapper.text()).toContain('暂无历史报告')
    })

    it('partial 状态显示"数据不足以形成趋势"', async () => {
      vi.mocked(useHistoryStore).mockReturnValue({
        items: [item1],
        status: 'ready',
        error: '',
        latest: item1,
        scoreDelta: null,
        hasEnoughData: false,
        load: vi.fn().mockResolvedValue(true),
        clear: vi.fn(),
      } as any)
      vi.mocked(useAvailabilityStore).mockReturnValue({
        states: { reports: 'ready' },
      } as any)

      const wrapper = mount(HistoryView)

      expect(wrapper.text()).toContain('数据不足以形成趋势')
    })
  })
})
