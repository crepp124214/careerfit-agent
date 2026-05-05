<script setup lang="ts">
import { computed } from 'vue'
import type { Dimension } from '@/api/reports'

const props = defineProps<{
  totalScore: number
  dimensions: Dimension[]
}>()

const RING_RADIUS = 52
const RING_CIRCUMFERENCE = 2 * Math.PI * RING_RADIUS
const RING_VIEWBOX = 128

const scoreColor = computed(() => {
  if (props.totalScore >= 70) return 'var(--color-risk-low)'
  if (props.totalScore >= 50) return 'var(--color-risk-medium)'
  return 'var(--color-risk-high)'
})

const ringOffset = computed(
  () => RING_CIRCUMFERENCE * (1 - props.totalScore / 100),
)

const scoreLabel = computed(() => {
  if (props.totalScore >= 70) return '匹配度良好'
  if (props.totalScore >= 50) return '有待提升'
  return '差距较大'
})

const scoreLabelColor = computed(() => {
  if (props.totalScore >= 70) return 'var(--color-risk-low)'
  if (props.totalScore >= 50) return 'var(--color-risk-medium)'
  return 'var(--color-risk-high)'
})

const highCount = computed(() =>
  props.dimensions.filter(d => d.riskLevel === 'high').length,
)

const mediumCount = computed(() =>
  props.dimensions.filter(d => d.riskLevel === 'medium').length,
)

const lowCount = computed(() =>
  props.dimensions.filter(d => d.riskLevel === 'low').length,
)
</script>

<template>
  <section class="donut-overview" aria-label="综合匹配度">
    <div class="donut-overview__chart">
      <svg
        class="donut-overview__svg"
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
          stroke="var(--color-surface-3)"
          stroke-width="8"
        />
        <circle
          :cx="RING_VIEWBOX / 2"
          :cy="RING_VIEWBOX / 2"
          :r="RING_RADIUS"
          fill="none"
          :stroke="scoreColor"
          stroke-width="8"
          stroke-linecap="round"
          :stroke-dasharray="RING_CIRCUMFERENCE"
          :stroke-dashoffset="ringOffset"
          transform="rotate(-90 64 64)"
          class="donut-overview__ring-progress"
          :style="{
            '--ring-circumference': RING_CIRCUMFERENCE,
            '--ring-target-offset': ringOffset + 'px',
          }"
        />
      </svg>
      <div class="donut-overview__center">
        <span class="donut-overview__number" :style="{ color: scoreColor }">{{ totalScore }}</span>
        <span class="donut-overview__unit">%</span>
      </div>
    </div>

    <div class="donut-overview__info">
      <h3 class="donut-overview__title">综合匹配度</h3>
      <p class="donut-overview__label" :style="{ color: scoreLabelColor }">{{ scoreLabel }}</p>

      <div class="donut-overview__breakdown">
        <div class="donut-overview__stat donut-overview__stat--low">
          <span class="donut-overview__stat-dot" aria-hidden="true" />
          <span class="donut-overview__stat-count">{{ lowCount }}</span>
          <span class="donut-overview__stat-name">通过</span>
        </div>
        <div class="donut-overview__stat donut-overview__stat--medium">
          <span class="donut-overview__stat-dot" aria-hidden="true" />
          <span class="donut-overview__stat-count">{{ mediumCount }}</span>
          <span class="donut-overview__stat-name">需关注</span>
        </div>
        <div class="donut-overview__stat donut-overview__stat--high">
          <span class="donut-overview__stat-dot" aria-hidden="true" />
          <span class="donut-overview__stat-count">{{ highCount }}</span>
          <span class="donut-overview__stat-name">高风险</span>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.donut-overview {
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-xl);
  padding: var(--space-xl);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-lg);
}

.donut-overview__chart {
  position: relative;
  width: 160px;
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.donut-overview__svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.donut-overview__ring-progress {
  animation: ring-draw 0.8s var(--motion-easing-emphasized) both;
  animation-delay: 0.2s;
  stroke-dashoffset: var(--ring-circumference);
  animation-fill-mode: forwards;
}

.donut-overview__center {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: baseline;
  gap: 1px;
  animation: count-up 0.5s var(--motion-easing-emphasized) both;
  animation-delay: 0.4s;
}

.donut-overview__number {
  font-size: 42px;
  font-weight: 700;
  line-height: 1;
  letter-spacing: -1.5px;
  font-variant-numeric: tabular-nums;
}

.donut-overview__unit {
  font-size: var(--font-body-lg-size);
  font-weight: 500;
  color: var(--color-ink-subtle);
}

.donut-overview__info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xs);
  text-align: center;
}

.donut-overview__title {
  margin: 0;
  font-size: var(--font-body-lg-size);
  font-weight: 600;
  color: var(--color-ink);
}

.donut-overview__label {
  margin: 0;
  font-size: var(--font-body-size);
  font-weight: 500;
}

.donut-overview__breakdown {
  display: flex;
  gap: var(--space-md);
  margin-top: var(--space-xs);
}

.donut-overview__stat {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--font-caption-size);
}

.donut-overview__stat-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.donut-overview__stat--low .donut-overview__stat-dot {
  background-color: var(--color-risk-low);
}

.donut-overview__stat--medium .donut-overview__stat-dot {
  background-color: var(--color-risk-medium);
}

.donut-overview__stat--high .donut-overview__stat-dot {
  background-color: var(--color-risk-high);
}

.donut-overview__stat-count {
  font-weight: 600;
  color: var(--color-ink);
}

.donut-overview__stat-name {
  color: var(--color-ink-subtle);
}

@media (max-width: 768px) {
  .donut-overview {
    padding: var(--space-lg);
  }

  .donut-overview__chart {
    width: 140px;
    height: 140px;
  }

  .donut-overview__number {
    font-size: 36px;
  }
}
</style>
