<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAvailabilityStore } from '@/stores/availability'
import { useLearningStore } from '@/stores/learning'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'
import EmptyState from '@/components/feedback/EmptyState.vue'
import AppButton from '@/components/common/AppButton.vue'
import ErrorBanner from '@/components/feedback/ErrorBanner.vue'
import LoadingCard from '@/components/feedback/LoadingCard.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import type { LearningTask, LearningTaskStatus } from '@/api/learning'

const availability = useAvailabilityStore()
const learning = useLearningStore()
const route = useRoute()

const isUnavailable = computed(() => availability.states.learning === 'unavailable')
const isReady = computed(() => availability.states.learning === 'ready')
const taskId = computed(() => route.query.taskId?.toString() ?? '')
const hasTasks = computed(() => learning.tasks.length > 0)
const isLoading = computed(() => learning.status === 'loading')
const hasError = computed(() => learning.status === 'error' || learning.status === 'unavailable')

const statusLabels: Record<LearningTaskStatus, string> = {
  not_started: '未开始',
  doing: '进行中',
  done: '已完成',
  paused: '已暂缓',
}

const statusTones: Record<LearningTaskStatus, 'neutral' | 'info' | 'risk-low' | 'risk-medium'> = {
  not_started: 'neutral',
  doing: 'info',
  done: 'risk-low',
  paused: 'risk-medium',
}

function statusLabel(status: LearningTaskStatus) {
  return statusLabels[status]
}

function statusTone(status: LearningTaskStatus) {
  return statusTones[status]
}

function evidenceCount(task: LearningTask) {
  return task.evidence_refs?.length ?? 0
}

function isPartial(task: LearningTask) {
  return !task.title || !task.dimension || !task.rationale
}

function startTask(task: LearningTask) {
  void learning.updateStatus(task.id, 'doing')
}

function pauseTask(task: LearningTask) {
  void learning.updateStatus(task.id, 'paused')
}

function completeTask(task: LearningTask) {
  void learning.updateStatus(task.id, 'done')
}

function generateTasks() {
  if (!taskId.value) return
  void learning.generateFromTask(taskId.value)
}

watch(
  () => availability.states.learning,
  (state) => {
    if (state === 'ready' && learning.status === 'idle') {
      void learning.loadTasks()
    }
  },
  { immediate: true },
)
</script>

<template>
  <section class="learning-view" role="main" aria-label="学习任务">
    <h1 class="learning-view__title">学习任务</h1>

    <BackendNotReadyNotice
      v-if="isUnavailable"
      feature="学习任务"
      waitingFor="learning 接口"
    />

    <template v-else>
      <LoadingCard
        v-if="isLoading"
        title="正在加载学习任务"
      />

      <ErrorBanner
        v-else-if="hasError"
        title="学习任务加载失败"
        :detail="learning.error ?? '请稍后重试。'"
        retry-label="重试"
        @retry="learning.loadTasks"
      />

      <template v-else-if="isReady && hasTasks">
        <ul class="learning-view__list" aria-label="学习任务列表">
          <li
            v-for="task in learning.tasks"
            :key="task.id"
            class="learning-task"
          >
            <div class="learning-task__main">
              <div class="learning-task__header">
                <h2 class="learning-task__title">
                  {{ task.title || '未命名学习任务' }}
                </h2>
                <StatusBadge :tone="statusTone(task.status)">
                  {{ statusLabel(task.status) }}
                </StatusBadge>
              </div>
              <p class="learning-task__meta">
                维度：{{ task.dimension || '未标注' }} · 证据引用 {{ evidenceCount(task) }} 条
              </p>
              <p class="learning-task__rationale">
                {{ task.rationale || '这条任务缺少生成理由，请回到报告确认来源。' }}
              </p>
              <p v-if="isPartial(task)" class="learning-task__partial" role="note">
                部分数据缺失，请以来源报告为准。
              </p>
            </div>

            <div class="learning-task__actions" aria-label="学习任务操作">
              <AppButton
                v-if="task.status === 'not_started'"
                variant="primary"
                :aria-label="`开始学习任务：${task.title}`"
                @click="startTask(task)"
              >
                开始
              </AppButton>
              <AppButton
                v-if="task.status === 'doing'"
                variant="secondary"
                :aria-label="`暂缓学习任务：${task.title}`"
                @click="pauseTask(task)"
              >
                暂缓
              </AppButton>
              <AppButton
                v-if="task.status === 'doing'"
                variant="primary"
                :aria-label="`完成学习任务：${task.title}`"
                @click="completeTask(task)"
              >
                完成
              </AppButton>
              <AppButton
                v-if="task.status === 'paused'"
                variant="primary"
                :aria-label="`继续学习任务：${task.title}`"
                @click="startTask(task)"
              >
                继续
              </AppButton>
            </div>
          </li>
        </ul>
      </template>

      <div v-else class="learning-view__empty">
        <AppButton
          variant="primary"
          :disabled="!taskId"
          :aria-label="taskId ? '按当前缺口生成学习任务' : '缺少分析任务 ID，暂不能生成学习任务'"
          @click="generateTasks"
        >
          按当前缺口生成学习任务
        </AppButton>

        <EmptyState
          title="暂无学习任务"
          description="完成分析后，系统将根据你的能力缺口生成个性化学习计划。"
        />
      </div>
    </template>
  </section>
</template>

<style scoped>
.learning-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  max-width: 960px;
}

.learning-view__title {
  margin: 0;
  font-size: var(--font-headline-size);
  font-weight: var(--font-headline-weight);
  line-height: var(--font-headline-line);
}

.learning-view__empty {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--space-md);
}

.learning-view__list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  margin: 0;
  padding: 0;
}

.learning-task {
  display: flex;
  justify-content: space-between;
  gap: var(--space-lg);
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  padding: var(--space-lg);
}

.learning-task__main {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  min-width: 0;
}

.learning-task__header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-sm);
}

.learning-task__title {
  margin: 0;
  color: var(--color-ink);
  font-size: var(--font-title-size);
  font-weight: var(--font-title-weight);
  line-height: var(--font-title-line);
  overflow-wrap: anywhere;
}

.learning-task__meta,
.learning-task__rationale,
.learning-task__partial {
  margin: 0;
  font-size: var(--font-body-sm-size);
  line-height: var(--font-body-sm-line);
}

.learning-task__meta {
  color: var(--color-ink-subtle);
}

.learning-task__rationale {
  color: var(--color-ink-muted);
}

.learning-task__partial {
  color: var(--color-risk-medium);
}

.learning-task__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: flex-end;
  gap: var(--space-sm);
}

@media (max-width: 640px) {
  .learning-task {
    flex-direction: column;
  }

  .learning-task__actions {
    justify-content: flex-start;
  }
}
</style>
