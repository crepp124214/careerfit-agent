<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAvailabilityStore } from '@/stores/availability'
import { useHistoryStore } from '@/stores/history'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'
import EmptyState from '@/components/feedback/EmptyState.vue'
import LoadingCard from '@/components/feedback/LoadingCard.vue'
import ErrorBanner from '@/components/feedback/ErrorBanner.vue'

const availability = useAvailabilityStore()
const historyStore = useHistoryStore()

const isUnavailable = computed(() => availability.states.reports === 'unavailable')
const isLoading = computed(() => historyStore.status === 'loading')
const isError = computed(() => historyStore.status === 'error')
const isEmpty = computed(() => historyStore.status === 'empty')
const isReady = computed(() => historyStore.status === 'ready')

const scoreDeltaText = computed(() => {
  const delta = historyStore.scoreDelta
  if (delta === null) return null
  if (delta > 0) return `+${delta}`
  return String(delta)
})

const scoreDeltaClass = computed(() => {
  const delta = historyStore.scoreDelta
  if (delta === null) return ''
  if (delta > 0) return 'history-view__score-delta--up'
  if (delta < 0) return 'history-view__score-delta--down'
  return 'history-view__score-delta--same'
})

const scoreDeltaLabel = computed(() => {
  const delta = historyStore.scoreDelta
  if (delta === null) return null
  if (delta > 0) return '上升'
  if (delta < 0) return '下降'
  return '持平'
})

onMounted(() => {
  if (!isUnavailable.value) {
    historyStore.load()
  }
})

function handleRetry() {
  historyStore.load()
}
</script>

<template>
  <section class="history-view" role="main" aria-label="历史趋势">
    <h1 class="history-view__title">历史趋势</h1>

    <BackendNotReadyNotice
      v-if="isUnavailable"
      feature="历史趋势"
      waitingFor="reports 历史聚合接口"
    />

    <div v-else-if="isLoading" class="history-view__loading">
      <LoadingCard message="加载历史趋势..." />
    </div>

    <ErrorBanner
      v-else-if="isError"
      :message="historyStore.error || '加载失败'"
      @retry="handleRetry"
    />

    <EmptyState
      v-else-if="isEmpty"
      title="暂无历史报告"
      description="完成首次分析后，历史趋势将在此展示。"
    />

    <template v-else-if="isReady">
      <div class="history-view__summary">
        <div class="history-view__summary-item">
          <span class="history-view__summary-label">最新分数</span>
          <span class="history-view__latest-score">{{ historyStore.latest?.finalScore ?? '-' }}</span>
        </div>
        <div v-if="historyStore.scoreDelta !== null" class="history-view__summary-item">
          <span class="history-view__summary-label">分数变化</span>
          <span
            class="history-view__score-delta"
            :class="scoreDeltaClass"
            :aria-label="`分数${scoreDeltaLabel}`"
          >
            {{ scoreDeltaText }}
            <span class="history-view__score-delta-label">{{ scoreDeltaLabel }}</span>
          </span>
        </div>
        <div class="history-view__summary-item">
          <span class="history-view__summary-label">当前缺口</span>
          <span class="history-view__gap-count">{{ historyStore.latest?.gapCount ?? 0 }} 项</span>
        </div>
      </div>

      <p v-if="!historyStore.hasEnoughData" class="history-view__partial-notice">
        数据不足以形成趋势，至少完成两次分析后才能展示趋势变化。
      </p>

      <div class="history-view__chart" aria-label="分数趋势图表">
        <div class="history-view__chart-placeholder">
          <p class="history-view__chart-text">
            {{ historyStore.hasEnoughData ? '趋势图表功能即将上线' : '需要更多数据以生成趋势图' }}
          </p>
        </div>
      </div>

      <div class="history-view__list">
        <h2 class="history-view__list-title">历史报告</h2>
        <ul class="history-view__list-items">
          <li v-for="item in historyStore.items" :key="item.taskId" class="history-view__list-item">
            <span class="history-view__list-score">{{ item.finalScore }}</span>
            <span class="history-view__list-job">{{ item.jobTitle }}</span>
            <span class="history-view__list-resume">{{ item.resumeLabel }}</span>
            <span class="history-view__list-date">{{ new Date(item.createdAt).toLocaleDateString('zh-CN') }}</span>
          </li>
        </ul>
      </div>
    </template>
  </section>
</template>

<style scoped>
.history-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  max-width: 960px;
}

.history-view__title {
  margin: 0;
  font-size: var(--font-headline-size);
  font-weight: var(--font-headline-weight);
  line-height: var(--font-headline-line);
}

.history-view__loading {
  display: flex;
  justify-content: center;
  padding: var(--space-xl);
}

.history-view__summary {
  display: flex;
  gap: var(--space-xl);
  padding: var(--space-lg);
  background-color: var(--color-surface-1);
  border-radius: var(--rounded-lg);
}

.history-view__summary-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.history-view__summary-label {
  font-size: var(--font-body-size-sm);
  color: var(--color-ink-subtle);
}

.history-view__latest-score {
  font-size: var(--font-display-size);
  font-weight: var(--font-display-weight);
  color: var(--color-ink);
}

.history-view__score-delta {
  display: flex;
  align-items: baseline;
  gap: var(--space-xs);
  font-size: var(--font-display-size);
  font-weight: var(--font-display-weight);
}

.history-view__score-delta--up {
  color: var(--color-success);
}

.history-view__score-delta--down {
  color: var(--color-risk-high);
}

.history-view__score-delta--same {
  color: var(--color-ink-subtle);
}

.history-view__score-delta-label {
  font-size: var(--font-body-size-sm);
  font-weight: var(--font-body-weight);
}

.history-view__gap-count {
  font-size: var(--font-display-size);
  font-weight: var(--font-display-weight);
  color: var(--color-ink);
}

.history-view__partial-notice {
  margin: 0;
  padding: var(--space-md);
  background-color: var(--color-surface-2);
  border-radius: var(--rounded-md);
  font-size: var(--font-body-size-sm);
  color: var(--color-ink-subtle);
}

.history-view__chart {
  min-height: 200px;
}

.history-view__chart-placeholder {
  background-color: var(--color-surface-1);
  border: 1px dashed var(--color-hairline-strong);
  border-radius: var(--rounded-lg);
  padding: var(--space-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.history-view__chart-text {
  margin: 0;
  color: var(--color-ink-muted);
  font-size: var(--font-body-size);
}

.history-view__list {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.history-view__list-title {
  margin: 0;
  font-size: var(--font-body-size);
  font-weight: var(--font-body-weight-bold);
  color: var(--color-ink);
}

.history-view__list-items {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.history-view__list-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md);
  background-color: var(--color-surface-1);
  border-radius: var(--rounded-md);
}

.history-view__list-score {
  font-size: var(--font-body-size);
  font-weight: var(--font-body-weight-bold);
  color: var(--color-primary);
  min-width: 40px;
}

.history-view__list-job {
  font-size: var(--font-body-size);
  color: var(--color-ink);
  flex: 1;
}

.history-view__list-resume {
  font-size: var(--font-body-size-sm);
  color: var(--color-ink-subtle);
}

.history-view__list-date {
  font-size: var(--font-body-size-sm);
  color: var(--color-ink-muted);
}
</style>
