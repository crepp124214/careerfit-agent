import { describe, expect, it, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { nextTick } from 'vue'

import ReportView from '@/views/ReportView.vue'
import { useAvailabilityStore } from '@/stores/availability'
import { ApiErrorCode } from '@/api/client'

vi.mock('@/api/reports', () => ({
  fetchReport: vi.fn(),
}))

vi.mock('@/api/agentRuns', () => ({
  fetchAgentRun: vi.fn(),
}))

vi.mock('@/components/report/SkillsRadarChart.vue', () => ({
  default: {
    name: 'SkillsRadarChart',
    template: '<div class="skills-radar-mock" />',
    props: ['dimensions'],
  },
}))

import type { Report } from '@/api/reports'
import type { AgentRun } from '@/api/agentRuns'
import { fetchReport } from '@/api/reports'
import { fetchAgentRun } from '@/api/agentRuns'

const mockFetchReport = vi.mocked(fetchReport)
const mockFetchAgentRun = vi.mocked(fetchAgentRun)

function makeReport(overrides: Partial<Report> = {}): Report {
  return {
    id: 'report-001',
    taskId: 'task-001',
    totalScore: 72,
    interviewQuestions: [],
    learningPlan: [],
    dimensions: [
      {
        name: '技术匹配',
        score: 85,
        threshold: 70,
        reason: '核心技能匹配度高',
        riskLevel: 'low',
        evidence: [
          {
            jdExcerpt: '熟悉 Python 和 FastAPI',
            resumeExcerpt: '使用 Python 开发后端服务',
            dimensionName: '技术匹配',
          },
        ],
      },
      {
        name: '项目经验',
        score: 60,
        threshold: 65,
        reason: '项目规模偏小',
        riskLevel: 'medium',
        evidence: [],
      },
    ],
    suggestions: [
      {
        original: '负责后端开发',
        optimized: '主导后端微服务架构设计与实现',
        jdRequirement: '需要架构设计经验',
        resumeEvidence: '有后端开发经验',
        riskLevel: 'low',
        blocked: false,
      },
      {
        original: '参与系统优化',
        optimized: '独立完成系统性能优化，QPS 提升 300%',
        jdRequirement: '性能优化经验',
        resumeEvidence: '有优化经验但数据不足',
        riskLevel: 'high',
        blocked: true,
      },
    ],
    nextBestAction: {
      headline: '更新简历以突出架构设计经验',
      actionLabel: '生成新简历版本',
      state: 'ready',
    },
    integrityGuard: {
      blockedCount: 1,
      summary: '拦截了 1 条夸大表述',
      blockedItems: ['QPS 提升 300%'],
    },
    ...overrides,
  }
}

function makeAgentRun(): AgentRun {
  return {
    id: 'run-001',
    taskId: 'task-001',
    nodes: [
      {
        name: '需求解析',
        status: 'success' as const,
        duration: 1200,
        summary: '已提取 JD 中 8 项核心要求',
        length: 2400,
        field_names: ['title', 'requirements'],
      },
      {
        name: 'Integrity Guard',
        status: 'failed' as const,
        duration: 50,
        summary: '拦截了 1 条夸大表述',
        length: 300,
        field_names: ['blocked_items'],
      },
    ],
  }
}

describe('ReportView', () => {
  function createRouterInstance() {
    return createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/reports/:taskId',
          name: 'report',
          component: ReportView,
          props: true,
        },
      ],
    })
  }

  async function mountView(taskId = 'task-001') {
    const pinia = createPinia()
    setActivePinia(pinia)
    const router = createRouterInstance()
    await router.push(`/reports/${taskId}`)
    await router.isReady()
    const wrapper = mount(ReportView, {
      global: { plugins: [pinia, router] },
    })
    return { wrapper, pinia, router }
  }

  beforeEach(() => {
    vi.resetAllMocks()
    mockFetchReport.mockResolvedValue({
      ok: false,
      unavailable: true,
      code: ApiErrorCode.NOT_IMPLEMENTED,
      message: 'mock not set',
      retryable: false,
    })
    mockFetchAgentRun.mockResolvedValue({
      ok: false,
      unavailable: true,
      code: ApiErrorCode.NOT_IMPLEMENTED,
      message: 'mock not set',
      retryable: false,
    })
  })

  describe('错误状态', () => {
    it('taskId 非法（空字符串）时渲染 ErrorBanner', async () => {
      const { wrapper } = await mountView('')
      await flushPromises()
      const banner = wrapper.findComponent({ name: 'ErrorBanner' })
      expect(banner.exists()).toBe(true)
    })

    it('后端 reports API unavailable 时显示 BackendNotReadyNotice', async () => {
      const { wrapper } = await mountView('task-001')
      const availability = useAvailabilityStore()
      availability.setCapability('reports', 'unavailable')
      await nextTick()
      await flushPromises()
      const notice = wrapper.findComponent({ name: 'BackendNotReadyNotice' })
      expect(notice.exists()).toBe(true)
      expect(notice.text()).toContain('analysis pipeline')
    })
  })

  describe('加载状态', () => {
    it('后端 ready 但 API 返回 unavailable 时显示 LoadingCard', async () => {
      mockFetchReport.mockImplementation(
        () => new Promise(() => {}),
      )
      mockFetchAgentRun.mockImplementation(
        () => new Promise(() => {}),
      )
      const { wrapper } = await mountView('task-001')
      const availability = useAvailabilityStore()
      availability.setCapability('reports', 'ready')
      availability.setCapability('analysis', 'ready')
      await nextTick()
      await flushPromises()
      const loading = wrapper.findComponent({ name: 'LoadingCard' })
      expect(loading.exists()).toBe(true)
    })
  })

  describe('报告结构', () => {
    async function mountWithData() {
      mockFetchReport.mockResolvedValue({
        ok: true,
        data: makeReport(),
      })
      mockFetchAgentRun.mockResolvedValue({
        ok: true,
        data: makeAgentRun(),
      })
      const result = await mountView('task-001')
      const availability = useAvailabilityStore()
      availability.setCapability('reports', 'ready')
      availability.setCapability('analysis', 'ready')
      await nextTick()
      await flushPromises()
      return result
    }

    it('数据就绪时渲染 NextBestActionCallout', async () => {
      const { wrapper } = await mountWithData()
      const callout = wrapper.findComponent({ name: 'NextBestActionCallout' })
      expect(callout.exists()).toBe(true)
    })

    it('报告头部 Next Best Action CTA 指向学习任务', async () => {
      const { wrapper } = await mountWithData()
      expect(wrapper.find('a[href="/interview?tab=learning"]').exists()).toBe(true)
    })

    it('数据就绪时渲染 ScoringOverviewCard', async () => {
      const { wrapper } = await mountWithData()
      const overview = wrapper.findComponent({ name: 'ScoringOverviewCard' })
      expect(overview.exists()).toBe(true)
    })

    it('数据就绪时渲染 AgentTraceTimeline（切换到 Trace Tab）', async () => {
      const { wrapper } = await mountWithData()
      const traceToggle = wrapper.find('.report-view__trace-toggle')
      expect(traceToggle.exists()).toBe(true)
      await traceToggle.trigger('click')
      await nextTick()
      const timeline = wrapper.findComponent({ name: 'AgentTraceTimeline' })
      expect(timeline.exists()).toBe(true)
    })
  })

  describe('Integrity Guard', () => {
    async function mountWithIntegrityGuard() {
      mockFetchReport.mockResolvedValue({
        ok: true,
        data: makeReport(),
      })
      mockFetchAgentRun.mockResolvedValue({
        ok: true,
        data: makeAgentRun(),
      })
      const result = await mountView('task-001')
      const availability = useAvailabilityStore()
      availability.setCapability('reports', 'ready')
      availability.setCapability('analysis', 'ready')
      await nextTick()
      await flushPromises()
      return result
    }

    it('有拦截时渲染 ResumeSuggestionReview 组件（切换到建议 Tab）', async () => {
      const { wrapper } = await mountWithIntegrityGuard()
      const suggestionsTab = wrapper.find('button[id="tab-resume"]')
      expect(suggestionsTab.exists()).toBe(true)
      await suggestionsTab.trigger('click')
      await nextTick()
      const review = wrapper.findComponent({ name: 'ResumeSuggestionReview' })
      expect(review.exists()).toBe(true)
    })

    it('被拦截卡片带有 RiskPill level=high', async () => {
      const { wrapper } = await mountWithIntegrityGuard()
      const suggestionsTab = wrapper.find('button[id="tab-resume"]')
      expect(suggestionsTab.exists()).toBe(true)
      await suggestionsTab.trigger('click')
      await nextTick()
      const highPills = wrapper.findAllComponents({ name: 'RiskPill' }).filter(
        (c) => c.props('level') === 'high',
      )
      expect(highPills.length).toBeGreaterThan(0)
    })
  })
})
