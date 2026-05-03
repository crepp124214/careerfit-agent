<script setup lang="ts">
import { computed, useId } from 'vue'

const props = withDefaults(
  defineProps<{
    modelValue: string
    label?: string
    placeholder?: string
    rows?: number
    disabled?: boolean
    readonly?: boolean
    error?: string
    helper?: string
    required?: boolean
    minHeight?: string
  }>(),
  {
    label: '',
    placeholder: '',
    rows: 6,
    disabled: false,
    readonly: false,
    error: '',
    helper: '',
    required: false,
    minHeight: '200px',
  },
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'blur'): void
  (e: 'focus'): void
}>()

const fieldId = useId()
const helperId = `${fieldId}-helper`
const errorId = `${fieldId}-error`

const hasError = computed(() => props.error.length > 0)

const describedBy = computed(() => {
  const ids: string[] = []
  if (hasError.value) ids.push(errorId)
  else if (props.helper) ids.push(helperId)
  return ids.length ? ids.join(' ') : undefined
})

function onInput(event: Event) {
  const target = event.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
}
</script>

<template>
  <div class="app-textarea" :class="{ 'app-textarea--error': hasError, 'app-textarea--disabled': props.disabled }">
    <label v-if="props.label" :for="fieldId" class="app-textarea__label">
      {{ props.label }}
      <span v-if="props.required" class="app-textarea__required" aria-hidden="true">*</span>
    </label>
    <textarea
      :id="fieldId"
      class="app-textarea__control"
      :value="props.modelValue"
      :placeholder="props.placeholder"
      :rows="props.rows"
      :disabled="props.disabled"
      :readonly="props.readonly"
      :required="props.required"
      :aria-invalid="hasError || undefined"
      :aria-describedby="describedBy"
      :style="{ minHeight: props.minHeight }"
      @input="onInput"
      @blur="emit('blur')"
      @focus="emit('focus')"
    />
    <p v-if="hasError" :id="errorId" class="app-textarea__error">
      {{ props.error }}
    </p>
    <p v-else-if="props.helper" :id="helperId" class="app-textarea__helper">
      {{ props.helper }}
    </p>
  </div>
</template>

<style scoped>
.app-textarea {
  display: flex;
  flex-direction: column;
  gap: var(--space-xxs);
}

.app-textarea__label {
  font-size: var(--font-caption-size);
  font-weight: var(--font-button-weight);
  color: var(--color-ink-muted);
}

.app-textarea__required {
  color: var(--color-risk-high);
  margin-left: 2px;
}

.app-textarea__control {
  background-color: var(--color-surface-1);
  color: var(--color-ink);
  font-family: var(--font-family-sans);
  font-size: var(--font-body-size);
  font-weight: var(--font-body-weight);
  line-height: var(--font-body-line);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-md);
  padding: 12px 14px;
  resize: vertical;
  transition:
    border-color var(--motion-duration-fast) var(--motion-easing-standard),
    background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.app-textarea__control:hover:not(:disabled):not(:read-only) {
  border-color: var(--color-hairline-strong);
}

.app-textarea__control:focus {
  outline: none;
  border-color: var(--color-primary-focus);
}

.app-textarea__control:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.app-textarea--error .app-textarea__control {
  border-color: var(--color-risk-high);
}

.app-textarea__error {
  color: var(--color-risk-high);
  font-size: var(--font-caption-size);
  margin: 0;
}

.app-textarea__helper {
  color: var(--color-ink-subtle);
  font-size: var(--font-caption-size);
  margin: 0;
}
</style>
