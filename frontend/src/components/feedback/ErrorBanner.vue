<script setup lang="ts">
import { computed } from 'vue'
import type { ApiError } from '@/api/client'
import { ApiErrorCode, isRetryable } from '@/api/client'

const props = withDefaults(
  defineProps<{
    title?: string
    detail?: string
    retryLabel?: string
    error?: ApiError | null
  }>(),
  {
    title: '操作失败',
    detail: '',
    retryLabel: '',
    error: null,
  },
)

const emit = defineEmits<{
  (e: 'retry'): void
}>()

const displayTitle = computed(() => {
  if (props.title) return props.title
  if (props.error) {
    return props.error.message
  }
  return '操作失败'
})

const displayDetail = computed(() => {
  if (props.detail) return props.detail
  if (props.error?.detail) {
    return props.error.detail
  }
  return ''
})

const showRetry = computed(() => {
  if (props.retryLabel) return true
  if (props.error && isRetryable(props.error)) return true
  return false
})

const retryText = computed(() => {
  if (props.retryLabel) return props.retryLabel
  return '重试'
})

const errorIcon = computed(() => {
  if (!props.error) return '⚠️'
  switch (props.error.code) {
    case ApiErrorCode.NETWORK_ERROR:
      return '🔌'
    case ApiErrorCode.TIMEOUT:
      return '⏱️'
    case ApiErrorCode.NOT_FOUND:
    case ApiErrorCode.NOT_IMPLEMENTED:
      return '🚧'
    case ApiErrorCode.UNAUTHORIZED:
    case ApiErrorCode.FORBIDDEN:
      return '🔒'
    case ApiErrorCode.VALIDATION_ERROR:
      return '📝'
    case ApiErrorCode.SERVER_ERROR:
      return '🔧'
    default:
      return '⚠️'
  }
})
</script>

<template>
  <section class="error-banner" role="alert" :class="`error-banner--${error?.code ?? 'default'}`">
    <div class="error-banner__main">
      <div class="error-banner__header">
        <span class="error-banner__icon" aria-hidden="true">{{ errorIcon }}</span>
        <h3 class="error-banner__title">{{ displayTitle }}</h3>
      </div>
      <p v-if="displayDetail" class="error-banner__detail">{{ displayDetail }}</p>
    </div>
    <button
      v-if="showRetry"
      type="button"
      class="error-banner__retry"
      @click="emit('retry')"
    >
      {{ retryText }}
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

.error-banner__header {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.error-banner__icon {
  font-size: 16px;
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

.error-banner--TIMEOUT,
.error-banner--NETWORK_ERROR {
  background-color: rgba(242, 153, 74, 0.1);
  border-color: #f2994a;
  color: #f2994a;
}

.error-banner--NOT_FOUND,
.error-banner--NOT_IMPLEMENTED {
  background-color: rgba(139, 149, 161, 0.1);
  border-color: var(--color-ink-subtle);
  color: var(--color-ink-subtle);
}

.error-banner--UNAUTHORIZED,
.error-banner--FORBIDDEN {
  background-color: rgba(107, 117, 224, 0.1);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

@media (max-width: 480px) {
  .error-banner {
    flex-direction: column;
    gap: var(--space-sm);
  }

  .error-banner__retry {
    align-self: flex-end;
  }
}
</style>
