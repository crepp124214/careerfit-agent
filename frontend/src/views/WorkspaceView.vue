<script setup lang="ts">
import { onMounted } from 'vue'
import { useAvailabilityStore } from '@/stores/availability'
import NextBestActionCallout from '@/components/workbench/NextBestActionCallout.vue'
import JobSelector from '@/components/workbench/JobSelector.vue'
import ResumeSelector from '@/components/workbench/ResumeSelector.vue'
import AnalysisLauncher from '@/components/workbench/AnalysisLauncher.vue'

const availability = useAvailabilityStore()

onMounted(() => {
  availability.probe()
  if (availability.states.jobs === 'unknown') {
    availability.setCapability('jobs', 'unavailable')
  }
  if (availability.states.resumes === 'unknown') {
    availability.setCapability('resumes', 'unavailable')
  }
})
</script>

<template>
  <section role="main" aria-label="个人求职成长工作台" class="workspace-view">
    <h1 class="workspace-view__title">个人求职成长工作台</h1>

    <NextBestActionCallout
      state="empty"
      headline=""
      action-label=""
    />

    <div class="workspace-view__grid">
      <JobSelector />
      <ResumeSelector />
    </div>

    <AnalysisLauncher />
  </section>
</template>

<style scoped>
.workspace-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.workspace-view__title {
  margin: 0;
  font-size: var(--font-headline-size);
  font-weight: var(--font-headline-weight);
  line-height: var(--font-headline-line);
  letter-spacing: var(--font-headline-letter);
}

.workspace-view__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-lg);
}

@media (max-width: 768px) {
  .workspace-view__grid {
    grid-template-columns: 1fr;
  }
}
</style>
