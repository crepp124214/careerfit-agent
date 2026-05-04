<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAvailabilityStore } from '@/stores/availability'
import { useResumeDiffStore } from '@/stores/resumeDiff'
import { useResumesStore } from '@/stores/resumes'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'
import EmptyState from '@/components/feedback/EmptyState.vue'
import LoadingCard from '@/components/feedback/LoadingCard.vue'
import ErrorBanner from '@/components/feedback/ErrorBanner.vue'

const availability = useAvailabilityStore()
const diffStore = useResumeDiffStore()
const resumesStore = useResumesStore()

const isUnavailable = computed(() => availability.states.resumes === 'unavailable')
const isLoading = computed(() => diffStore.status === 'loading')
const isError = computed(() => diffStore.status === 'error')
const hasDiff = computed(() => diffStore.diff !== null)
const resumeOptions = computed(() => resumesStore.list)

const fromScoreDelta = computed(() => {
  const ctx = diffStore.scoreContext
  if (!ctx?.available || ctx.fromScore === undefined || ctx.toScore === undefined) return null
  return ctx.toScore - ctx.fromScore
})

const scoreDeltaText = computed(() => {
  const delta = fromScoreDelta.value
  if (delta === null) return null
  if (delta > 0) return `+${delta}`
  return String(delta)
})

const scoreDeltaClass = computed(() => {
  const delta = fromScoreDelta.value
  if (delta === null) return ''
  if (delta > 0) return 'diff-view__score-delta--up'
  if (delta < 0) return 'diff-view__score-delta--down'
  return 'diff-view__score-delta--same'
})

function handleFromChange(event: Event) {
  const target = event.target as HTMLSelectElement
  diffStore.setFromId(target.value || null)
}

function handleToChange(event: Event) {
  const target = event.target as HTMLSelectElement
  diffStore.setToId(target.value || null)
}

function handleCompare() {
  if (diffStore.hasValidSelection) {
    diffStore.load()
  }
}

function handleRetry() {
  diffStore.load()
}

onMounted(() => {
  if (!isUnavailable.value) {
    resumesStore.load()
    diffStore.clear()
  }
})
</script>

<template>
  <section class="diff-view" role="main" aria-label="版本对比">
    <h1 class="diff-view__title">版本对比</h1>

    <BackendNotReadyNotice
      v-if="isUnavailable"
      feature="版本对比"
      waitingFor="简历版本 diff 接口"
    />

    <template v-else>
      <div class="diff-view__selectors">
        <div class="diff-view__select-group">
          <label class="diff-view__label" for="diff-from">基线版本</label>
          <select
            id="diff-from"
            class="diff-view__select"
            :value="diffStore.fromId || ''"
            @change="handleFromChange"
          >
            <option value="">选择简历版本</option>
            <option v-for="r in resumeOptions" :key="r.id" :value="String(r.id)">
              {{ r.candidate_name }} — {{ r.version_label }}
            </option>
          </select>
        </div>
        <div class="diff-view__select-group">
          <label class="diff-view__label" for="diff-to">对比版本</label>
          <select
            id="diff-to"
            class="diff-view__select"
            :value="diffStore.toId || ''"
            @change="handleToChange"
          >
            <option value="">选择简历版本</option>
            <option v-for="r in resumeOptions" :key="r.id" :value="String(r.id)">
              {{ r.candidate_name }} — {{ r.version_label }}
            </option>
          </select>
        </div>
        <button
          class="diff-view__compare-btn"
          :disabled="!diffStore.hasValidSelection || isLoading"
          @click="handleCompare"
        >
          对比
        </button>
      </div>

      <div v-if="isLoading" class="diff-view__loading">
        <LoadingCard message="加载版本对比..." />
      </div>

      <ErrorBanner
        v-else-if="isError"
        :message="diffStore.error || '加载失败'"
        @retry="handleRetry"
      />

      <EmptyState
        v-else-if="!hasDiff && !diffStore.hasValidSelection"
        title="选择两个简历版本"
        description="请在上方选择两个不同的简历版本进行对比。"
      />

      <template v-else-if="hasDiff">
        <div class="diff-view__summary">
          <div class="diff-view__summary-item">
            <span class="diff-view__summary-label">新增行</span>
            <span class="diff-view__summary-value diff-view__summary-value--added">
              {{ diffStore.summary?.addedLines ?? 0 }}
            </span>
          </div>
          <div class="diff-view__summary-item">
            <span class="diff-view__summary-label">删除行</span>
            <span class="diff-view__summary-value diff-view__summary-value--removed">
              {{ diffStore.summary?.removedLines ?? 0 }}
            </span>
          </div>
          <div class="diff-view__summary-item">
            <span class="diff-view__summary-label">未变行</span>
            <span class="diff-view__summary-value">
              {{ diffStore.summary?.unchangedLines ?? 0 }}
            </span>
          </div>
        </div>

        <div v-if="diffStore.scoreContext?.available" class="diff-view__score-context">
          <span class="diff-view__score-label">分数变化</span>
          <span class="diff-view__score-from">{{ diffStore.scoreContext.fromScore }}</span>
          <span>→</span>
          <span class="diff-view__score-to">{{ diffStore.scoreContext.toScore }}</span>
          <span v-if="scoreDeltaText" class="diff-view__score-delta" :class="scoreDeltaClass">
            {{ scoreDeltaText }}
          </span>
        </div>
        <div v-else class="diff-view__score-context diff-view__score-context--unavailable">
          <span class="diff-view__score-unavailable">
            {{ diffStore.scoreContext?.reason || '暂无分析报告，无法展示分数变化' }}
          </span>
        </div>

        <div class="diff-view__diff">
          <div
            v-for="(section, index) in diffStore.sections"
            :key="index"
            class="diff-view__line"
            :class="`diff-view__line--${section.type}`"
          >
            <span class="diff-view__line-num">
              <template v-if="section.type === 'removed'">{{ section.oldLine }}</template>
              <template v-else-if="section.type === 'added'">{{ section.newLine }}</template>
              <template v-else>{{ section.oldLine }}</template>
            </span>
            <span class="diff-view__line-type">
              <template v-if="section.type === 'added'">新增</template>
              <template v-else-if="section.type === 'removed'">删除</template>
            </span>
            <span class="diff-view__line-text">{{ section.text }}</span>
          </div>
        </div>
      </template>
    </template>
  </section>
</template>

<style scoped>
.diff-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  max-width: 960px;
}

.diff-view__title {
  margin: 0;
  font-size: var(--font-headline-size);
  font-weight: var(--font-headline-weight);
  line-height: var(--font-headline-line);
}

.diff-view__selectors {
  display: flex;
  gap: var(--space-md);
  align-items: flex-end;
}

.diff-view__select-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-xxs);
  flex: 1;
}

.diff-view__label {
  font-size: var(--font-body-size-sm);
  color: var(--color-ink-subtle);
}

.diff-view__select {
  font-family: var(--font-family-sans);
  font-size: var(--font-body-size);
  padding: var(--space-xs) var(--space-sm);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-md);
  background-color: var(--color-surface-1);
  color: var(--color-ink);
}

.diff-view__compare-btn {
  font-family: var(--font-family-sans);
  font-size: var(--font-button-size);
  font-weight: var(--font-button-weight);
  padding: var(--space-xs) var(--space-lg);
  border: none;
  border-radius: var(--rounded-md);
  background-color: var(--color-primary);
  color: white;
  cursor: pointer;
  transition: background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.diff-view__compare-btn:disabled {
  background-color: var(--color-ink-muted);
  cursor: not-allowed;
}

.diff-view__compare-btn:not(:disabled):hover {
  background-color: var(--color-primary-hover);
}

.diff-view__loading {
  display: flex;
  justify-content: center;
  padding: var(--space-xl);
}

.diff-view__summary {
  display: flex;
  gap: var(--space-xl);
  padding: var(--space-md);
  background-color: var(--color-surface-1);
  border-radius: var(--rounded-lg);
}

.diff-view__summary-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-xxs);
}

.diff-view__summary-label {
  font-size: var(--font-body-size-sm);
  color: var(--color-ink-subtle);
}

.diff-view__summary-value {
  font-size: var(--font-display-size);
  font-weight: var(--font-display-weight);
  color: var(--color-ink);
}

.diff-view__summary-value--added {
  color: var(--color-success);
}

.diff-view__summary-value--removed {
  color: var(--color-risk-high);
}

.diff-view__score-context {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md);
  background-color: var(--color-surface-1);
  border-radius: var(--rounded-md);
  font-size: var(--font-body-size);
}

.diff-view__score-context--unavailable {
  color: var(--color-ink-subtle);
}

.diff-view__score-label {
  color: var(--color-ink-subtle);
}

.diff-view__score-from {
  font-weight: var(--font-body-weight-bold);
}

.diff-view__score-to {
  font-weight: var(--font-body-weight-bold);
}

.diff-view__score-delta {
  font-weight: var(--font-body-weight-bold);
  margin-left: var(--space-xs);
}

.diff-view__score-delta--up {
  color: var(--color-success);
}

.diff-view__score-delta--down {
  color: var(--color-risk-high);
}

.diff-view__score-delta--same {
  color: var(--color-ink-subtle);
}

.diff-view__score-unavailable {
  font-size: var(--font-body-size-sm);
}

.diff-view__diff {
  display: flex;
  flex-direction: column;
  gap: 1px;
  background-color: var(--color-hairline);
  border-radius: var(--rounded-lg);
  overflow: hidden;
}

.diff-view__line {
  display: flex;
  align-items: flex-start;
  gap: var(--space-sm);
  padding: var(--space-xs) var(--space-sm);
  background-color: var(--color-surface-0);
  font-family: var(--font-family-mono);
  font-size: var(--font-code-size);
}

.diff-view__line--added {
  background-color: rgba(34, 197, 94, 0.1);
}

.diff-view__line--removed {
  background-color: rgba(239, 68, 68, 0.1);
}

.diff-view__line-num {
  min-width: 32px;
  color: var(--color-ink-muted);
  text-align: right;
}

.diff-view__line-type {
  min-width: 32px;
  font-size: var(--font-body-size-sm);
  font-weight: var(--font-body-weight-bold);
}

.diff-view__line--added .diff-view__line-type {
  color: var(--color-success);
}

.diff-view__line--removed .diff-view__line-type {
  color: var(--color-risk-high);
}

.diff-view__line-text {
  flex: 1;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
