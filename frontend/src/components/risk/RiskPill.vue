<script setup lang="ts">
import { computed } from 'vue'

type Level = 'high' | 'medium' | 'low'

const props = withDefaults(
  defineProps<{
    level: Level
    label?: string
  }>(),
  {
    label: '',
  },
)

const DEFAULT_LABELS: Record<Level, string> = {
  high: '高风险',
  medium: '需关注',
  low: '通过',
}

const visibleLabel = computed(() => {
  return props.label.length > 0 ? props.label : DEFAULT_LABELS[props.level]
})

const className = computed(() => `risk-pill risk-pill--${props.level}`)
</script>

<template>
  <span :class="className" :aria-label="visibleLabel" role="status">
    <span class="risk-pill__dot" aria-hidden="true" />
    <span class="risk-pill__text">{{ visibleLabel }}</span>
  </span>
</template>

<style scoped>
.risk-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 2px 10px;
  border-radius: var(--rounded-pill);
  font-size: var(--font-caption-size);
  line-height: var(--font-caption-line);
  letter-spacing: var(--font-caption-letter);
  white-space: nowrap;
  min-height: 22px;
}

.risk-pill__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: currentColor;
}

.risk-pill--high {
  background-color: var(--color-risk-high-bg);
  color: var(--color-risk-high);
}

.risk-pill--medium {
  background-color: var(--color-risk-medium-bg);
  color: var(--color-risk-medium);
}

.risk-pill--low {
  background-color: var(--color-risk-low-bg);
  color: var(--color-risk-low);
}

@media (forced-colors: active) {
  .risk-pill {
    border: 1px solid CanvasText;
  }
}
</style>
