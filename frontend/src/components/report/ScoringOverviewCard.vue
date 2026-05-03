<script setup lang="ts">
import { computed } from 'vue'
import type { Dimension } from '@/api/reports'
import RiskPill from '@/components/risk/RiskPill.vue'

const props = defineProps<{
  totalScore: number
  dimensions: Dimension[]
}>()

const RING_RADIUS = 36
const RING_CIRCUMFERENCE = 2 * Math.PI * RING_RADIUS
const RING_VIEWBOX = 88

const scoreColor = computed(() => {
  if (props.totalScore >= 70) return 'var(--color-risk-low)'
  if (props.totalScore >= 50) return 'var(--color-risk-medium)'
  return 'var(--color-risk-high)'
})

const ringOffset = computed(
  () => RING_CIRCUMFERENCE * (1 - props.totalScore / 100),
)

const best = () =>
  [...props.dimensions].sort((a, b) => b.score - a.score)[0]

const worst = () =>
  [...props.dimensions].sort((a, b) => a.score - b.score)[0]
</script>

<template>
  <section class="scoring-overview" aria-label="评分总览">
    <div class="scoring-overview__score">
      <svg
        class="scoring-overview__ring"
        :width="RING_VIEWBOX"
        :height="RING_VIEWBOX"
        :viewBox="`0 0 ${RING_VIEWBOX} ${RING_VIEWBOX}`"
        aria-hidden="true"
      >
        <circle
          :cx="RING_VIEWBOX / 2"
          :cy="RING_VIEWBOX / 2"
          :r="RING_RADIUS"
          fill="none"
          stroke="var(--color-surface-2)"
          stroke-width="6"
        />
        <circle
          :cx="RING_VIEWBOX / 2"
          :cy="RING_VIEWBOX / 2"
          :r="RING_RADIUS"
          fill="none"
          :stroke="scoreColor"
          stroke-width="6"
          stroke-linecap="round"
          :stroke-dasharray="RING_CIRCUMFERENCE"
          :stroke-dashoffset="ringOffset"
          transform="rotate(-90 44 44)"
          class="scoring-overview__ring-progress"
        />
      </svg>
      <span class="scoring-overview__number" :style="{ color: scoreColor }">{{ totalScore }}</span>
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
  background-color: var(--color-surface-2);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-xl);
  padding: var(--space-xl);
  display: flex;
  gap: var(--space-xl);
  align-items: center;
}

.scoring-overview__score {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xxs);
}

.scoring-overview__ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -60%);
  pointer-events: none;
}

.scoring-overview__ring-progress {
  transition: stroke-dashoffset var(--motion-duration-slow) var(--motion-easing-emphasized);
}

.scoring-overview__number {
  font-size: var(--font-display-lg-size);
  font-weight: var(--font-display-lg-weight);
  line-height: var(--font-display-lg-line);
  letter-spacing: var(--font-display-lg-letter);
  position: relative;
  z-index: 1;
}

.scoring-overview__label {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
  position: relative;
  z-index: 1;
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
