<script setup lang="ts">
import { computed } from 'vue'
import type { Dimension } from '@/api/reports'
import RiskPill from '@/components/risk/RiskPill.vue'
import EvidenceCard from './EvidenceCard.vue'

const props = defineProps<{
  dimension: Dimension
}>()

const barColor = computed(() => {
  if (props.dimension.riskLevel === 'high') return 'var(--color-risk-high)'
  if (props.dimension.riskLevel === 'medium') return 'var(--color-risk-medium)'
  return 'var(--color-risk-low)'
})

const gap = computed(() => Math.max(0, props.dimension.threshold - props.dimension.score))
</script>

<template>
  <article class="dim-card">
    <header class="dim-card__header">
      <h4 class="dim-card__name">{{ dimension.name }}</h4>
      <div class="dim-card__score-row">
        <span class="dim-card__score">{{ dimension.score }}</span>
        <RiskPill :level="dimension.riskLevel" />
      </div>
    </header>

    <div class="dim-card__bar-track">
      <div
        class="dim-card__bar-fill"
        :style="{ width: `${dimension.score}%`, backgroundColor: barColor }"
      />
      <div
        class="dim-card__bar-threshold"
        :style="{ left: `${dimension.threshold}%` }"
        :title="`阈值 ${dimension.threshold}`"
      />
    </div>

    <div class="dim-card__meta">
      <span class="dim-card__threshold-text">阈值 {{ dimension.threshold }}</span>
      <span v-if="gap > 0" class="dim-card__gap-text">差 {{ gap }} 分</span>
    </div>

    <p class="dim-card__reason">{{ dimension.reason }}</p>

    <div v-if="dimension.evidence?.length" class="dim-card__evidence">
      <EvidenceCard
        v-for="(ev, i) in dimension.evidence"
        :key="i"
        :evidence="ev"
      />
    </div>
  </article>
</template>

<style scoped>
.dim-card {
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  transition:
    border-color var(--motion-duration-fast) var(--motion-easing-standard),
    box-shadow var(--motion-duration-fast) var(--motion-easing-standard);
}

.dim-card:hover {
  border-color: var(--color-hairline-strong);
  box-shadow: var(--shadow-sm);
}

.dim-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-sm);
}

.dim-card__name {
  margin: 0;
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
  line-height: var(--font-card-title-line);
}

.dim-card__score-row {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  flex-shrink: 0;
}

.dim-card__score {
  font-size: var(--font-card-title-size);
  font-weight: 600;
  color: var(--color-ink);
  font-variant-numeric: tabular-nums;
}

.dim-card__bar-track {
  position: relative;
  height: 6px;
  background-color: var(--color-surface-3);
  border-radius: var(--rounded-pill);
  overflow: visible;
}

.dim-card__bar-fill {
  height: 100%;
  border-radius: var(--rounded-pill);
  transition: width 0.4s var(--motion-easing-emphasized);
}

.dim-card__bar-threshold {
  position: absolute;
  top: -2px;
  width: 2px;
  height: 10px;
  background-color: var(--color-ink-subtle);
  border-radius: 1px;
}

.dim-card__meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dim-card__threshold-text {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

.dim-card__gap-text {
  font-size: var(--font-caption-size);
  font-weight: 500;
  color: var(--color-risk-medium);
}

.dim-card__reason {
  margin: 0;
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-muted);
  line-height: var(--font-body-sm-line);
}

.dim-card__evidence {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  margin-top: var(--space-xxs);
}
</style>
