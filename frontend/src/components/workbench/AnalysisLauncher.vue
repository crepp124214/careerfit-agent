<script setup lang="ts">
import { computed } from 'vue'
import { useAvailabilityStore } from '@/stores/availability'
import { useJobsStore } from '@/stores/jobs'
import { useResumesStore } from '@/stores/resumes'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'
import AppButton from '@/components/common/AppButton.vue'

const availability = useAvailabilityStore()
const jobs = useJobsStore()
const resumes = useResumesStore()

const canLaunch = computed(() =>
  availability.states.analysis === 'ready'
  && jobs.selectedId !== null
  && resumes.selectedId !== null,
)

const isUnavailable = computed(() => availability.states.analysis === 'unavailable')

const emit = defineEmits<{
  (e: 'launch'): void
}>()
</script>

<template>
  <section class="analysis-launcher" aria-label="启动分析">
    <h2 class="analysis-launcher__title">匹配分析</h2>

    <BackendNotReadyNotice
      v-if="isUnavailable"
      feature="匹配分析"
      waitingFor="analysis API"
    />

    <div v-else class="analysis-launcher__body">
      <p class="analysis-launcher__hint">
        已选岗位：
        <strong>{{ jobs.selectedJob?.title ?? '未选择' }}</strong>
      </p>
      <p class="analysis-launcher__hint">
        已选简历：
        <strong>{{ resumes.selectedResume?.name ?? '未选择' }}</strong>
      </p>
      <AppButton
        variant="primary"
        :disabled="!canLaunch"
        @click="emit('launch')"
      >
        开始分析
      </AppButton>
    </div>
  </section>
</template>

<style scoped>
.analysis-launcher {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  padding: var(--space-lg);
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--motion-duration-fast) var(--motion-easing-standard);
}

.analysis-launcher:hover {
  box-shadow: var(--shadow-md);
}

.analysis-launcher__title {
  margin: 0;
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
  line-height: var(--font-card-title-line);
  color: var(--color-ink);
}

.analysis-launcher__body {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.analysis-launcher__hint {
  margin: 0;
  font-size: var(--font-body-size);
  color: var(--color-ink-muted);
}

.analysis-launcher__hint strong {
  color: var(--color-ink);
  font-weight: 500;
}
</style>
