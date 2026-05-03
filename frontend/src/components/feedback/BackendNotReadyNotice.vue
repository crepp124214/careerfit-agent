<script lang="ts">
import { computed, defineComponent, type PropType } from 'vue'

type Severity = 'status' | 'alert'

export default defineComponent({
  name: 'BackendNotReadyNotice',
  props: {
    feature: {
      type: String,
      required: true,
      validator(value: unknown) {
        return typeof value === 'string' && value.length > 0
      },
    },
    waitingFor: {
      type: String,
      required: true,
      validator(value: unknown) {
        return typeof value === 'string' && value.length > 0
      },
    },
    description: {
      type: String,
      default: '',
    },
    severity: {
      type: String as PropType<Severity>,
      default: 'status',
      validator(value: unknown): value is Severity {
        return value === 'status' || value === 'alert'
      },
    },
  },
  setup(props) {
    const role = computed(() => (props.severity === 'alert' ? 'alert' : 'status'))
    return { role }
  },
})
</script>

<template>
  <section
    class="backend-not-ready"
    :class="{ 'backend-not-ready--alert': severity === 'alert' }"
    :role="role"
    aria-live="polite"
  >
    <span class="backend-not-ready__icon" aria-hidden="true">⌛</span>
    <div class="backend-not-ready__body">
      <p class="backend-not-ready__title">
        <span class="backend-not-ready__feature">{{ feature }}</span>
        尚未上线，等待后端
        <span class="backend-not-ready__waiting">{{ waitingFor }}</span>
        完成后启用。
      </p>
      <p v-if="description" class="backend-not-ready__description">
        {{ description }}
      </p>
    </div>
  </section>
</template>

<style scoped>
.backend-not-ready {
  display: flex;
  gap: var(--space-sm);
  align-items: flex-start;
  padding: var(--space-md) var(--space-lg);
  background-color: var(--color-surface-2);
  border: 1px dashed var(--color-hairline-strong);
  border-radius: var(--rounded-lg);
  color: var(--color-ink-muted);
}

.backend-not-ready--alert {
  background-color: var(--color-risk-medium-bg);
  border-color: var(--color-risk-medium);
  color: var(--color-risk-medium);
}

.backend-not-ready__icon {
  font-size: var(--font-body-lg-size);
  line-height: 1;
  margin-top: 2px;
}

.backend-not-ready__body {
  display: flex;
  flex-direction: column;
  gap: var(--space-xxs);
}

.backend-not-ready__title {
  margin: 0;
  font-size: var(--font-body-size);
  line-height: var(--font-body-line);
}

.backend-not-ready__feature,
.backend-not-ready__waiting {
  color: var(--color-ink);
  font-weight: 500;
}

.backend-not-ready--alert .backend-not-ready__feature,
.backend-not-ready--alert .backend-not-ready__waiting {
  color: inherit;
}

.backend-not-ready__description {
  margin: 0;
  color: var(--color-ink-subtle);
  font-size: var(--font-body-sm-size);
  line-height: var(--font-body-sm-line);
}

.backend-not-ready--alert .backend-not-ready__description {
  color: inherit;
  opacity: 0.85;
}
</style>
