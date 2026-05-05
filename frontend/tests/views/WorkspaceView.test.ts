import { describe, expect, it, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { nextTick } from 'vue'

import WorkspaceView from '@/views/WorkspaceView.vue'
import { useAvailabilityStore } from '@/stores/availability'
import { useJobsStore } from '@/stores/jobs'
import { useResumesStore } from '@/stores/resumes'
import { useAnalysesStore } from '@/stores/analyses'
import type { Report } from '@/api/reports'

vi.mock('@/api/jobs', () => ({
  fetchJobs: vi.fn(() => Promise.resolve({ ok: true, data: [] })),
}))

vi.mock('@/api/resumes', () => ({
  fetchResumes: vi.fn(() => Promise.resolve({ ok: true, data: [] })),
}))

const MOCK_JOB = { id: 1, title: 'Test Job', raw_text: '', profile: {}, created_at: '' }
const MOCK_RESUME = { id: 1, candidate_name: 'Test', version_label: 'v1', raw_text: '', profile: {}, created_at: '' }

describe('WorkspaceView', () => {
  function createRouterInstance() {
    return createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/', name: 'workspace', component: WorkspaceView }],
    })
  }

  async function mountView() {
    const pinia = createPinia()
    setActivePinia(pinia)
    const router = createRouterInstance()
    await router.push('/')
    await router.isReady()
    const wrapper = mount(WorkspaceView, {
      global: {
        plugins: [pinia, router],
      },
    })
    return { wrapper, pinia, router }
  }

  beforeEach(() => {
    vi.resetAllMocks()
  })

  describe('基础结构', () => {
    it('视图根元素带有 role="main"', async () => {
      const { wrapper } = await mountView()
      const root = wrapper.find('[role="main"]')
      expect(root.exists()).toBe(true)
    })

    it('可见标题为"求职工作台"', async () => {
      const { wrapper } = await mountView()
      expect(wrapper.text()).toContain('求职工作台')
    })

    it('没有岗位或简历时渲染 OnboardingGuide', async () => {
      const { wrapper } = await mountView()
      await flushPromises()
      const guide = wrapper.findComponent({ name: 'OnboardingGuide' })
      expect(guide.exists()).toBe(true)
    })

    it('有岗位和简历时渲染三列工作台布局', async () => {
      const { wrapper } = await mountView()
      const jobs = useJobsStore()
      const resumes = useResumesStore()
      jobs.list = [MOCK_JOB]
      resumes.list = [MOCK_RESUME]
      await nextTick()
      await flushPromises()
      const contextPanel = wrapper.findComponent({ name: 'WorkbenchContextPanel' })
      expect(contextPanel.exists()).toBe(true)
    })

    it('有最新报告时 Next Best Action CTA 指向学习任务', async () => {
      const { wrapper } = await mountView()
      const jobs = useJobsStore()
      const resumes = useResumesStore()
      const analyses = useAnalysesStore()
      jobs.list = [MOCK_JOB]
      resumes.list = [MOCK_RESUME]
      analyses.report = {
        id: 'report-001',
        taskId: 'task-001',
        totalScore: 70,
        dimensions: [],
        suggestions: [],
        interviewQuestions: [],
        learningPlan: [],
        nextBestAction: {
          headline: '优先补齐 Docker 的可验证证据',
          actionLabel: '查看学习任务',
          state: 'ready',
          ctaTo: '/learning',
        },
      } as Report
      await nextTick()
      await flushPromises()

      const callout = wrapper.findComponent({ name: 'NextBestActionCallout' })
      expect(callout.exists()).toBe(true)
      expect(callout.props('headline')).toBe('优先补齐 Docker 的可验证证据')
    })
  })

  describe('后端 unavailable 诚实告知', () => {
    it('岗位选择器显示 BackendNotReadyNotice，文案提到等待后端 jobs API', async () => {
      const { wrapper } = await mountView()
      const jobs = useJobsStore()
      const resumes = useResumesStore()
      jobs.list = [MOCK_JOB]
      resumes.list = [MOCK_RESUME]
      const availability = useAvailabilityStore()
      availability.setCapability('jobs', 'unavailable')
      await nextTick()
      await flushPromises()
      const contextPanel = wrapper.findComponent({ name: 'WorkbenchContextPanel' })
      expect(contextPanel.exists()).toBe(true)
    })

    it('简历选择器显示 BackendNotReadyNotice，文案提到等待后端 resumes API', async () => {
      const { wrapper } = await mountView()
      const jobs = useJobsStore()
      const resumes = useResumesStore()
      jobs.list = [MOCK_JOB]
      resumes.list = [MOCK_RESUME]
      const availability = useAvailabilityStore()
      availability.setCapability('resumes', 'unavailable')
      await nextTick()
      await flushPromises()
      const contextPanel = wrapper.findComponent({ name: 'WorkbenchContextPanel' })
      expect(contextPanel.exists()).toBe(true)
    })
  })

  describe('后端 ready 但列表为空', () => {
    it('岗位选择器渲染 EmptyState 且含"新建岗位"按钮', async () => {
      const { wrapper } = await mountView()
      const jobs = useJobsStore()
      const resumes = useResumesStore()
      jobs.list = []
      resumes.list = [MOCK_RESUME]
      const availability = useAvailabilityStore()
      availability.setCapability('jobs', 'ready')
      await nextTick()
      await flushPromises()
      const guide = wrapper.findComponent({ name: 'OnboardingGuide' })
      expect(guide.exists()).toBe(true)
    })

    it('简历选择器渲染 EmptyState 且含"新建简历"按钮', async () => {
      const { wrapper } = await mountView()
      const jobs = useJobsStore()
      const resumes = useResumesStore()
      jobs.list = [MOCK_JOB]
      resumes.list = []
      const availability = useAvailabilityStore()
      availability.setCapability('resumes', 'ready')
      await nextTick()
      await flushPromises()
      const guide = wrapper.findComponent({ name: 'OnboardingGuide' })
      expect(guide.exists()).toBe(true)
    })
  })
})
