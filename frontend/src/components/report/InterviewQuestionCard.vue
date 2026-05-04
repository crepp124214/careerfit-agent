<script setup lang="ts">
import type { InterviewQuestion } from '@/api/reports'

defineProps<{
  question: InterviewQuestion
}>()
</script>

<template>
  <article class="interview-question-card">
    <span class="interview-question-card__skill">{{ question.skill }}</span>
    <p class="interview-question-card__text">{{ question.question }}</p>
  </article>
</template>

<style scoped>
.interview-question-card {
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-md);
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.interview-question-card__skill {
  font-size: var(--font-caption-size);
  font-weight: 500;
  color: var(--color-primary);
}

.interview-question-card__text {
  margin: 0;
  font-size: var(--font-body-size);
  color: var(--color-ink);
  line-height: var(--font-body-line);
}
</style>
