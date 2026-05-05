<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useJobsStore } from '@/stores/jobs'
import { useResumesStore } from '@/stores/resumes'
import { useAnalysesStore } from '@/stores/analyses'
import StatusBadge from '@/components/common/StatusBadge.vue'

const router = useRouter()
const jobs = useJobsStore()
const resumes = useResumesStore()
const analyses = useAnalysesStore()

const selectedJob = computed(() => {
  if (!jobs.selectedId) return null
  return jobs.list.find((j: { id: number }) => j.id === jobs.selectedId) ?? null
})

const selectedResume = computed(() => {
  if (!resumes.selectedId) return null
  return resumes.list.find((r: { id: number }) => r.id === resumes.selectedId) ?? null
})

const latestReport = computed(() => analyses.report)

const gapCount = computed(() => {
  if (!latestReport.value) return 0
  return latestReport.value.dimensions.filter(d => d.score < 50).length
})

const hasSelection = computed(() => selectedJob.value || selectedResume.value)
</script>

<template>
  <section class="context-panel" aria-label="任务上下文">
    <h2 class="context-panel__title">任务上下文</h2>

    <div v-if="!hasSelection" class="context-panel__empty">
      <p class="context-panel__empty-text">还没有选择目标岗位或简历版本</p>
      <p class="context-panel__empty-hint">选择一个岗位和简历版本，系统才能进行匹配分析。</p>
    </div>

    <div v-else class="context-panel__cards">
      <article v-if="selectedJob" class="context-card">
        <header class="context-card__header">
          <h3 class="context-card__label">目标岗位</h3>
          <StatusBadge v-if="selectedJob.profile?.job_family" :label="String(selectedJob.profile.job_family)" />
        </header>
        <p class="context-card__name">{{ selectedJob.title }}</p>
        <button
          type="button"
          class="context-card__action"
          @click="router.push({ name: 'jobs' })"
        >
          查看详情
        </button>
      </article>

      <article v-if="selectedResume" class="context-card">
        <header class="context-card__header">
          <h3 class="context-card__label">简历版本</h3>
        </header>
        <p class="context-card__name">{{ selectedResume.version_label }}</p>
        <p v-if="selectedResume.candidate_name" class="context-card__meta">{{ selectedResume.candidate_name }}</p>
        <button
          type="button"
          class="context-card__action"
          @click="router.push({ name: 'resumes' })"
        >
          查看详情
        </button>
      </article>

      <article v-if="latestReport" class="context-card context-card--gaps">
        <h3 class="context-card__label">能力缺口</h3>
        <p class="context-card__gap-count">{{ gapCount }} 项待补齐</p>
      </article>
    </div>
  </section>
</template>

<style scoped>
.context-panel {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.context-panel__title {
  margin: 0;
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
  line-height: var(--font-card-title-line);
  color: var(--color-ink);
}

.context-panel__empty {
  padding: var(--space-lg);
  background-color: var(--color-surface-1);
  border: 1px dashed var(--color-hairline);
  border-radius: var(--rounded-lg);
}

.context-panel__empty-text {
  margin: 0 0 var(--space-xs);
  font-size: var(--font-body-size);
  color: var(--color-ink-muted);
}

.context-panel__empty-hint {
  margin: 0;
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-subtle);
}

.context-panel__cards {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.context-card {
  padding: var(--space-md);
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  box-shadow: var(--shadow-sm);
  transition:
    border-color var(--motion-duration-fast) var(--motion-easing-standard),
    box-shadow var(--motion-duration-fast) var(--motion-easing-standard);
}

.context-card:hover {
  border-color: var(--color-hairline-strong);
  box-shadow: var(--shadow-md);
}

.context-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-xs);
}

.context-card__label {
  margin: 0;
  font-size: var(--font-caption-size);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: var(--color-ink-subtle);
}

.context-card__name {
  margin: 0;
  font-size: var(--font-body-size);
  font-weight: 500;
  color: var(--color-ink);
}

.context-card__meta {
  margin: 0;
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-muted);
}

.context-card__action {
  align-self: flex-start;
  margin-top: var(--space-xs);
  padding: 6px 12px;
  background-color: var(--color-surface-2);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-sm);
  color: var(--color-ink-muted);
  font-size: var(--font-caption-size);
  cursor: pointer;
  transition: background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.context-card__action:hover {
  background-color: var(--color-surface-3);
}

.context-card--gaps {
  background-color: var(--color-surface-2);
}

.context-card__gap-count {
  margin: 0;
  font-size: var(--font-body-size);
  font-weight: 500;
  color: var(--color-ink);
}
</style>
