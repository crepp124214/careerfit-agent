<script setup lang="ts">
defineProps<{
  title: string
}>()
</script>

<template>
  <article class="report-card" role="region" :aria-label="title">
    <header class="report-card__header">
      <h3 class="report-card__title">{{ title }}</h3>
    </header>
    <div class="report-card__body">
      <slot />
    </div>
    <footer v-if="$slots.cta" class="report-card__footer">
      <slot name="cta" />
    </footer>
  </article>
</template>

<style scoped>
.report-card {
  display: flex;
  flex-direction: column;
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.report-card__header {
  padding: var(--space-sm) var(--space-md);
  border-bottom: 1px solid var(--color-hairline);
}

.report-card__title {
  margin: 0;
  font-size: var(--font-body-sm-size);
  font-weight: 600;
  color: var(--color-ink-subtle);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.report-card__body {
  flex: 1;
  padding: var(--space-md);
}

.report-card__footer {
  padding: var(--space-sm) var(--space-md);
  border-top: 1px solid var(--color-hairline);
}
</style>
