<script setup lang="ts">
defineOptions({ name: 'EmptyState' })

withDefaults(
  defineProps<{
    title?: string
    description?: string
    actionLabel?: string
  }>(),
  {
    title: '当前还没有内容',
    description: '',
    actionLabel: '',
  },
)

const emit = defineEmits<{
  (e: 'action'): void
}>()
</script>

<template>
  <section class="empty-state" role="status">
    <h3 class="empty-state__title">{{ title }}</h3>
    <p v-if="description" class="empty-state__description">{{ description }}</p>
    <button
      v-if="actionLabel"
      type="button"
      class="empty-state__action"
      @click="emit('action')"
    >
      {{ actionLabel }}
    </button>
  </section>
</template>

<style scoped>
.empty-state {
  background-color: var(--color-surface-1);
  border: 1px dashed var(--color-hairline);
  border-radius: var(--rounded-lg);
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--space-xs);
  color: var(--color-ink-muted);
}

.empty-state__title {
  margin: 0;
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
  line-height: var(--font-card-title-line);
  color: var(--color-ink);
}

.empty-state__description {
  margin: 0;
  color: var(--color-ink-subtle);
  font-size: var(--font-body-sm-size);
  line-height: var(--font-body-sm-line);
}

.empty-state__action {
  margin-top: var(--space-xs);
  background-color: var(--color-primary);
  color: var(--color-on-primary);
  border: 1px solid var(--color-primary);
  border-radius: var(--rounded-md);
  padding: 8px 14px;
  font-family: var(--font-family-sans);
  font-size: var(--font-button-size);
  font-weight: var(--font-button-weight);
  cursor: pointer;
  transition: background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.empty-state__action:hover {
  background-color: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
}
</style>
