<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string
    detail?: string
    retryLabel?: string
  }>(),
  {
    title: '操作失败',
    detail: '',
    retryLabel: '',
  },
)

const emit = defineEmits<{
  (e: 'retry'): void
}>()
</script>

<template>
  <section class="error-banner" role="alert">
    <div class="error-banner__main">
      <h3 class="error-banner__title">{{ title }}</h3>
      <p v-if="detail" class="error-banner__detail">{{ detail }}</p>
    </div>
    <button
      v-if="retryLabel"
      type="button"
      class="error-banner__retry"
      @click="emit('retry')"
    >
      {{ retryLabel }}
    </button>
  </section>
</template>

<style scoped>
.error-banner {
  display: flex;
  justify-content: space-between;
  gap: var(--space-md);
  background-color: var(--color-risk-high-bg);
  border: 1px solid var(--color-risk-high);
  color: var(--color-risk-high);
  border-radius: var(--rounded-lg);
  padding: var(--space-md) var(--space-lg);
}

.error-banner__main {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.error-banner__title {
  margin: 0;
  font-size: var(--font-body-size);
  font-weight: 600;
}

.error-banner__detail {
  margin: 0;
  color: var(--color-ink-muted);
  font-size: var(--font-body-sm-size);
}

.error-banner__retry {
  background-color: transparent;
  color: inherit;
  border: 1px solid currentColor;
  border-radius: var(--rounded-md);
  padding: 6px 12px;
  font-family: var(--font-family-sans);
  font-size: var(--font-button-size);
  font-weight: var(--font-button-weight);
  cursor: pointer;
  align-self: flex-start;
  transition: background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.error-banner__retry:hover {
  background-color: rgba(229, 72, 77, 0.12);
}
</style>
