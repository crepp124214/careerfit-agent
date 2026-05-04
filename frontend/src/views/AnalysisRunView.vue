<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAvailabilityStore } from '@/stores/availability'
import { useJobsStore } from '@/stores/jobs'
import { useResumesStore } from '@/stores/resumes'
import { createAnalysis } from '@/api/analysis'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'
import AppButton from '@/components/common/AppButton.vue'

const router = useRouter()
const availability = useAvailabilityStore()
const jobs = useJobsStore()
const resumes = useResumesStore()

const isUnavailable = computed(() => availability.states.analysis === 'unavailable')
const canLaunch = computed(
  () =>
    !isUnavailable.value &&
    !!jobs.selectedId &&
    !!resumes.selectedId,
)

const launching = ref(false)
const error = ref('')

onMounted(() => {
  availability.probe()
  if (availability.states.jobs !== 'unavailable' && jobs.list.length === 0) {
    jobs.load()
  }
  if (availability.states.resumes !== 'unavailable' && resumes.list.length === 0) {
    resumes.load()
  }
})

async function launch() {
  if (!jobs.selectedId || !resumes.selectedId) return
  launching.value = true
  error.value = ''

  const res = await createAnalysis({
    job_id: jobs.selectedId,
    resume_id: resumes.selectedId,
  })

  if (!res.ok) {
    error.value = res.message
    launching.value = false
    return
  }

  router.push({ name: 'report', params: { taskId: res.data.id } })
}
</script>

<template>
  <section class="analysis-run" role="main" aria-label="启动分析">
    <h1 class="analysis-run__title">启动匹配分析</h1>

    <BackendNotReadyNotice
      v-if="isUnavailable"
      feature="匹配分析"
      waitingFor="analysis API"
    />

    <div v-else class="analysis-run__body">
      <div class="analysis-run__selection">
        <div class="analysis-run__field">
          <span class="analysis-run__label">目标岗位</span>
          <span class="analysis-run__value">
            {{ jobs.selectedJob?.title ?? '未选择' }}
          </span>
        </div>
        <div class="analysis-run__field">
          <span class="analysis-run__label">简历版本</span>
          <span class="analysis-run__value">
            {{ resumes.selectedResume?.candidate_name ?? '未选择' }}
          </span>
        </div>
      </div>

      <p v-if="!jobs.selectedId || !resumes.selectedId" class="analysis-run__hint">
        请先在工作台选择目标岗位和简历版本。
      </p>

      <p v-if="error" class="analysis-run__error">{{ error }}</p>

      <AppButton
        variant="primary"
        :disabled="!canLaunch"
        :loading="launching"
        @click="launch"
      >
        开始分析
      </AppButton>
    </div>
  </section>
</template>

<style scoped>
.analysis-run {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  max-width: 640px;
}

.analysis-run__title {
  margin: 0;
  font-size: var(--font-headline-size);
  font-weight: var(--font-headline-weight);
  line-height: var(--font-headline-line);
}

.analysis-run__body {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.analysis-run__selection {
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.analysis-run__field {
  display: flex;
  gap: var(--space-sm);
}

.analysis-run__label {
  font-size: var(--font-body-size);
  color: var(--color-ink-subtle);
  min-width: 80px;
}

.analysis-run__value {
  font-size: var(--font-body-size);
  font-weight: 500;
  color: var(--color-ink);
}

.analysis-run__hint {
  margin: 0;
  color: var(--color-risk-medium);
  font-size: var(--font-body-sm-size);
}

.analysis-run__error {
  margin: 0;
  color: var(--color-risk-high);
  font-size: var(--font-body-sm-size);
}
</style>
