import { describe, expect, it, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { nextTick } from 'vue'

import HistoryView from '@/views/HistoryView.vue'
import VersionDiffView from '@/views/VersionDiffView.vue'
import LearningTasksView from '@/views/LearningTasksView.vue'
import AgentTraceView from '@/views/AgentTraceView.vue'
import { useAvailabilityStore } from '@/stores/availability'
import { fetchLearningTasks } from '@/api/learning'
import { fetchReportHistory } from '@/api/reports'

vi.mock('@/api/agentRuns', () => ({
  fetchAgentRun: vi.fn(),
}))

vi.mock('@/api/reports', () => ({
  fetchReport: vi.fn(),
  fetchReportHistory: vi.fn().mockResolvedValue({ ok: true, data: { schemaVersion: '1', items: [] } }),
}))

vi.mock('@/api/resumes', () => ({
  fetchResumes: vi.fn().mockResolvedValue({ ok: true, data: [] }),
  compareResumes: vi.fn(),
}))

vi.mock('@/api/learning', () => ({
  fetchLearningTasks: vi.fn().mockResolvedValue({ ok: true, data: [] }),
  generateLearningTasks: vi.fn(),
  updateLearningTaskStatus: vi.fn(),
}))

describe('周边视图 — BackendNotReadyNotice smoke tests', () => {
  function createRouterInstance() {
    return createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/history', name: 'history', component: HistoryView },
        { path: '/diff', name: 'version-diff', component: VersionDiffView },
        { path: '/learning', name: 'learning', component: LearningTasksView },
        { path: '/trace/:taskId', name: 'agent-trace', component: AgentTraceView, props: true },
      ],
    })
  }

  async function mountAtPath(path: string, component: unknown) {
    const pinia = createPinia()
    setActivePinia(pinia)
    const router = createRouterInstance()
    await router.push(path)
    await router.isReady()
    const wrapper = mount(component, {
      global: { plugins: [pinia, router] },
    })
    return { wrapper, pinia }
  }

  beforeEach(() => {
    vi.resetAllMocks()
    vi.mocked(fetchReportHistory).mockResolvedValue({
      ok: true,
      data: { schemaVersion: '1', items: [] },
    })
    vi.mocked(fetchLearningTasks).mockResolvedValue({ ok: true, data: [] })
  })

  describe('HistoryView', () => {
    it('reports unavailable 时渲染 BackendNotReadyNotice', async () => {
      const { wrapper, pinia } = await mountAtPath('/history', HistoryView)
      const availability = useAvailabilityStore(pinia)
      availability.setCapability('reports', 'unavailable')
      await nextTick()
      await flushPromises()
      const notice = wrapper.findComponent({ name: 'BackendNotReadyNotice' })
      expect(notice.exists()).toBe(true)
      expect(notice.text()).toContain('reports 历史聚合接口')
    })

    it('reports ready 时渲染历史趋势视图', async () => {
      const { wrapper, pinia } = await mountAtPath('/history', HistoryView)
      const availability = useAvailabilityStore(pinia)
      availability.setCapability('reports', 'ready')
      await nextTick()
      await flushPromises()
      expect(wrapper.findComponent({ name: 'BackendNotReadyNotice' }).exists()).toBe(false)
      expect(wrapper.text()).toContain('历史趋势')
    })
  })

  describe('VersionDiffView', () => {
    it('resumes unavailable 时渲染 BackendNotReadyNotice', async () => {
      const { wrapper, pinia } = await mountAtPath('/diff', VersionDiffView)
      const availability = useAvailabilityStore(pinia)
      availability.setCapability('resumes', 'unavailable')
      await nextTick()
      await flushPromises()
      const notice = wrapper.findComponent({ name: 'BackendNotReadyNotice' })
      expect(notice.exists()).toBe(true)
      expect(notice.text()).toContain('简历版本 diff 接口')
    })

    it('resumes ready 时渲染版本对比视图', async () => {
      const { wrapper, pinia } = await mountAtPath('/diff', VersionDiffView)
      const availability = useAvailabilityStore(pinia)
      availability.setCapability('resumes', 'ready')
      await nextTick()
      await flushPromises()
      expect(wrapper.findComponent({ name: 'BackendNotReadyNotice' }).exists()).toBe(false)
      expect(wrapper.text()).toContain('版本对比')
    })
  })

  describe('LearningTasksView', () => {
    it('learning unavailable 时渲染 BackendNotReadyNotice', async () => {
      const { wrapper, pinia } = await mountAtPath('/learning', LearningTasksView)
      const availability = useAvailabilityStore(pinia)
      availability.setCapability('learning', 'unavailable')
      await nextTick()
      await flushPromises()
      const notice = wrapper.findComponent({ name: 'BackendNotReadyNotice' })
      expect(notice.exists()).toBe(true)
      expect(notice.text()).toContain('learning 接口')
    })

    it('learning ready 时渲染生成按钮（disabled）', async () => {
      const { wrapper, pinia } = await mountAtPath('/learning', LearningTasksView)
      const availability = useAvailabilityStore(pinia)
      availability.setCapability('learning', 'ready')
      await nextTick()
      await flushPromises()
      expect(wrapper.findComponent({ name: 'BackendNotReadyNotice' }).exists()).toBe(false)
      expect(wrapper.text()).toContain('按当前缺口生成学习任务')
    })
  })

  describe('AgentTraceView', () => {
    it('agentRuns unavailable 时渲染 BackendNotReadyNotice', async () => {
      const pinia = createPinia()
      setActivePinia(pinia)
      const router = createRouterInstance()
      await router.push('/trace/task-001')
      await router.isReady()
      const availability = useAvailabilityStore(pinia)
      availability.setCapability('agentRuns', 'unavailable')
      const wrapper = mount(AgentTraceView, {
        props: { taskId: 'task-001' },
        global: { plugins: [pinia, router] },
      })
      await nextTick()
      await flushPromises()
      const notice = wrapper.findComponent({ name: 'BackendNotReadyNotice' })
      expect(notice.exists()).toBe(true)
      expect(notice.text()).toContain('agent_runs 接口')
    })

    it('taskId 为空时渲染 ErrorBanner', async () => {
      const pinia = createPinia()
      setActivePinia(pinia)
      const router = createRouterInstance()
      await router.push('/trace/')
      await router.isReady()
      const wrapper = mount(AgentTraceView, {
        props: { taskId: '' },
        global: { plugins: [pinia, router] },
      })
      await flushPromises()
      const banner = wrapper.findComponent({ name: 'ErrorBanner' })
      expect(banner.exists()).toBe(true)
    })
  })
})
