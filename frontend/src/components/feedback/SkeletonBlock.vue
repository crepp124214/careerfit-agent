<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    width?: string
    height?: string
    rounded?: string
  }>(),
  {
    width: '100%',
    height: '12px',
    rounded: 'var(--rounded-sm)',
  },
)

const style = computed(() => ({
  width: props.width,
  height: props.height,
  borderRadius: props.rounded,
}))
</script>

<template>
  <span class="skeleton-block" :style="style" aria-hidden="true" />
</template>

<style scoped>
.skeleton-block {
  display: inline-block;
  background: linear-gradient(
    90deg,
    var(--color-surface-2) 0%,
    var(--color-surface-3) 50%,
    var(--color-surface-2) 100%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.4s ease-in-out infinite;
}

@keyframes skeleton-shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .skeleton-block {
    animation: none;
    background: var(--color-surface-2);
  }
}
</style>
