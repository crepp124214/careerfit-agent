<script setup lang="ts">
import type { Dimension } from '@/api/reports'
import RiskPill from '@/components/risk/RiskPill.vue'
import EvidenceCard from './EvidenceCard.vue'

defineProps<{
  dimension: Dimension
}>()
</script>

<template>
  <article class="dimension-card">
    <header class="dimension-card__header">
      <h4 class="dimension-card__name">{{ dimension.name }}</h4>
      <div class="dimension-card__score-row">
        <span class="dimension-card__score">{{ dimension.score }}</span>
        <RiskPill :level="dimension.riskLevel" />
      </div>
    </header>

    <div class="dimension-card__threshold">
      <span class="dimension-card__threshold-label">阈值：{{ dimension.threshold }}</span>
    </div>

    <p class="dimension-card__reason">{{ dimension.reason }}</p>

    <div v-if="dimension.evidence?.length" class="dimension-card__evidence">
      <EvidenceCard
        v-for="(ev, i) in dimension.evidence"
        :key="i"
        :evidence="ev"
      />
    </div>
  </article>
</template>

<style scoped>
.dimension-card {
  background-color: var(--color-surface-2);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  transition: border-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.dimension-card:hover {
  border-color: var(--color-hairline-strong);
}

.dimension-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-md);
}

.dimension-card__name {
  margin: 0;
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
  line-height: var(--font-card-title-line);
}

.dimension-card__score-row {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.dimension-card__score {
  font-size: var(--font-card-title-size);
  font-weight: 600;
  color: var(--color-ink);
}

.dimension-card__threshold-label {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

.dimension-card__reason {
  margin: 0;
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-muted);
  line-height: var(--font-body-sm-line);
}

.dimension-card__evidence {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  margin-top: var(--space-xxs);
}
</style>
