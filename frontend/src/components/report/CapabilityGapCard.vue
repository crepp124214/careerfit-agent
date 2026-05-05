<script setup lang="ts">
import { computed } from 'vue'
import type { Dimension } from '@/api/reports'
import RiskPill from '@/components/risk/RiskPill.vue'

const props = defineProps<{
  dimensions: Dimension[]
}>()

const gapDimensions = computed(() =>
  props.dimensions.filter(d => d.riskLevel === 'high' || d.riskLevel === 'medium'),
)

const hasGaps = computed(() => gapDimensions.value.length > 0)

const highGapCount = computed(() =>
  gapDimensions.value.filter(d => d.riskLevel === 'high').length,
)

const mediumGapCount = computed(() =>
  gapDimensions.value.filter(d => d.riskLevel === 'medium').length,
)
</script>

<template>
  <section class="capability-gap" aria-label="能力缺口发现">
    <header class="capability-gap__header">
      <h3 class="capability-gap__title">能力缺口发现</h3>
      <div v-if="hasGaps" class="capability-gap__stats">
        <span class="capability-gap__stat capability-gap__stat--high">
          {{ highGapCount }} 高风险
        </span>
        <span class="capability-gap__stat capability-gap__stat--medium">
          {{ mediumGapCount }} 需关注
        </span>
      </div>
    </header>

    <div v-if="!hasGaps" class="capability-gap__empty">
      <span class="capability-gap__empty-icon" aria-hidden="true">✓</span>
      <p class="capability-gap__empty-text">未发现明显能力缺口，各项维度均达标</p>
    </div>

    <ul v-else class="capability-gap__list">
      <li
        v-for="dim in gapDimensions"
        :key="dim.name"
        class="capability-gap__item"
        :class="{
          'capability-gap__item--high': dim.riskLevel === 'high',
          'capability-gap__item--medium': dim.riskLevel === 'medium',
        }"
      >
        <div class="capability-gap__item-header">
          <span class="capability-gap__item-name">{{ dim.name }}</span>
          <RiskPill :level="dim.riskLevel" />
        </div>

        <div class="capability-gap__bar-track">
          <div
            class="capability-gap__bar-fill"
            :class="{
              'capability-gap__bar-fill--high': dim.riskLevel === 'high',
              'capability-gap__bar-fill--medium': dim.riskLevel === 'medium',
            }"
            :style="{ width: `${dim.score}%` }"
          />
          <div
            class="capability-gap__bar-threshold"
            :style="{ left: `${dim.threshold}%` }"
          />
        </div>

        <div class="capability-gap__item-meta">
          <span class="capability-gap__item-score">
            得分 <strong>{{ dim.score }}</strong> / 阈值 {{ dim.threshold }}
          </span>
        </div>

        <p class="capability-gap__item-reason">{{ dim.reason }}</p>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.capability-gap {
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-xl);
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.capability-gap__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-sm);
}

.capability-gap__title {
  margin: 0;
  font-size: var(--font-body-lg-size);
  font-weight: 600;
  color: var(--color-ink);
}

.capability-gap__stats {
  display: flex;
  gap: var(--space-sm);
}

.capability-gap__stat {
  padding: 2px 8px;
  border-radius: var(--rounded-sm);
  font-size: var(--font-caption-size);
  font-weight: 500;
}

.capability-gap__stat--high {
  background-color: var(--color-risk-high-bg);
  color: var(--color-risk-high);
}

.capability-gap__stat--medium {
  background-color: var(--color-risk-medium-bg);
  color: var(--color-risk-medium);
}

.capability-gap__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-lg);
  text-align: center;
}

.capability-gap__empty-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: var(--color-risk-low-bg);
  color: var(--color-risk-low);
  font-size: var(--font-body-lg-size);
  font-weight: 700;
}

.capability-gap__empty-text {
  margin: 0;
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-muted);
}

.capability-gap__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.capability-gap__item {
  padding: var(--space-md);
  border-radius: var(--rounded-md);
  border: 1px solid var(--color-hairline);
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  transition: border-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.capability-gap__item--high {
  border-color: rgba(229, 72, 77, 0.3);
  background-color: var(--color-risk-high-bg);
}

.capability-gap__item--medium {
  border-color: rgba(245, 165, 36, 0.2);
  background-color: var(--color-risk-medium-bg);
}

.capability-gap__item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-sm);
}

.capability-gap__item-name {
  font-size: var(--font-body-size);
  font-weight: 500;
  color: var(--color-ink);
}

.capability-gap__bar-track {
  position: relative;
  height: 6px;
  background-color: var(--color-surface-3);
  border-radius: var(--rounded-pill);
  overflow: visible;
}

.capability-gap__bar-fill {
  height: 100%;
  border-radius: var(--rounded-pill);
  transition: width 0.4s var(--motion-easing-emphasized);
}

.capability-gap__bar-fill--high {
  background-color: var(--color-risk-high);
}

.capability-gap__bar-fill--medium {
  background-color: var(--color-risk-medium);
}

.capability-gap__bar-threshold {
  position: absolute;
  top: -2px;
  width: 2px;
  height: 10px;
  background-color: var(--color-ink-subtle);
  border-radius: 1px;
}

.capability-gap__item-meta {
  display: flex;
  justify-content: space-between;
}

.capability-gap__item-score {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

.capability-gap__item-score strong {
  color: var(--color-ink);
  font-weight: 600;
}

.capability-gap__item-reason {
  margin: 0;
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-muted);
  line-height: var(--font-body-sm-line);
}

@media (max-width: 768px) {
  .capability-gap {
    padding: var(--space-md);
  }

  .capability-gap__header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
