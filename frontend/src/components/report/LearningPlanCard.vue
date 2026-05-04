<script setup lang="ts">
import type { LearningPlanItem } from '@/api/reports'

defineProps<{
  item: LearningPlanItem
}>()
</script>

<template>
  <article class="learning-plan-card">
    <span class="learning-plan-card__skill">{{ item.skill }}</span>
    <p class="learning-plan-card__task">{{ item.task }}</p>
  </article>
</template>

<style scoped>
.learning-plan-card {
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-md);
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.learning-plan-card__skill {
  font-size: var(--font-caption-size);
  font-weight: 500;
  color: var(--color-primary);
}

.learning-plan-card__task {
  margin: 0;
  font-size: var(--font-body-size);
  color: var(--color-ink);
  line-height: var(--font-body-line);
}
</style>
