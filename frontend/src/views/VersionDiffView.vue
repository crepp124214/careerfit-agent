<script setup lang="ts">
import { computed } from 'vue'
import { useAvailabilityStore } from '@/stores/availability'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'

const availability = useAvailabilityStore()
const isUnavailable = computed(() => availability.states.resumes === 'unavailable')
</script>

<template>
  <section class="diff-view" role="main" aria-label="版本对比">
    <h1 class="diff-view__title">版本对比</h1>

    <BackendNotReadyNotice
      v-if="isUnavailable"
      feature="版本对比"
      waitingFor="简历版本 diff 接口"
    />

    <template v-else>
      <div class="diff-view__selectors">
        <div class="diff-view__select-group">
          <label class="diff-view__label" for="diff-baseline">基线版本</label>
          <select id="diff-baseline" class="diff-view__select" disabled>
            <option>选择简历版本</option>
          </select>
        </div>
        <div class="diff-view__select-group">
          <label class="diff-view__label" for="diff-target">对比版本</label>
          <select id="diff-target" class="diff-view__select" disabled>
            <option>选择简历版本</option>
          </select>
        </div>
      </div>

      <div class="diff-view__placeholder">
        <p class="diff-view__placeholder-text">版本 diff 功能尚未上线，等待后端简历版本 diff 接口完成。</p>
      </div>
    </template>
  </section>
</template>

<style scoped>
.diff-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  max-width: 960px;
}

.diff-view__title {
  margin: 0;
  font-size: var(--font-headline-size);
  font-weight: var(--font-headline-weight);
  line-height: var(--font-headline-line);
}

.diff-view__selectors {
  display: flex;
  gap: var(--space-lg);
}

.diff-view__select-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-xxs);
  flex: 1;
}

.diff-view__label {
  font-size: var(--font-body-size);
  color: var(--color-ink-subtle);
}

.diff-view__select {
  font-family: var(--font-family-sans);
  font-size: var(--font-body-size);
  padding: var(--space-xs) var(--space-sm);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-md);
  background-color: var(--color-surface-1);
  color: var(--color-ink);
}

.diff-view__placeholder {
  background-color: var(--color-surface-1);
  border: 1px dashed var(--color-hairline-strong);
  border-radius: var(--rounded-lg);
  padding: var(--space-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.diff-view__placeholder-text {
  margin: 0;
  color: var(--color-ink-muted);
  font-size: var(--font-body-size);
}
</style>
