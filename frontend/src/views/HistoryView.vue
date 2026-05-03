<script setup lang="ts">
import { computed } from 'vue'
import { useAvailabilityStore } from '@/stores/availability'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'
import EmptyState from '@/components/feedback/EmptyState.vue'

const availability = useAvailabilityStore()
const isUnavailable = computed(() => availability.states.reports === 'unavailable')
</script>

<template>
  <section class="history-view" role="main" aria-label="历史趋势">
    <h1 class="history-view__title">历史趋势</h1>

    <BackendNotReadyNotice
      v-if="isUnavailable"
      feature="历史趋势"
      waitingFor="reports 历史聚合接口"
    />

    <template v-else>
      <div class="history-view__filter">
        <label class="history-view__filter-label" for="history-range">时间区间</label>
        <select
          id="history-range"
          class="history-view__filter-select"
          disabled
        >
          <option>最近 30 天</option>
        </select>
      </div>

      <div class="history-view__chart-placeholder">
        <p class="history-view__chart-text">趋势图表功能尚未上线，等待后端 reports 历史聚合接口完成。</p>
      </div>

      <EmptyState
        title="暂无历史报告"
        description="完成首次分析后，历史趋势将在此展示。"
      />
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

.history-view__filter {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.history-view__filter-label {
  font-size: var(--font-body-size);
  color: var(--color-ink-subtle);
}

.history-view__filter-select {
  font-family: var(--font-family-sans);
  font-size: var(--font-body-size);
  padding: var(--space-xs) var(--space-sm);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-md);
  background-color: var(--color-surface-1);
  color: var(--color-ink);
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
</style>
