<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useJobsStore } from '@/stores/jobs'
import { useResumesStore } from '@/stores/resumes'
import { useAnalysesStore } from '@/stores/analyses'
import NextBestActionCallout from './NextBestActionCallout.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'

const router = useRouter()
const jobs = useJobsStore()
const resumes = useResumesStore()
const analyses = useAnalysesStore()

const latestReport = computed(() => analyses.report)

const topGaps = computed(() => {
  if (!latestReport.value?.dimensions) return []
  return latestReport.value.dimensions
    .filter(d => d.score < 50)
    .slice(0, 3)
    .map(d => ({ skillKey: d.name, priority: d.riskLevel }))
})

const hasSelection = computed(() => jobs.selectedId && resumes.selectedId)

const nbaState = computed(() => {
  if (latestReport.value) return 'ready' as const
  if (hasSelection.value) return 'ready' as const
  return 'empty' as const
})

const nbaHeadline = computed(() => {
  if (latestReport.value?.nextBestAction?.headline) {
    return latestReport.value.nextBestAction.headline
  }
  if (hasSelection.value) return '开始匹配分析'
  return ''
})

const nbaActionLabel = computed(() => {
  if (latestReport.value?.nextBestAction?.actionLabel) {
    return latestReport.value.nextBestAction.actionLabel
  }
  if (hasSelection.value) return '开始分析'
  return ''
})

function onNbaAction() {
  if (latestReport.value) {
    router.push(`/reports/${latestReport.value.taskId}`)
    return
  }
  if (hasSelection.value) {
    router.push({ name: 'analysis-run' })
  }
}
</script>

<template>
  <section class="action-panel" aria-label="分析与行动">
    <NextBestActionCallout
      :state="nbaState"
      :headline="nbaHeadline"
      :action-label="nbaActionLabel"
      @action="onNbaAction"
    />

    <div v-if="latestReport" class="action-panel__report-summary">
      <article class="score-summary">
        <h3 class="score-summary__label">最近报告总分</h3>
        <p class="score-summary__score">{{ latestReport.totalScore }}</p>
        <p class="score-summary__unit">/ 100</p>
      </article>

      <div v-if="topGaps.length > 0" class="action-panel__gaps">
        <h3 class="action-panel__gaps-title">Top {{ topGaps.length }} 缺口</h3>
        <ul class="action-panel__gaps-list">
          <li v-for="(gap, i) in topGaps" :key="i" class="action-panel__gap-item">
            <span class="action-panel__gap-skill">{{ gap.skillKey }}</span>
            <StatusBadge :label="gap.priority" />
          </li>
        </ul>
      </div>
    </div>

    <div v-else-if="hasSelection" class="action-panel__ready">
      <p class="action-panel__ready-text">已选择岗位和简历，点击上方按钮开始分析。</p>
    </div>

    <div v-else class="action-panel__empty">
      <p class="action-panel__empty-text">选择岗位和简历后，这里会显示分析结果。</p>
    </div>
  </section>
</template>

<style scoped>
.action-panel {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.action-panel__report-summary {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.score-summary {
  padding: var(--space-lg);
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-xl);
  box-shadow: var(--shadow-sm);
  text-align: center;
}

.score-summary__label {
  margin: 0 0 var(--space-xs);
  font-size: var(--font-caption-size);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: var(--color-ink-subtle);
}

.score-summary__score {
  margin: 0;
  font-size: var(--font-display-lg-size);
  font-weight: var(--font-display-lg-weight);
  line-height: var(--font-display-lg-line);
  letter-spacing: var(--font-display-lg-letter);
  color: var(--color-ink);
}

.score-summary__unit {
  margin: 0;
  font-size: var(--font-body-size);
  color: var(--color-ink-muted);
}

.action-panel__gaps {
  padding: var(--space-md);
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  box-shadow: var(--shadow-sm);
}

.action-panel__gaps-title {
  margin: 0 0 var(--space-sm);
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
  color: var(--color-ink);
}

.action-panel__gaps-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.action-panel__gap-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-xs) 0;
  border-bottom: 1px solid var(--color-hairline);
}

.action-panel__gap-item:last-child {
  border-bottom: none;
}

.action-panel__gap-skill {
  font-size: var(--font-body-size);
  color: var(--color-ink);
}

.action-panel__empty {
  padding: var(--space-lg);
  background-color: var(--color-surface-1);
  border: 1px dashed var(--color-hairline);
  border-radius: var(--rounded-lg);
  text-align: center;
}

.action-panel__empty-text {
  margin: 0;
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-subtle);
}

.action-panel__ready {
  padding: var(--space-lg);
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  text-align: center;
}

.action-panel__ready-text {
  margin: 0;
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-muted);
}
</style>
