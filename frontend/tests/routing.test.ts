import { describe, it, expect, beforeEach } from 'vitest'
import { createRouter, createMemoryHistory } from 'vue-router'
import type { Router } from 'vue-router'

import { routes } from '@/router/index'
import WorkspaceView from '@/views/WorkspaceView.vue'
import JobsView from '@/views/JobsView.vue'
import JobDetailView from '@/views/JobDetailView.vue'
import ResumesView from '@/views/ResumesView.vue'
import ResumeDetailView from '@/views/ResumeDetailView.vue'
import AnalysisRunView from '@/views/AnalysisRunView.vue'
import ReportView from '@/views/ReportView.vue'
import HistoryView from '@/views/HistoryView.vue'
import VersionDiffView from '@/views/VersionDiffView.vue'
import InterviewView from '@/views/InterviewView.vue'
import AgentTraceView from '@/views/AgentTraceView.vue'
import SettingsView from '@/views/SettingsView.vue'
import NotFoundView from '@/views/NotFoundView.vue'

interface RouteCase {
  readonly path: string
  readonly name: string
  readonly component: unknown
}

const ROUTE_CASES: readonly RouteCase[] = [
  { path: '/', name: 'workspace', component: WorkspaceView },
  { path: '/jobs', name: 'jobs', component: JobsView },
  { path: '/jobs/abc-123', name: 'job-detail', component: JobDetailView },
  { path: '/resumes', name: 'resumes', component: ResumesView },
  { path: '/resumes/v3', name: 'resume-detail', component: ResumeDetailView },
  { path: '/analyses/new', name: 'analysis-run', component: AnalysisRunView },
  { path: '/reports/task-42', name: 'report', component: ReportView },
  { path: '/history', name: 'history', component: HistoryView },
  { path: '/diff', name: 'version-diff', component: VersionDiffView },
  { path: '/interview', name: 'interview', component: InterviewView },
  { path: '/trace/task-42', name: 'agent-trace', component: AgentTraceView },
  { path: '/settings', name: 'settings', component: SettingsView },
] as const

let router: Router

beforeEach(() => {
  router = createRouter({
    history: createMemoryHistory(),
    routes,
  })
})

describe('router smoke', () => {
  it('注册了 16 条路由（12 主路由 + 2 重定向 + 1 详情 + 1 通配 NotFound）', () => {
    expect(routes).toHaveLength(16)
  })

  it('每个主路由都能解析到预期 view', async () => {
    for (const route of ROUTE_CASES) {
      await router.push(route.path)
      await router.isReady()
      const matched = router.currentRoute.value.matched
      expect(matched.length, `路径 ${route.path} 至少需要匹配一个 record`).toBeGreaterThan(0)
      const last = matched[matched.length - 1]
      expect(last, `路径 ${route.path} 的尾部匹配存在`).toBeDefined()
      expect(last?.name, `路径 ${route.path} 的 name 应是 ${route.name}`).toBe(route.name)
      expect(last?.components?.default, `路径 ${route.path} 的 view 应是预期组件`).toBe(route.component)
    }
  })

  it('根路径 / 命中 WorkspaceView', async () => {
    await router.push('/')
    await router.isReady()
    const matched = router.currentRoute.value.matched
    expect(matched[matched.length - 1]?.components?.default).toBe(WorkspaceView)
  })

  it('未知路径命中 NotFoundView', async () => {
    await router.push('/this-path-does-not-exist/abc/123')
    await router.isReady()
    const matched = router.currentRoute.value.matched
    expect(matched[matched.length - 1]?.name).toBe('not-found')
    expect(matched[matched.length - 1]?.components?.default).toBe(NotFoundView)
  })
})
