<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAvailabilityStore } from '@/stores/availability'
import { useAnalysesStore } from '@/stores/analyses'
import { useInterviewStore } from '@/stores/interview'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'
import LoadingCard from '@/components/feedback/LoadingCard.vue'
import ErrorBanner from '@/components/feedback/ErrorBanner.vue'
import ReportDashboard from '@/components/report/ReportDashboard.vue'

const route = useRoute()
const router = useRouter()
const availability = useAvailabilityStore()
const analyses = useAnalysesStore()
const interviewStore = useInterviewStore()

const taskId = computed(() => (route.params.taskId as string) ?? '')
const isUnavailable = computed(() => availability.states.reports === 'unavailable')
const isValidTaskId = computed(() => taskId.value.trim().length > 0)

const hasReport = computed(
  () => !analyses.loading && !analyses.error && analyses.report !== null,
)

async function load() {
  if (!isValidTaskId.value) return
  if (isUnavailable.value) return
  await analyses.loadReport(taskId.value)
}

async function startInterviewTraining() {
  if (!analyses.report) return
  const reportId = Number(analyses.report.id)
  if (!reportId) return
  const session = await interviewStore.createSession(reportId)
  if (session) {
    router.push(`/interview/${session.id}`)
  }
}

function exportMarkdown() {
  const id = Number(taskId.value)
  if (!id) return
  window.open(`/api/reports/${id}/export?format=markdown`, '_blank')
}

function printReport() {
  window.print()
}

onMounted(load)

watch(
  () => route.params.taskId,
  (id) => {
    if (typeof id === 'string' && id.trim().length > 0) {
      analyses.clear()
      load()
    }
  },
)
</script>

<template>
  <section class="report-view" role="main" aria-label="分析报告">
    <h1 class="report-view__title sr-only">分析报告</h1>

    <ErrorBanner
      v-if="!isValidTaskId"
      title="无效的任务 ID"
      detail="请从工作台或分析记录中选择一个有效的分析任务。"
    />

    <BackendNotReadyNotice
      v-else-if="isUnavailable"
      feature="评分报告"
      waitingFor="analysis pipeline"
    />

    <LoadingCard
      v-else-if="analyses.loading"
      title="正在加载报告…"
      :lines="4"
    />

    <ErrorBanner
      v-else-if="analyses.error"
      title="报告加载失败"
      :detail="analyses.error"
    />

    <ReportDashboard
      v-else-if="hasReport && analyses.report"
      :report="analyses.report"
      :nodes="analyses.nodes"
      @start-interview="startInterviewTraining"
      @export-markdown="exportMarkdown"
      @print="printReport"
    />

    <LoadingCard
      v-else
      title="等待分析结果…"
      :lines="3"
    />
  </section>
</template>

<style scoped>
.report-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  max-width: 1200px;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>
