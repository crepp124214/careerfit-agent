<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAvailabilityStore } from '@/stores/availability'
import { useAnalysesStore } from '@/stores/analyses'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'
import LoadingCard from '@/components/feedback/LoadingCard.vue'
import ErrorBanner from '@/components/feedback/ErrorBanner.vue'
import AgentTraceTimeline from '@/components/report/AgentTraceTimeline.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'

const props = withDefaults(
  defineProps<{ taskId: string }>(),
  { taskId: '' },
)

const availability = useAvailabilityStore()
const analyses = useAnalysesStore()

const isUnavailable = computed(() => availability.states.agentRuns === 'unavailable')
const isValidTaskId = computed(() => props.taskId.trim().length > 0)

async function load() {
  if (!isValidTaskId.value || isUnavailable.value) return
  await analyses.loadAgentRun(props.taskId)
}

onMounted(load)
</script>

<template>
  <section class="trace-view" role="main" aria-label="Agent 运行轨迹">
    <h1 class="trace-view__title">Agent 运行轨迹</h1>

    <ErrorBanner
      v-if="!isValidTaskId"
      title="无效的任务 ID"
      detail="请从报告页或分析记录中选择一个有效的分析任务。"
    />

    <BackendNotReadyNotice
      v-else-if="isUnavailable"
      feature="Agent 运行轨迹"
      waitingFor="agent_runs 接口"
    />

    <LoadingCard
      v-else-if="analyses.loading"
      title="正在加载运行轨迹…"
      :lines="4"
    />

    <ErrorBanner
      v-else-if="analyses.error"
      title="加载失败"
      :detail="analyses.error"
    />

    <template v-else-if="analyses.nodes.length > 0">
      <div class="trace-view__header">
        <span class="trace-view__task-id">任务 ID：{{ taskId }}</span>
        <StatusBadge tone="info">
          {{ analyses.nodes.length }} 个节点
        </StatusBadge>
      </div>

      <AgentTraceTimeline :nodes="analyses.nodes" />
    </template>

    <LoadingCard
      v-else
      title="等待运行轨迹…"
      :lines="3"
    />
  </section>
</template>

<style scoped>
.trace-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  max-width: 960px;
}

.trace-view__title {
  margin: 0;
  font-size: var(--font-headline-size);
  font-weight: var(--font-headline-weight);
  line-height: var(--font-headline-line);
}

.trace-view__header {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.trace-view__task-id {
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-subtle);
}
</style>
