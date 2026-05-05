<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAvailabilityStore } from '@/stores/availability'
import { useJobsStore } from '@/stores/jobs'
import { useResumesStore } from '@/stores/resumes'
import WorkbenchContextPanel from '@/components/workbench/WorkbenchContextPanel.vue'
import AnalysisActionPanel from '@/components/workbench/AnalysisActionPanel.vue'
import OnboardingGuide from '@/components/workbench/OnboardingGuide.vue'
import JobSelector from '@/components/workbench/JobSelector.vue'
import ResumeSelector from '@/components/workbench/ResumeSelector.vue'

const router = useRouter()
const availability = useAvailabilityStore()
const jobs = useJobsStore()
const resumes = useResumesStore()

const hasJobs = computed(() => jobs.list.length > 0)
const hasResumes = computed(() => resumes.list.length > 0)
const showOnboarding = computed(() => !hasJobs.value || !hasResumes.value)

function goToJobs() {
  router.push({ name: 'jobs' })
}

function goToResumes() {
  router.push({ name: 'resumes' })
}

onMounted(async () => {
  await availability.probe()
  if (availability.states.jobs !== 'unavailable') {
    await jobs.load()
    if (jobs.list.length > 0 && !jobs.selectedId) {
      const firstJob = jobs.list[0]
      if (firstJob) {
        jobs.select(firstJob.id)
      }
    }
  }
  if (availability.states.resumes !== 'unavailable') {
    await resumes.load()
    if (resumes.list.length > 0 && !resumes.selectedId) {
      const firstResume = resumes.list[0]
      if (firstResume) {
        resumes.select(firstResume.id)
      }
    }
  }
})
</script>

<template>
  <div class="workbench-layout">
    <main class="workbench-main" role="main" aria-label="个人求职成长工作台">
      <header class="workbench-header animate-in">
        <div class="workbench-header__text">
          <h1 class="workbench-title">求职工作台</h1>
          <p class="workbench-subtitle">选择目标岗位与简历版本，开始匹配分析</p>
        </div>
      </header>

      <OnboardingGuide v-if="showOnboarding" class="workbench-onboarding animate-in animate-in-stagger-1" />

      <div v-else class="workbench-columns animate-in animate-in-stagger-1">
        <section class="workbench-columns__selectors" aria-label="工作台选择">
          <JobSelector @create="goToJobs" />
          <ResumeSelector @create="goToResumes" />
        </section>
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
  padding: var(--space-xl);
  max-width: 1440px;
  margin: 0 auto;
  width: 100%;
}

.workbench-header {
  flex-shrink: 0;
}

.workbench-header__text {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.workbench-title {
  margin: 0;
  font-size: var(--font-display-md-size);
  font-weight: var(--font-display-md-weight);
  line-height: var(--font-display-md-line);
  letter-spacing: var(--font-display-md-letter);
  color: var(--color-ink);
}

.workbench-subtitle {
  margin: 0;
  font-size: var(--font-body-lg-size);
  color: var(--color-ink-subtle);
  line-height: var(--font-body-lg-line);
}

.workbench-columns {
  display: grid;
  grid-template-columns: minmax(280px, 320px) minmax(0, 1fr) minmax(320px, 380px);
  gap: var(--space-lg);
  flex: 1;
  align-items: start;
}

.workbench-onboarding {
  flex-shrink: 0;
}

.workbench-columns__selectors {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  min-width: 0;
}

.workbench-columns__context {
  min-width: 0;
}

.workbench-columns__action {
  min-width: 0;
}

@media (max-width: 1024px) {
  .workbench-columns {
    grid-template-columns: minmax(260px, 320px) minmax(0, 1fr);
  }

  .workbench-columns__action {
    grid-column: 1 / -1;
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

  .workbench-subtitle {
    font-size: var(--font-body-size);
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
