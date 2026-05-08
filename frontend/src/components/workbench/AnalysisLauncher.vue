<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAvailabilityStore } from '@/stores/availability'
import { useJobsStore } from '@/stores/jobs'
import { useResumesStore } from '@/stores/resumes'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'
import AppButton from '@/components/common/AppButton.vue'

const availability = useAvailabilityStore()
const jobs = useJobsStore()
const resumes = useResumesStore()

type AnalysisMode = 'lite_analysis' | 'full_analysis'

const selectedMode = ref<AnalysisMode>('full_analysis')

const modeInfo: Record<AnalysisMode, { label: string; desc: string; time: string }> = {
  lite_analysis: {
    label: '快速分析',
    desc: '仅匹配度 + 能力缺口 + Next Best Action',
    time: '~15s',
  },
  full_analysis: {
    label: '完整分析',
    desc: '匹配度 + 缺口 + 简历优化 + 面试题 + 准备计划',
    time: '~45s',
  },
}

const canLaunch = computed(() =>
  availability.states.analysis === 'ready'
  && jobs.selectedId !== null
  && resumes.selectedId !== null,
)

const isUnavailable = computed(() => availability.states.analysis === 'unavailable')

const emit = defineEmits<{
  (e: 'launch', mode: AnalysisMode): void
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
        <strong>{{ resumes.selectedResume?.candidate_name ?? '未选择' }}</strong>
      </p>

      <fieldset class="analysis-launcher__mode">
        <legend class="analysis-launcher__mode-legend">分析模式</legend>
        <label
          v-for="(info, mode) in modeInfo"
          :key="mode"
          class="analysis-launcher__mode-option"
          :class="{ 'analysis-launcher__mode-option--active': selectedMode === mode }"
        >
          <input
            type="radio"
            name="analysis-mode"
            :value="mode"
            v-model="selectedMode"
            class="analysis-launcher__mode-radio"
          />
          <span class="analysis-launcher__mode-content">
            <span class="analysis-launcher__mode-label">{{ info.label }}</span>
            <span class="analysis-launcher__mode-desc">{{ info.desc }}</span>
            <span class="analysis-launcher__mode-time">{{ info.time }}</span>
          </span>
        </label>
      </fieldset>

      <AppButton
        variant="primary"
        :disabled="!canLaunch"
        @click="emit('launch', selectedMode)"
      >
        开始{{ modeInfo[selectedMode].label }}
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

.analysis-launcher__mode {
  border: none;
  margin: var(--space-sm) 0;
  padding: 0;
}

.analysis-launcher__mode-legend {
  font-size: var(--font-body-sm-size);
  font-weight: 500;
  color: var(--color-ink-subtle);
  margin-bottom: var(--space-xs);
}

.analysis-launcher__mode-option {
  display: flex;
  align-items: flex-start;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  margin-bottom: var(--space-xs);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-md);
  cursor: pointer;
  transition:
    border-color var(--motion-duration-fast) var(--motion-easing-standard),
    background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.analysis-launcher__mode-option:hover {
  background-color: var(--color-surface-2);
}

.analysis-launcher__mode-option--active {
  border-color: var(--color-primary);
  background-color: var(--color-surface-2);
}

.analysis-launcher__mode-radio {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
}

.analysis-launcher__mode-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.analysis-launcher__mode-label {
  font-size: var(--font-body-size);
  font-weight: 600;
  color: var(--color-ink);
}

.analysis-launcher__mode-desc {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

.analysis-launcher__mode-time {
  font-size: var(--font-caption-size);
  color: var(--color-primary);
  font-weight: 500;
}
</style>
