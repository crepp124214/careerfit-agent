<script setup lang="ts">
import { useAvailabilityStore } from '@/stores/availability'

const store = useAvailabilityStore()
</script>

<template>
  <footer class="status-bar" role="contentinfo">
    <div class="status-bar__left">
      <span
        class="status-bar__dot"
        :class="{
          'status-bar__dot--ready': store.allReady,
          'status-bar__dot--partial': store.anyUnavailable && !store.allReady,
          'status-bar__dot--offline': !store.allReady && !store.anyUnavailable,
        }"
        aria-hidden="true"
      />
      <span class="status-bar__label">{{ store.statusLabel }}</span>
    </div>
    <div class="status-bar__right">
      <span class="status-bar__hint">本会话中展示的 JD 与简历文本已脱敏，仅供个人使用。</span>
    </div>
  </footer>
</template>

<style scoped>
.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-md);
  padding: 6px var(--space-lg);
  border-top: 1px solid var(--color-hairline);
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
  background-color: var(--color-canvas);
}

.status-bar__left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-bar__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--color-ink-tertiary);
}

.status-bar__dot--ready {
  background-color: var(--color-risk-low);
}

.status-bar__dot--partial {
  background-color: var(--color-risk-medium);
}

.status-bar__dot--offline {
  background-color: var(--color-risk-high);
}

.status-bar__label {
  color: var(--color-ink-muted);
}

.status-bar__hint {
  opacity: 0.7;
}
</style>
