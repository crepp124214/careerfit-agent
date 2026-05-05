import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import { nextTick } from 'vue'

import LearningTasksView from '@/views/LearningTasksView.vue'
import { useAvailabilityStore } from '@/stores/availability'
import { useLearningStore } from '@/stores/learning'
import {
  fetchLearningTasks,
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
  evidence_refs: [{ skill: 'Docker', score: 0 }],
  created_at: '2026-05-03T00:00:00Z',
  updated_at: '2026-05-03T00:00:00Z',
}

async function mountView() {
  const pinia = createPinia()
  setActivePinia(pinia)
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/learning', name: 'learning', component: LearningTasksView }],
  })
  await router.push('/learning')
  await router.isReady()
  const wrapper = mount(LearningTasksView, {
    global: { plugins: [pinia, router] },
  })
  return { wrapper, pinia }
}

describe('LearningTasksView', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('learning ready 时渲染真实学习任务列表', async () => {
    vi.mocked(fetchLearningTasks).mockResolvedValue({ ok: true, data: [task] })
    const { wrapper, pinia } = await mountView()
    useAvailabilityStore(pinia).setCapability('learning', 'ready')

    await nextTick()
    await flushPromises()

    expect(wrapper.text()).toContain('补强 Docker 项目证据')
    expect(wrapper.text()).toContain('Docker')
    expect(wrapper.text()).toContain('未开始')
    expect(wrapper.text()).toContain('证据引用 1 条')
  })

  it('没有学习任务时显示空状态且不出现 mock 任务', async () => {
    vi.mocked(fetchLearningTasks).mockResolvedValue({ ok: true, data: [] })
    const { wrapper, pinia } = await mountView()
    useAvailabilityStore(pinia).setCapability('learning', 'ready')

    await nextTick()
    await flushPromises()

    expect(wrapper.text()).toContain('暂无学习任务')
    expect(wrapper.text()).not.toContain('示例任务')
  })

  it('加载失败时显示错误提示', async () => {
    vi.mocked(fetchLearningTasks).mockResolvedValue({
      ok: false,
      unavailable: true,
      code: ApiErrorCode.NOT_IMPLEMENTED,
      message: '后端接口尚未实现',
      retryable: false,
    })
    const { wrapper, pinia } = await mountView()
    useAvailabilityStore(pinia).setCapability('learning', 'ready')

    await nextTick()
    await flushPromises()

    expect(wrapper.findComponent({ name: 'ErrorBanner' }).exists()).toBe(true)
    expect(wrapper.text()).toContain('后端接口尚未实现')
  })

  it('点击开始任务后调用 updateStatus', async () => {
    vi.mocked(fetchLearningTasks).mockResolvedValue({ ok: true, data: [task] })
    vi.mocked(updateLearningTaskStatus).mockResolvedValue({
      ok: true,
      data: { ...task, status: 'doing' },
    })
    const { wrapper, pinia } = await mountView()
    useAvailabilityStore(pinia).setCapability('learning', 'ready')
    const learning = useLearningStore(pinia)

    await nextTick()
    await flushPromises()
    await wrapper.get('[aria-label="开始学习任务：补强 Docker 项目证据"]').trigger('click')

    expect(updateLearningTaskStatus).toHaveBeenCalledWith(1, 'doing')
    expect(learning.tasks.at(0)?.status).toBe('doing')
  })
})
