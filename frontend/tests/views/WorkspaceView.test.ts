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

    it('可见标题为“个人求职成长工作台”', async () => {
      const { wrapper } = await mountView()
      expect(wrapper.text()).toContain('个人求职成长工作台')
    })

    it('默认渲染 NextBestActionCallout 且 state=empty 时显示“当前没有推荐行动”', async () => {
      const { wrapper } = await mountView()
      await flushPromises()
      const callout = wrapper.findComponent({ name: 'NextBestActionCallout' })
      expect(callout.exists()).toBe(true)
      expect(wrapper.text()).toContain('当前没有推荐行动')
    })

    it('有最新报告时 Next Best Action CTA 指向学习任务', async () => {
      const { wrapper } = await mountView()
      const analyses = useAnalysesStore()
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
        },
      } as Report
      await nextTick()
      await flushPromises()

      expect(wrapper.find('a[href="/learning"]').exists()).toBe(true)
    })
  })

  describe('后端 unavailable 诚实告知', () => {
    it('岗位选择器显示 BackendNotReadyNotice，文案提到等待后端 jobs API', async () => {
      const { wrapper } = await mountView()
      const availability = useAvailabilityStore()
      availability.setCapability('jobs', 'unavailable')
      await nextTick()
      await flushPromises()
      const notices = wrapper.findAllComponents({ name: 'BackendNotReadyNotice' })
      const jobNotice = notices.find((n) =>
        n.text().includes('jobs API'),
      )
      expect(jobNotice?.exists() ?? false).toBe(true)
    })

    it('简历选择器显示 BackendNotReadyNotice，文案提到等待后端 resumes API', async () => {
      const { wrapper } = await mountView()
      const availability = useAvailabilityStore()
      availability.setCapability('resumes', 'unavailable')
      await nextTick()
      await flushPromises()
      const notices = wrapper.findAllComponents({ name: 'BackendNotReadyNotice' })
      const resumeNotice = notices.find((n) =>
        n.text().includes('resumes API'),
      )
      expect(resumeNotice?.exists() ?? false).toBe(true)
    })
  })

  describe('后端 ready 但列表为空', () => {
    it('岗位选择器渲染 EmptyState 且含“新建岗位”按钮', async () => {
      const { wrapper } = await mountView()
      await flushPromises()
      const availability = useAvailabilityStore()
      const jobs = useJobsStore()
      availability.setCapability('jobs', 'ready')
      jobs.list = []
      await nextTick()
      await flushPromises()
      const emptyStates = wrapper.findAll('.empty-state')
      const jobEmpty = emptyStates.find((e) =>
        e.text().includes('新建岗位'),
      )
      expect(jobEmpty?.exists() ?? false).toBe(true)
    })

    it('简历选择器渲染 EmptyState 且含“新建简历”按钮', async () => {
      const { wrapper } = await mountView()
      await flushPromises()
      const availability = useAvailabilityStore()
      const resumes = useResumesStore()
      availability.setCapability('resumes', 'ready')
      resumes.list = []
      await nextTick()
      await flushPromises()
      const emptyStates = wrapper.findAll('.empty-state')
      const resumeEmpty = emptyStates.find((e) =>
        e.text().includes('新建简历'),
      )
      expect(resumeEmpty?.exists() ?? false).toBe(true)
    })
  })
})
