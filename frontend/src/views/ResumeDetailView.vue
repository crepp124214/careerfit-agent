<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAvailabilityStore } from '@/stores/availability'
import { useResumesStore } from '@/stores/resumes'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'
import LoadingCard from '@/components/feedback/LoadingCard.vue'
import AppButton from '@/components/common/AppButton.vue'
import { formatDate } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const availability = useAvailabilityStore()
const resumes = useResumesStore()

const resumeId = ref(Number(route.params.id))
const resume = ref<Awaited<ReturnType<typeof resumes.loadOne>> | null>(null)
const loading = ref(false)

async function load() {
  if (availability.states.resumes !== 'ready') return
  loading.value = true
  resume.value = await resumes.loadOne(resumeId.value)
  loading.value = false
}

watch(() => route.params.id, (id) => {
  if (typeof id === 'string') {
    resumeId.value = Number(id)
    load()
  }
}, { immediate: true })
</script>

<template>
  <section class="resume-detail-view" role="main" aria-label="简历详情">
    <AppButton variant="tertiary" @click="router.back()">← 返回</AppButton>

    <BackendNotReadyNotice
      v-if="availability.states.resumes === 'unavailable'"
      feature="简历详情"
      waitingFor="resumes API"
    />

    <LoadingCard v-else-if="loading" title="加载简历详情中…" />

    <div v-else-if="resume" class="resume-detail-view__card">
      <h1 class="resume-detail-view__title">{{ resume.candidate_name }} — {{ resume.version_label }}</h1>
      <div v-if="resume.raw_text" class="resume-detail-view__content">
        <h2 class="resume-detail-view__section-title">简历内容</h2>
        <pre class="resume-detail-view__content-text">{{ resume.raw_text }}</pre>
      </div>
      <p class="resume-detail-view__meta">创建于 {{ formatDate(resume.created_at) }}</p>
    </div>

    <p v-else class="resume-detail-view__not-found">未找到该简历。</p>
  </section>
</template>

<style scoped>
.resume-detail-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  max-width: 960px;
}

.resume-detail-view__card {
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.resume-detail-view__title {
  margin: 0;
  font-size: var(--font-headline-size);
  font-weight: var(--font-headline-weight);
  line-height: var(--font-headline-line);
}

.resume-detail-view__section-title {
  margin: 0;
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
}

.resume-detail-view__content-text {
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
  max-height: 600px;
  overflow: auto;
}

.resume-detail-view__meta {
  margin: 0;
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

.resume-detail-view__not-found {
  color: var(--color-ink-subtle);
}
</style>
