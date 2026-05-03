<script setup lang="ts">
import { computed, useId } from 'vue'

const props = withDefaults(
  defineProps<{
    modelValue: string
    label?: string
    placeholder?: string
    type?: string
    disabled?: boolean
    readonly?: boolean
    error?: string
    helper?: string
    required?: boolean
    autocomplete?: string
  }>(),
  {
    label: '',
    placeholder: '',
    type: 'text',
    disabled: false,
    readonly: false,
    error: '',
    helper: '',
    required: false,
    autocomplete: 'off',
  },
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'blur'): void
  (e: 'focus'): void
}>()

const inputId = useId()
const helperId = `${inputId}-helper`
const errorId = `${inputId}-error`

const hasError = computed(() => props.error.length > 0)

const describedBy = computed(() => {
  const ids: string[] = []
  if (hasError.value) ids.push(errorId)
  else if (props.helper) ids.push(helperId)
  return ids.length ? ids.join(' ') : undefined
})

function onInput(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}
</script>

<template>
  <div class="app-input" :class="{ 'app-input--error': hasError, 'app-input--disabled': props.disabled }">
    <label v-if="props.label" :for="inputId" class="app-input__label">
      {{ props.label }}
      <span v-if="props.required" class="app-input__required" aria-hidden="true">*</span>
    </label>
    <input
      :id="inputId"
      class="app-input__control"
      :value="props.modelValue"
      :type="props.type"
      :placeholder="props.placeholder"
      :disabled="props.disabled"
      :readonly="props.readonly"
      :required="props.required"
      :autocomplete="props.autocomplete"
      :aria-invalid="hasError || undefined"
      :aria-describedby="describedBy"
      @input="onInput"
      @blur="emit('blur')"
      @focus="emit('focus')"
    />
    <p v-if="hasError" :id="errorId" class="app-input__error">
      {{ props.error }}
    </p>
    <p v-else-if="props.helper" :id="helperId" class="app-input__helper">
      {{ props.helper }}
    </p>
  </div>
</template>

<style scoped>
.app-input {
  display: flex;
  flex-direction: column;
  gap: var(--space-xxs);
}

.app-input__label {
  font-size: var(--font-caption-size);
  font-weight: var(--font-button-weight);
  color: var(--color-ink-muted);
}

.app-input__required {
  color: var(--color-risk-high);
  margin-left: 2px;
}

.app-input__control {
  background-color: var(--color-surface-1);
  color: var(--color-ink);
  font-family: var(--font-family-sans);
  font-size: var(--font-body-size);
  font-weight: var(--font-body-weight);
  line-height: var(--font-body-line);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-md);
  padding: 10px 12px;
  transition:
    border-color var(--motion-duration-fast) var(--motion-easing-standard),
    background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.app-input__control:hover:not(:disabled):not(:read-only) {
  border-color: var(--color-hairline-strong);
}

.app-input__control:focus {
  outline: none;
  border-color: var(--color-primary-focus);
}

.app-input__control:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.app-input--error .app-input__control {
  border-color: var(--color-risk-high);
}

.app-input__error {
  color: var(--color-risk-high);
  font-size: var(--font-caption-size);
  margin: 0;
}

.app-input__helper {
  color: var(--color-ink-subtle);
  font-size: var(--font-caption-size);
  margin: 0;
}
</style>
