<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAvailabilityStore } from '@/stores/availability'
import { useJobsStore } from '@/stores/jobs'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'
import LoadingCard from '@/components/feedback/LoadingCard.vue'
import AppButton from '@/components/common/AppButton.vue'

const route = useRoute()
const router = useRouter()
const availability = useAvailabilityStore()
const jobs = useJobsStore()

const jobId = ref(route.params.id as string)
const job = ref<Awaited<ReturnType<typeof jobs.loadOne>> | null>(null)
const loading = ref(false)

async function load() {
  if (availability.states.jobs !== 'ready') return
  loading.value = true
  job.value = await jobs.loadOne(jobId.value)
  loading.value = false
}

watch(() => route.params.id, (id) => {
  if (typeof id === 'string') {
    jobId.value = id
    load()
  }
}, { immediate: true })
</script>

<template>
  <section class="job-detail-view" role="main" aria-label="岗位详情">
    <AppButton variant="tertiary" @click="router.back()">← 返回</AppButton>

    <BackendNotReadyNotice
      v-if="availability.states.jobs === 'unavailable'"
      feature="岗位详情"
      waitingFor="jobs API"
    />

    <LoadingCard v-else-if="loading" title="加载岗位详情中…" />

    <div v-else-if="job" class="job-detail-view__card">
      <h1 class="job-detail-view__title">{{ job.title }}</h1>
      <p v-if="job.company" class="job-detail-view__company">{{ job.company }}</p>
      <div v-if="job.jdText" class="job-detail-view__jd">
        <h2 class="job-detail-view__section-title">职位描述</h2>
        <pre class="job-detail-view__jd-text">{{ job.jdText }}</pre>
      </div>
      <p class="job-detail-view__meta">创建于 {{ job.createdAt }}</p>
    </div>

    <p v-else class="job-detail-view__not-found">未找到该岗位。</p>
  </section>
</template>

<style scoped>
.job-detail-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  max-width: 960px;
}

.job-detail-view__card {
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.job-detail-view__title {
  margin: 0;
  font-size: var(--font-headline-size);
  font-weight: var(--font-headline-weight);
  line-height: var(--font-headline-line);
}

.job-detail-view__company {
  margin: 0;
  font-size: var(--font-body-lg-size);
  color: var(--color-ink-muted);
}

.job-detail-view__section-title {
  margin: 0;
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
}

.job-detail-view__jd-text {
  margin: 0;
  padding: var(--space-md);
  background-color: var(--color-surface-2);
  border-radius: var(--rounded-sm);
  font-family: var(--font-family-mono);
  font-size: var(--font-mono-size);
  line-height: var(--font-mono-line);
  color: var(--color-ink-muted);
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 400px;
  overflow: auto;
}

.job-detail-view__meta {
  margin: 0;
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

.job-detail-view__not-found {
  color: var(--color-ink-subtle);
}
</style>
