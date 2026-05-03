<script setup lang="ts">
import { computed } from 'vue'

type Tone = 'neutral' | 'info' | 'risk-high' | 'risk-medium' | 'risk-low'

const props = withDefaults(
  defineProps<{
    tone?: Tone
    label?: string
  }>(),
  {
    tone: 'neutral',
    label: '',
  },
)

const className = computed(() => `status-badge status-badge--${props.tone}`)
</script>

<template>
  <span :class="className">
    <slot>{{ props.label }}</slot>
  </span>
</template>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: var(--rounded-pill);
  font-size: var(--font-caption-size);
  line-height: var(--font-caption-line);
  letter-spacing: var(--font-caption-letter);
  background-color: var(--color-surface-2);
  color: var(--color-ink-muted);
}

.status-badge--info {
  background-color: var(--color-info-trace-bg);
  color: var(--color-info-trace);
}

.status-badge--risk-high {
  background-color: var(--color-risk-high-bg);
  color: var(--color-risk-high);
}

.status-badge--risk-medium {
  background-color: var(--color-risk-medium-bg);
  color: var(--color-risk-medium);
}

.status-badge--risk-low {
  background-color: var(--color-risk-low-bg);
  color: var(--color-risk-low);
}
</style>
