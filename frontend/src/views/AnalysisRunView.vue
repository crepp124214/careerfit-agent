<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAvailabilityStore } from '@/stores/availability'
import { useJobsStore } from '@/stores/jobs'
import { useResumesStore } from '@/stores/resumes'
import { createAnalysis, fetchAnalysis } from '@/api/analysis'
import type { AnalysisTask } from '@/api/analysis'
import { connectSSE, getAnalysisStreamUrl } from '@/api/sse'
import type { SSEEvent, SSEConnection } from '@/api/sse'
import AgentTerminal from '@/components/analysis/AgentTerminal.vue'
import type { TerminalLine } from '@/components/analysis/AgentTerminal.vue'
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
    !launching.value &&
    !!jobs.selectedId &&
    !!resumes.selectedId,
)

const launching = ref(false)
const error = ref('')
const currentTask = ref<AnalysisTask | null>(null)
const pollInterval = ref<ReturnType<typeof setInterval> | null>(null)
const sseConnection = ref<SSEConnection | null>(null)
const terminalLines = ref<TerminalLine[]>([])
const workflowCompleted = ref(false)
const lineId = ref(0)
const completedNodeCount = ref(0)

function addLine(text: string, type: TerminalLine['type']): void {
  terminalLines.value.push({ id: lineId.value++, text, type })
}

function addBlank(): void {
  terminalLines.value.push({ id: lineId.value++, text: '', type: 'blank' })
}

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(1)}s`
}

function now(): string {
  return new Date().toLocaleTimeString('zh-CN', { hour12: false })
}

function handleSSEEvent(event: SSEEvent): void {
  const data = event.data
  const ts = now()

  switch (event.type) {
    case 'node_started': {
      const mode = data.execution_mode === 'llm' ? '[LLM]' : '[确定性]'
      addLine(`[${ts}] [${data.node_index}/${data.total_nodes}] ◳ ${data.node_label} ...                    ${mode}`, 'start')
      break
    }

    case 'llm_connecting': {
      addLine(`[${ts}]   → 正在连接大模型 API ...`, 'connecting')
      break
    }

    case 'llm_connected': {
      const model = data.model_name || 'unknown'
      const duration = data.connection_duration_ms ? ` (${formatDuration(data.connection_duration_ms)})` : ''
      addLine(`[${ts}] ✓ 大模型 API 连接成功                  ${model}${duration}`, 'connected')
      break
    }

    case 'llm_failed': {
      const errMsg = data.error || '未知错误'
      const duration = data.connection_duration_ms ? ` (耗时 ${formatDuration(data.connection_duration_ms)})` : ''
      addLine(`[${ts}] ✗ 大模型 API 连接失败                  ${errMsg}${duration}`, 'failed')
      if (data.fallback_used) {
        addLine(`[${ts}]   → 回退到本地规则引擎`, 'info')
      }
      break
    }

    case 'node_completed': {
      completedNodeCount.value = data.node_index
      const dur = formatDuration(data.duration_ms)
      const fallback = data.execution_mode === 'rule' && data.node_index >= 6 ? ' (fallback)' : ''
      addLine(`[${ts}] [${data.node_index}/${data.total_nodes}] ✓ ${data.node_label}完成${fallback}                     ${dur}`, 'success')
      if (data.summary) {
        addLine(`[${ts}]       → ${data.summary}`, 'summary')
      }
      addBlank()
      break
    }

    case 'node_failed': {
      const dur = formatDuration(data.duration_ms)
      addLine(`[${ts}] [${data.node_index}/${data.total_nodes}] ✗ ${data.node_label}失败                     ${dur}`, 'error')
      if (data.error) {
        addLine(`[${ts}]   错误: ${data.error}`, 'error')
      }
      addBlank()
      break
    }

    case 'workflow_completed': {
      workflowCompleted.value = true
      const totalDur = formatDuration(data.total_duration_ms)
      addLine(`[${ts}] ✓ 分析完成  总耗时: ${totalDur}`, 'success')
      addLine(`[${ts}]   综合匹配度: ${data.final_score}%  高风险: ${data.high_risk_count}  需关注: ${data.watch_count}`, 'info')
      launching.value = false

      setTimeout(() => {
        router.push({ name: 'report', params: { taskId: currentTask.value?.id } })
      }, 2000)
      break
    }
  }
}

function cleanupConnections(): void {
  if (sseConnection.value) {
    sseConnection.value.close()
    sseConnection.value = null
  }
  if (pollInterval.value) {
    clearInterval(pollInterval.value)
    pollInterval.value = null
  }
}

onMounted(async () => {
  await availability.probe()
  if (availability.states.jobs !== 'unavailable' && jobs.list.length === 0) {
    await jobs.load()
    if (jobs.list.length > 0 && !jobs.selectedId) {
      const firstJob = jobs.list[0]
      if (firstJob) {
        jobs.select(firstJob.id)
      }
    }
  }
  if (availability.states.resumes !== 'unavailable' && resumes.list.length === 0) {
    await resumes.load()
    if (resumes.list.length > 0 && !resumes.selectedId) {
      const firstResume = resumes.list[0]
      if (firstResume) {
        resumes.select(firstResume.id)
      }
    }
  }
})

onUnmounted(() => {
  cleanupConnections()
})

async function pollTaskStatus(taskId: number) {
  const res = await fetchAnalysis(taskId)
  if (!res.ok) {
    error.value = res.message
    launching.value = false
    return
  }

  currentTask.value = res.data

  if (res.data.status === 'success') {
    launching.value = false
    cleanupConnections()
    if (!workflowCompleted.value) {
      router.push({ name: 'report', params: { taskId: res.data.id } })
    }
  } else if (res.data.status === 'failed') {
    launching.value = false
    error.value = res.data.error_message || '分析任务失败'
    cleanupConnections()
    addLine(`[${now()}] ✗ 分析任务失败: ${error.value}`, 'error')
  }
}

async function launch() {
  if (!jobs.selectedId || !resumes.selectedId) return
  launching.value = true
  error.value = ''
  currentTask.value = null
  workflowCompleted.value = false
  completedNodeCount.value = 0
  terminalLines.value = []
  lineId.value = 0

  const ts = now()
  addLine(`[${ts}] ▸ CareerFit Agent v0.1`, 'info')
  addLine(`[${ts}]   岗位: ${jobs.selectedJob?.title ?? '未选择'}`, 'info')
  addLine(`[${ts}]   简历: ${resumes.selectedResume?.candidate_name ?? '未选择'}`, 'info')
  addBlank()

  const res = await createAnalysis({
    job_id: jobs.selectedId,
    resume_id: resumes.selectedId,
  })

  if (!res.ok) {
    error.value = res.message
    launching.value = false
    addLine(`[${now()}] ✗ 创建分析任务失败: ${res.message}`, 'error')
    return
  }

  currentTask.value = res.data
  addLine(`[${now()}] ▸ 启动分析任务 #${res.data.id}`, 'info')
  addBlank()

  if (res.data.status === 'success') {
    launching.value = false
    router.push({ name: 'report', params: { taskId: res.data.id } })
    return
  }

  if (res.data.status === 'failed') {
    launching.value = false
    error.value = res.data.error_message || '分析任务失败'
    addLine(`[${now()}] ✗ 分析任务失败: ${error.value}`, 'error')
    return
  }

  const streamUrl = getAnalysisStreamUrl(res.data.id)
  sseConnection.value = connectSSE(
    streamUrl,
    handleSSEEvent,
    () => {
      pollInterval.value = setInterval(() => {
        pollTaskStatus(res.data.id)
      }, 3000)
    },
  )

  pollInterval.value = setInterval(() => {
    pollTaskStatus(res.data.id)
  }, 5000)
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
      <div v-if="!launching" class="analysis-run__selection">
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

      <p v-if="!launching && (!jobs.selectedId || !resumes.selectedId)" class="analysis-run__hint">
        请先在工作台选择目标岗位和简历版本。
      </p>

      <p v-if="error" class="analysis-run__error">{{ error }}</p>

      <AgentTerminal
        v-if="launching || terminalLines.length > 0"
        :lines="terminalLines"
        :completed="workflowCompleted"
      />

      <div v-if="workflowCompleted" class="analysis-run__actions">
        <AppButton
          variant="primary"
          @click="router.push({ name: 'report', params: { taskId: currentTask?.id } })"
        >
          查看报告
        </AppButton>
      </div>

      <AppButton
        v-if="!launching && !workflowCompleted"
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
  max-width: 720px;
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

.analysis-run__actions {
  display: flex;
  gap: var(--space-md);
}
</style>
