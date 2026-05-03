<script setup lang="ts">
import SkeletonBlock from './SkeletonBlock.vue'

withDefaults(
  defineProps<{
    title?: string
    lines?: number
  }>(),
  {
    title: '加载中…',
    lines: 3,
  },
)
</script>

<template>
  <section
    class="loading-card"
    role="status"
    aria-live="polite"
    :aria-label="title"
  >
    <div class="loading-card__header">
      <SkeletonBlock width="40%" height="16px" />
      <SkeletonBlock width="20%" height="12px" />
    </div>
    <div class="loading-card__body">
      <SkeletonBlock
        v-for="i in lines"
        :key="i"
        width="100%"
        height="12px"
      />
    </div>
    <p class="loading-card__hint">{{ title }}</p>
  </section>
</template>

<style scoped>
.loading-card {
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.loading-card__header {
  display: flex;
  justify-content: space-between;
  gap: var(--space-md);
}

.loading-card__body {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.loading-card__hint {
  margin: 0;
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}
</style>
