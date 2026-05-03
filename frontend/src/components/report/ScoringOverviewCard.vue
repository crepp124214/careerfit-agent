<script setup lang="ts">
import type { Dimension } from '@/api/reports'
import RiskPill from '@/components/risk/RiskPill.vue'

const props = defineProps<{
  totalScore: number
  dimensions: Dimension[]
}>()

const best = () =>
  [...props.dimensions].sort((a, b) => b.score - a.score)[0]

const worst = () =>
  [...props.dimensions].sort((a, b) => a.score - b.score)[0]
</script>

<template>
  <section class="scoring-overview" aria-label="评分总览">
    <div class="scoring-overview__score">
      <span class="scoring-overview__number">{{ totalScore }}</span>
      <span class="scoring-overview__label">总分</span>
    </div>

    <div class="scoring-overview__summary">
      <div v-if="dimensions.length > 0" class="scoring-overview__extremes">
        <div class="scoring-overview__extreme">
          <span class="scoring-overview__extreme-label">最高维度</span>
          <span class="scoring-overview__extreme-name">
            {{ best()?.name }}
            <RiskPill level="low" />
          </span>
          <span class="scoring-overview__extreme-score">{{ best()?.score }}</span>
        </div>
        <div class="scoring-overview__extreme">
          <span class="scoring-overview__extreme-label">最低维度</span>
          <span class="scoring-overview__extreme-name">
            {{ worst()?.name }}
            <RiskPill :level="worst()?.riskLevel ?? 'medium'" />
          </span>
          <span class="scoring-overview__extreme-score">{{ worst()?.score }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.scoring-overview {
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-xl);
  padding: var(--space-xl);
  display: flex;
  gap: var(--space-xl);
  align-items: center;
}

.scoring-overview__score {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xxs);
}

.scoring-overview__number {
  font-size: var(--font-display-lg-size);
  font-weight: var(--font-display-lg-weight);
  line-height: var(--font-display-lg-line);
  letter-spacing: var(--font-display-lg-letter);
  color: var(--color-ink);
}

.scoring-overview__label {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

.scoring-overview__summary {
  flex: 1;
}

.scoring-overview__extremes {
  display: flex;
  gap: var(--space-lg);
}

.scoring-overview__extreme {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.scoring-overview__extreme-label {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

.scoring-overview__extreme-name {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-size: var(--font-body-size);
  font-weight: 500;
  color: var(--color-ink);
}

.scoring-overview__extreme-score {
  font-size: var(--font-body-size);
  color: var(--color-ink-muted);
}

@media (max-width: 768px) {
  .scoring-overview {
    flex-direction: column;
    align-items: flex-start;
  }

  .scoring-overview__extremes {
    flex-direction: column;
  }
}
</style>
