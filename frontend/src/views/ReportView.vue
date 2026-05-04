<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAvailabilityStore } from '@/stores/availability'
import { useAnalysesStore } from '@/stores/analyses'
import { useInterviewStore } from '@/stores/interview'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'
import LoadingCard from '@/components/feedback/LoadingCard.vue'
import ErrorBanner from '@/components/feedback/ErrorBanner.vue'
import NextBestActionCallout from '@/components/workbench/NextBestActionCallout.vue'
import IntegrityGuardBanner from '@/components/risk/IntegrityGuardBanner.vue'
import ScoringOverviewCard from '@/components/report/ScoringOverviewCard.vue'
import ScoringDimensionCard from '@/components/report/ScoringDimensionCard.vue'
import SuggestionCard from '@/components/report/SuggestionCard.vue'
import InterviewQuestionCard from '@/components/report/InterviewQuestionCard.vue'
import LearningPlanCard from '@/components/report/LearningPlanCard.vue'
import AgentTraceTimeline from '@/components/report/AgentTraceTimeline.vue'

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

function exportPdf() {
  const id = Number(taskId.value)
  if (!id) return
  window.open(`/api/reports/${id}/export?format=pdf`, '_blank')
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
    <div class="report-view__header-row">
      <h1 class="report-view__title animate-in">分析报告</h1>
      <div v-if="hasReport" class="report-view__export">
        <button type="button" class="report-view__export-btn" @click="exportMarkdown">
          导出 Markdown
        </button>
        <button type="button" class="report-view__export-btn" @click="exportPdf">
          打印 / PDF
        </button>
      </div>
    </div>

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

    <template v-else-if="hasReport">
      <NextBestActionCallout
        v-if="analyses.report!.nextBestAction"
        :state="analyses.report!.nextBestAction.state"
        :headline="analyses.report!.nextBestAction.headline"
        :action-label="analyses.report!.nextBestAction.actionLabel"
        :cta-to="analyses.report!.nextBestAction.ctaTo ?? '/learning'"
        :waiting-reason="analyses.report!.nextBestAction.waitingReason"
      />

      <ScoringOverviewCard
        class="animate-in animate-in-stagger-1"
        :total-score="analyses.report!.totalScore"
        :dimensions="analyses.report!.dimensions"
      />

      <section class="report-view__dimensions animate-in animate-in-stagger-2" aria-label="评分明细">
        <h2 class="report-view__section-title">评分明细</h2>
        <div class="report-view__dimension-grid">
          <ScoringDimensionCard
            v-for="dim in analyses.report!.dimensions"
            :key="dim.name"
            :dimension="dim"
          />
        </div>
      </section>

      <section class="report-view__suggestions animate-in animate-in-stagger-3" aria-label="简历建议">
        <h2 class="report-view__section-title">简历建议</h2>

        <IntegrityGuardBanner
          v-if="analyses.hasIntegrityGuard"
          :blocked-count="analyses.report!.integrityGuard!.blockedCount"
          :summary="analyses.report!.integrityGuard!.summary"
        />

        <div class="report-view__suggestion-list">
          <SuggestionCard
            v-for="(sug, i) in analyses.report!.suggestions"
            :key="i"
            :suggestion="sug"
          />
        </div>
      </section>

      <section
        v-if="analyses.report!.interviewQuestions.length > 0"
        class="report-view__interview animate-in animate-in-stagger-4"
        aria-label="面试问题"
      >
        <h2 class="report-view__section-title">面试问题</h2>
        <div class="report-view__interview-list">
          <InterviewQuestionCard
            v-for="(q, i) in analyses.report!.interviewQuestions"
            :key="i"
            :question="q"
          />
        </div>
        <div class="report-view__interview-cta">
          <button
            type="button"
            class="report-view__interview-btn"
            @click="startInterviewTraining"
          >
            开始面试训练
          </button>
        </div>
      </section>

      <section
        v-if="analyses.report!.learningPlan.length > 0"
        class="report-view__learning animate-in animate-in-stagger-5"
        aria-label="学习计划"
      >
        <h2 class="report-view__section-title">学习计划</h2>
        <div class="report-view__learning-list">
          <LearningPlanCard
            v-for="(item, i) in analyses.report!.learningPlan"
            :key="i"
            :item="item"
          />
        </div>
      </section>

      <AgentTraceTimeline
        v-if="analyses.nodes.length > 0"
        class="animate-in animate-in-stagger-6"
        :nodes="analyses.nodes"
      />
    </template>

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
  max-width: 880px;
}

.report-view__title {
  margin: 0;
  font-size: var(--font-headline-size);
  font-weight: var(--font-headline-weight);
  line-height: var(--font-headline-line);
}

.report-view__section-title {
  margin: 0 0 var(--space-sm);
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
  line-height: var(--font-card-title-line);
}

.report-view__dimensions {
  display: flex;
  flex-direction: column;
}

.report-view__dimension-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-md);
}

@media (min-width: 768px) {
  .report-view__dimension-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .report-view__dimension-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 480px) {
  .report-view {
    gap: var(--space-md);
  }

  .report-view__title {
    font-size: 28px;
    letter-spacing: -0.5px;
  }

  .report-view__dimension-grid {
    gap: var(--space-sm);
  }
}

.report-view__suggestions {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.report-view__suggestion-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.report-view__interview,
.report-view__learning {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.report-view__interview-list,
.report-view__learning-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.report-view__interview-cta {
  margin-top: var(--space-md);
  display: flex;
  justify-content: center;
}

.report-view__interview-btn {
  padding: var(--space-sm) var(--space-lg);
  background: var(--color-primary);
  color: var(--color-on-primary);
  border: none;
  border-radius: var(--rounded-md);
  font-size: var(--font-body-size);
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s ease;
}

.report-view__interview-btn:hover {
  opacity: 0.9;
}

.report-view__header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.report-view__export {
  display: flex;
  gap: var(--space-xs);
}

.report-view__export-btn {
  padding: var(--space-xs) var(--space-sm);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-sm);
  background: var(--color-surface-1);
  font-size: var(--font-caption-size);
  cursor: pointer;
  transition: background 0.15s ease;
}

.report-view__export-btn:hover {
  background: var(--color-surface-2);
}
</style>
