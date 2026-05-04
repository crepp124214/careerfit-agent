<script setup lang="ts">
import { onMounted } from 'vue'
import { useAvailabilityStore } from '@/stores/availability'
import { useJobsStore } from '@/stores/jobs'
import { useResumesStore } from '@/stores/resumes'
import WorkbenchContextPanel from '@/components/workbench/WorkbenchContextPanel.vue'
import AnalysisActionPanel from '@/components/workbench/AnalysisActionPanel.vue'

const availability = useAvailabilityStore()
const jobs = useJobsStore()
const resumes = useResumesStore()

onMounted(async () => {
  await availability.probe()
  if (availability.states.jobs !== 'unavailable') {
    jobs.load()
  }
  if (availability.states.resumes !== 'unavailable') {
    resumes.load()
  }
})
</script>

<template>
  <div class="workbench-layout">
    <main class="workbench-main" role="main" aria-label="个人求职成长工作台">
      <header class="workbench-header">
        <h1 class="workbench-title">个人求职成长工作台</h1>
      </header>

      <div class="workbench-columns">
        <WorkbenchContextPanel class="workbench-columns__context" />
        <AnalysisActionPanel class="workbench-columns__action" />
      </div>
    </main>
  </div>
</template>

<style scoped>
.workbench-layout {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.workbench-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  padding: var(--space-lg);
  max-width: 1440px;
  margin: 0 auto;
  width: 100%;
}

.workbench-header {
  flex-shrink: 0;
}

.workbench-title {
  margin: 0;
  font-size: var(--font-headline-size);
  font-weight: var(--font-headline-weight);
  line-height: var(--font-headline-line);
  letter-spacing: var(--font-headline-letter);
  color: var(--color-ink);
}

.workbench-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-lg);
  flex: 1;
}

.workbench-columns__context {
  min-width: 0;
}

.workbench-columns__action {
  min-width: 0;
}

@media (max-width: 1024px) {
  .workbench-columns {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .workbench-main {
    padding: var(--space-md);
    gap: var(--space-md);
  }

  .workbench-title {
    font-size: 28px;
    letter-spacing: -0.5px;
  }
}

@media (max-width: 480px) {
  .workbench-main {
    padding: var(--space-sm);
    gap: var(--space-sm);
  }

  .workbench-title {
    font-size: 24px;
  }
}
</style>
