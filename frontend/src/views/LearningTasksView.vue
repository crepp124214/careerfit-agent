<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAvailabilityStore } from '@/stores/availability'
import { useLearningStore } from '@/stores/learning'
import { useAnalysesStore } from '@/stores/analyses'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'
import EmptyState from '@/components/feedback/EmptyState.vue'
import AppButton from '@/components/common/AppButton.vue'
import ErrorBanner from '@/components/feedback/ErrorBanner.vue'
import LoadingCard from '@/components/feedback/LoadingCard.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import type { LearningTask, LearningTaskStatus } from '@/api/learning'

const availability = useAvailabilityStore()
const learning = useLearningStore()
const analyses = useAnalysesStore()
const route = useRoute()

const isUnavailable = computed(() => availability.states.learning === 'unavailable')
const isReady = computed(() => availability.states.learning === 'ready')
const taskIdFromRoute = computed(() => route.query.taskId?.toString() ?? '')
const hasTasks = computed(() => learning.tasks.length > 0)
const isLoading = computed(() => learning.status === 'loading')
const hasError = computed(() => learning.status === 'error' || learning.status === 'unavailable')

// 自动检测可用的taskId：优先使用路由参数，否则使用最新的分析任务
const effectiveTaskId = computed<string>(() => {
  if (taskIdFromRoute.value) {
    return taskIdFromRoute.value
  }
  
  // 如果路由没有taskId，尝试从analyses store获取最新任务
  if (analyses.currentTaskId) {
    return String(analyses.currentTaskId)
  }
  
  return ''
})

const canGenerateTasks = computed(() => {
  return Boolean(effectiveTaskId.value)
})

const statusLabels: Record<LearningTaskStatus, string> = {
  not_started: '未开始',
  doing: '进行中',
  done: '已完成',
  paused: '已暂缓',
  in_progress: '进行中',
  completed: '已完成',
}

const statusTones: Record<LearningTaskStatus, 'neutral' | 'info' | 'risk-low' | 'risk-medium'> = {
  not_started: 'neutral',
  doing: 'info',
  done: 'risk-low',
  paused: 'risk-medium',
  in_progress: 'info',
  completed: 'risk-low',
}

function statusLabel(status: LearningTaskStatus) {
  return statusLabels[status]
}

function statusTone(status: LearningTaskStatus) {
  return statusTones[status]
}

function startTask(task: LearningTask) {
  void learning.updateStatus(task.id, 'doing')
}

function pauseTask(task: LearningTask) {
  void learning.updateStatus(task.id, 'paused')
}

function generateTasks() {
  if (!effectiveTaskId.value) return
  void learning.generateFromTask(effectiveTaskId.value)
}

// 自动加载：如果路由没有taskId，尝试从store获取
onMounted(async () => {
  if (!taskIdFromRoute.value && !analyses.currentTaskId) {
    // 尝试获取最新的分析任务
    await analyses.loadLatestTask()
  }
})

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
  <section class="learning-view" role="main" aria-label="面试准备计划">
    <h1 class="learning-view__title">面试准备计划</h1>
    <p class="learning-view__description">基于面试题为你定制精准的准备清单</p>

    <BackendNotReadyNotice
      v-if="isUnavailable"
      feature="面试准备计划"
      waitingFor="learning 接口"
    />

    <template v-else>
      <LoadingCard
        v-if="isLoading"
        title="正在生成准备计划..."
        description="根据你的面试题制定个性化准备方案"
      />

      <ErrorBanner
        v-else-if="hasError"
        title="准备计划加载失败"
        :detail="learning.error ?? '请稍后重试。'"
        retry-label="重试"
        @retry="learning.loadTasks"
      />

      <template v-else-if="isReady && hasTasks">
        <div class="learning-view__actions">
          <AppButton variant="secondary" size="sm" @click="learning.loadTasks">
            刷新任务列表
          </AppButton>
          <StatusBadge tone="risk-low">已生成准备计划</StatusBadge>
        </div>

        <ul class="learning-view__list" aria-label="面试准备任务列表">
          <li
            v-for="task in learning.tasks"
            :key="task.id"
            class="learning-task"
          >
            <article class="learning-task__main">
              <header class="learning-task__header">
                <h2 class="learning-task__title">
                  {{ task.title || '未命名准备任务' }}
                </h2>
                <span v-if="task.skill" class="learning-task__skill-tag">{{ task.skill }}</span>
                <StatusBadge :tone="statusTone(task.status)">
                  {{ statusLabel(task.status) }}
                </StatusBadge>
              </header>

              <div v-if="task.target_question" class="learning-task__question">
                <strong>📋 目标面试题：</strong>
                <p>{{ task.target_question }}</p>
              </div>

              <ul v-if="task.specificActions && task.specificActions.length > 0" class="learning-task__actions-list">
                <li v-for="(action, idx) in task.specificActions!" :key="idx">
                  {{ action }}
                </li>
              </ul>

              <footer class="learning-task__meta">
                <span v-if="task.timeInvestment">⏱️ {{ task.timeInvestment }}</span>
                <span v-if="task.expectedOutcome">🎯 {{ task.expectedOutcome }}</span>
                <span v-if="task.isInterviewPrep" class="badge-interview-prep">🎤 面试准备</span>
              </footer>

              <div class="learning-task__actions" aria-label="准备任务操作">
                <AppButton
                  v-if="task.status === 'not_started' || !task.status"
                  variant="primary"
                  :aria-label="`开始准备：${task.title}`"
                  @click="startTask(task)"
                >
                  开始准备
                </AppButton>
                <AppButton
                  v-else-if="task.status === 'doing' || task.status === 'in_progress'"
                  variant="secondary"
                  :aria-label="`暂缓准备：${task.title}`"
                  @click="pauseTask(task)"
                >
                  暂缓
                </AppButton>
                <AppButton
                  v-else-if="task.status === 'done' || task.status === 'completed'"
                  variant="secondary"
                  disabled
                  aria-label="已完成"
                >
                  已完成 ✓
                </AppButton>
                <AppButton
                  v-else-if="task.status === 'paused'"
                  variant="primary"
                  :aria-label="`继续准备：${task.title}`"
                  @click="startTask(task)"
                >
                  继续
                </AppButton>
              </div>
            </article>
          </li>
        </ul>
      </template>

      <div v-else class="learning-view__empty">
        <AppButton
          variant="primary"
          :disabled="!canGenerateTasks"
          :aria-label="canGenerateTasks ? '生成面试准备计划' : '需要先完成一次分析才能生成准备计划'"
          @click="generateTasks"
        >
          生成面试准备计划
        </AppButton>

        <EmptyState
          title="暂无准备计划"
          :description="canGenerateTasks ? '点击上方按钮，系统将根据你的面试题生成个性化准备清单。' : '请先完成一次岗位匹配分析并查看报告中的面试题，即可在此生成准备计划。'"
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
  border-radius: var(--rounded-xl);
  padding: var(--space-lg);
  box-shadow: var(--shadow-sm);
  transition:
    border-color var(--motion-duration-fast) var(--motion-easing-standard),
    box-shadow var(--motion-duration-fast) var(--motion-easing-standard);
}

.learning-task:hover {
  border-color: var(--color-hairline-strong);
  box-shadow: var(--shadow-md);
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

/* 面试准备计划特有样式 */
.learning-task__skill-tag {
  display: inline-block;
  padding: 2px 8px;
  background-color: var(--color-surface-subtle);
  color: var(--color-ink-muted);
  border-radius: var(--radius-sm);
  font-size: var(--font-body-xs-size);
  font-weight: var(--font-body-weight-medium);
}

.learning-task__question {
  margin: var(--space-sm) 0;
  padding: var(--space-sm);
  background-color: var(--color-surface-subtle);
  border-left: 3px solid var(--color-primary);
  border-radius: var(--radius-sm);
}

.learning-task__question strong {
  display: block;
  margin-bottom: var(--space-xs);
  color: var(--color-primary);
  font-size: var(--font-body-sm-size);
}

.learning-task__question p {
  margin: 0;
  color: var(--color-ink);
  font-style: italic;
  line-height: var(--font-body-line);
}

.learning-task__actions-list {
  list-style: none;
  padding: 0;
  margin: var(--space-sm) 0;
}

.learning-task__actions-list li {
  position: relative;
  padding-left: var(--space-md);
  margin-bottom: var(--space-xs);
  font-size: var(--font-body-sm-size);
  line-height: var(--font-body-sm-line);
  color: var(--color-ink-subtle);
}

.learning-task__actions-list li::before {
  content: "✓";
  position: absolute;
  left: 0;
  color: var(--color-success);
  font-weight: bold;
}

.task-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
  margin-top: var(--space-sm);
  padding-top: var(--space-sm);
  border-top: 1px solid var(--color-hairline);
  font-size: var(--font-body-xs-size);
  color: var(--color-ink-muted);
}

.badge-interview-prep {
  display: inline-block;
  padding: 2px 8px;
  background-color: #e3f2fd;
  color: #1976d2;
  border-radius: var(--radius-full);
  font-size: var(--font-body-xs-size);
  font-weight: var(--font-body-weight-semibold);
}
</style>
