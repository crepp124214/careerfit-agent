<script setup lang="ts">
import { computed } from 'vue'

type Variant = 'primary' | 'secondary' | 'tertiary'
type ButtonType = 'button' | 'submit' | 'reset'

const props = withDefaults(
  defineProps<{
    variant?: Variant
    type?: ButtonType
    disabled?: boolean
    loading?: boolean
    error?: boolean
    fullWidth?: boolean
  }>(),
  {
    variant: 'primary',
    type: 'button',
    disabled: false,
    loading: false,
    error: false,
    fullWidth: false,
  },
)

const emit = defineEmits<{
  (e: 'click', payload: MouseEvent): void
}>()

const isInactive = computed(() => props.disabled || props.loading)

const classNames = computed(() => [
  'app-button',
  `app-button--${props.variant}`,
  {
    'app-button--loading': props.loading,
    'app-button--error': props.error,
    'app-button--block': props.fullWidth,
  },
])

function handleClick(event: MouseEvent) {
  if (isInactive.value) {
    event.preventDefault()
    return
  }
  emit('click', event)
}
</script>

<template>
  <button
    :type="props.type"
    :class="classNames"
    :disabled="isInactive"
    :aria-busy="props.loading || undefined"
    :aria-invalid="props.error || undefined"
    @click="handleClick"
  >
    <span v-if="props.loading" class="app-button__spinner" aria-hidden="true" />
    <span class="app-button__label">
      <slot />
    </span>
  </button>
</template>

<style scoped>
.app-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
  padding: 8px 14px;
  border-radius: var(--rounded-md);
  border: 1px solid transparent;
  font-family: var(--font-family-sans);
  font-size: var(--font-button-size);
  font-weight: var(--font-button-weight);
  line-height: var(--font-button-line);
  letter-spacing: var(--font-button-letter);
  cursor: pointer;
  transition:
    background-color var(--motion-duration-fast) var(--motion-easing-standard),
    border-color var(--motion-duration-fast) var(--motion-easing-standard),
    color var(--motion-duration-fast) var(--motion-easing-standard);
}

.app-button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.app-button--block {
  width: 100%;
}

/* primary —— Next Best Action / 主行动 */
.app-button--primary {
  background-color: var(--color-primary);
  color: var(--color-on-primary);
  border-color: var(--color-primary);
}

.app-button--primary:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
}

.app-button--primary:active:not(:disabled) {
  background-color: var(--color-primary-focus);
  border-color: var(--color-primary-focus);
}

/* secondary —— 次行动 */
.app-button--secondary {
  background-color: var(--color-surface-1);
  color: var(--color-ink);
  border-color: var(--color-hairline);
}

.app-button--secondary:hover:not(:disabled) {
  background-color: var(--color-surface-2);
  border-color: var(--color-hairline-strong);
}

.app-button--secondary:active:not(:disabled) {
  background-color: var(--color-surface-3);
}

/* tertiary —— 弱行动 */
.app-button--tertiary {
  background-color: var(--color-canvas);
  color: var(--color-ink-muted);
  border-color: transparent;
}

.app-button--tertiary:hover:not(:disabled) {
  color: var(--color-ink);
  background-color: var(--color-surface-1);
}

.app-button--tertiary:active:not(:disabled) {
  background-color: var(--color-surface-2);
}

/* error 状态 —— 提交失败时高亮 */
.app-button--error {
  border-color: var(--color-risk-high);
}

/* loading spinner */
.app-button__spinner {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid currentColor;
  border-right-color: transparent;
  animation: app-button-spin 0.7s linear infinite;
}

.app-button--loading .app-button__label {
  opacity: 0.7;
}

@keyframes app-button-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
