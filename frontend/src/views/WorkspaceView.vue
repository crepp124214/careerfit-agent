<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAvailabilityStore } from '@/stores/availability'
import { useJobsStore } from '@/stores/jobs'
import { useResumesStore } from '@/stores/resumes'
import { useAnalysesStore } from '@/stores/analyses'
import NextBestActionCallout from '@/components/workbench/NextBestActionCallout.vue'
import JobSelector from '@/components/workbench/JobSelector.vue'
import ResumeSelector from '@/components/workbench/ResumeSelector.vue'
import AnalysisLauncher from '@/components/workbench/AnalysisLauncher.vue'

const router = useRouter()
const availability = useAvailabilityStore()
const jobs = useJobsStore()
const resumes = useResumesStore()
const analyses = useAnalysesStore()

const calloutState = computed(() => {
  if (analyses.report) return 'ready' as const
  if (jobs.selectedId && resumes.selectedId) return 'ready' as const
  return 'empty' as const
})

const calloutHeadline = computed(() => {
  if (analyses.report) return analyses.report.nextBestAction?.headline ?? '查看最新报告'
  if (jobs.selectedId && resumes.selectedId) return '开始匹配分析'
  return ''
})

const calloutActionLabel = computed(() => {
  if (analyses.report) return analyses.report.nextBestAction?.actionLabel ?? '查看学习任务'
  if (jobs.selectedId && resumes.selectedId) return '开始分析'
  return ''
})

const calloutCtaTo = computed(() => {
  if (analyses.report) return analyses.report.nextBestAction?.ctaTo ?? '/learning'
  return ''
})

function onCalloutAction() {
  if (analyses.report) {
    router.push(`/reports/${analyses.report.taskId}`)
  }
}

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
    <h1 class="workspace-view__title animate-in">个人求职成长工作台</h1>

    <NextBestActionCallout
      class="animate-in animate-in-stagger-1"
      :state="calloutState"
      :headline="calloutHeadline"
      :action-label="calloutActionLabel"
      :cta-to="calloutCtaTo"
      @action="onCalloutAction"
    />

    <div class="workspace-view__grid animate-in animate-in-stagger-2">
      <JobSelector />
      <ResumeSelector />
    </div>

    <AnalysisLauncher class="animate-in animate-in-stagger-3" />
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
