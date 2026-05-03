<script setup lang="ts">
import type { Suggestion } from '@/api/reports'
import RiskPill from '@/components/risk/RiskPill.vue'

defineProps<{
  suggestion: Suggestion
}>()
</script>

<template>
  <article
    class="suggestion-card"
    :class="{ 'suggestion-card--blocked': suggestion.blocked }"
  >
    <header class="suggestion-card__header">
      <h4 class="suggestion-card__title">简历建议</h4>
      <RiskPill :level="suggestion.riskLevel" />
    </header>

    <div class="suggestion-card__fields">
      <div class="suggestion-card__field">
        <span class="suggestion-card__label">原始依据</span>
        <p class="suggestion-card__value">{{ suggestion.original }}</p>
      </div>

      <div class="suggestion-card__field">
        <span class="suggestion-card__label">优化表达</span>
        <p class="suggestion-card__value suggestion-card__value--optimized">
          {{ suggestion.optimized }}
        </p>
      </div>

      <div class="suggestion-card__field">
        <span class="suggestion-card__label">关联 JD 要求</span>
        <p class="suggestion-card__value">{{ suggestion.jdRequirement }}</p>
      </div>

      <div class="suggestion-card__field">
        <span class="suggestion-card__label">使用的简历证据</span>
        <p class="suggestion-card__value">{{ suggestion.resumeEvidence }}</p>
      </div>
    </div>
  </article>
</template>

<style scoped>
.suggestion-card {
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.suggestion-card--blocked {
  background-color: var(--color-surface-2);
  opacity: 0.7;
}

.suggestion-card--blocked .suggestion-card__value {
  color: var(--color-ink-muted);
}

.suggestion-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-md);
}

.suggestion-card__title {
  margin: 0;
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
  line-height: var(--font-card-title-line);
}

.suggestion-card__fields {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.suggestion-card__field {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.suggestion-card__label {
  font-size: var(--font-caption-size);
  font-weight: 500;
  color: var(--color-ink-subtle);
}

.suggestion-card__value {
  margin: 0;
  font-size: var(--font-body-sm-size);
  color: var(--color-ink);
  line-height: var(--font-body-sm-line);
}

.suggestion-card__value--optimized {
  color: var(--color-ink);
  background-color: var(--color-surface-2);
  padding: var(--space-xs);
  border-radius: var(--rounded-xs);
}
</style>
