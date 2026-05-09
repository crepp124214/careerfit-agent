import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

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
import InterviewDetailView from '@/views/InterviewDetailView.vue'
import AgentTraceView from '@/views/AgentTraceView.vue'
import SettingsView from '@/views/SettingsView.vue'
import NotFoundView from '@/views/NotFoundView.vue'

export const routes: RouteRecordRaw[] = [
  { path: '/', name: 'workspace', component: WorkspaceView },
  { path: '/jobs', name: 'jobs', component: JobsView },
  { path: '/jobs/:id', name: 'job-detail', component: JobDetailView, props: true },
  { path: '/resumes', name: 'resumes', component: ResumesView },
  { path: '/resumes/:id', name: 'resume-detail', component: ResumeDetailView, props: true },
  { path: '/analyses/new', name: 'analysis-run', component: AnalysisRunView },
  { path: '/reports/:taskId', name: 'report', component: ReportView, props: true },
  { path: '/history', name: 'history', component: HistoryView },
  { path: '/diff', name: 'version-diff', component: VersionDiffView },
  { path: '/learning', redirect: '/interview?tab=learning' },
  { path: '/interview', name: 'interview', component: InterviewView },
  { path: '/interview/:id', name: 'interview-detail', component: InterviewDetailView },
  { path: '/interview-bank', redirect: '/interview?tab=bank' },
  { path: '/trace/:taskId', name: 'agent-trace', component: AgentTraceView, props: true },
  { path: '/settings', name: 'settings', component: SettingsView },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundView },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
