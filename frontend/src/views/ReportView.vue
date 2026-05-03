<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAvailabilityStore } from '@/stores/availability'
import { useAnalysesStore } from '@/stores/analyses'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'
import LoadingCard from '@/components/feedback/LoadingCard.vue'
import ErrorBanner from '@/components/feedback/ErrorBanner.vue'
import NextBestActionCallout from '@/components/workbench/NextBestActionCallout.vue'
import IntegrityGuardBanner from '@/components/risk/IntegrityGuardBanner.vue'
import ScoringOverviewCard from '@/components/report/ScoringOverviewCard.vue'
import ScoringDimensionCard from '@/components/report/ScoringDimensionCard.vue'
import SuggestionCard from '@/components/report/SuggestionCard.vue'
import AgentTraceTimeline from '@/components/report/AgentTraceTimeline.vue'

const route = useRoute()
const availability = useAvailabilityStore()
const analyses = useAnalysesStore()

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
    <h1 class="report-view__title animate-in">分析报告</h1>

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

      <AgentTraceTimeline
        v-if="analyses.nodes.length > 0"
        class="animate-in animate-in-stagger-4"
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
</style>
