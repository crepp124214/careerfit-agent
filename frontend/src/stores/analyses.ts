import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { fetchReport, fetchReportHistory } from '@/api/reports'
import type { Report } from '@/api/reports'
import { fetchAgentRun } from '@/api/agentRuns'
import type { AgentRun, AgentNode } from '@/api/agentRuns'

export const useAnalysesStore = defineStore('analyses', () => {
  const report = ref<Report | null>(null)
  const agentRun = ref<AgentRun | null>(null)
  const loading = ref(false)
  const error = ref('')

  const nodes = computed<AgentNode[]>(() => agentRun.value?.nodes ?? [])

  // 当前报告的taskId（从report中提取）
  const currentTaskId = computed<string | null>(() => {
    if (report.value?.id) {
      return String(report.value.id)
    }
    // 如果没有report但有task_id（某些情况下可能直接有）
    if (report.value && (report.value as Record<string, unknown>).task_id) {
      return String((report.value as Record<string, unknown>).task_id)
    }
    return null
  })

  const hasIntegrityGuard = computed(
    () =>
      report.value?.integrityGuard !== undefined &&
      report.value.integrityGuard.blockedCount > 0,
  )

  async function loadReport(taskId: string) {
    loading.value = true
    error.value = ''

    const [reportRes, runRes] = await Promise.all([
      fetchReport(taskId),
      fetchAgentRun(taskId),
    ])

    if (!reportRes.ok) {
      error.value = reportRes.message
      loading.value = false
      return false
    }

    report.value = reportRes.data
    if (runRes.ok) {
      agentRun.value = runRes.data
    }

    loading.value = false
    return true
  }

  async function loadAgentRun(taskId: string) {
    loading.value = true
    error.value = ''

    const res = await fetchAgentRun(taskId)
    if (!res.ok) {
      error.value = res.message
      loading.value = false
      return false
    }

    agentRun.value = res.data
    loading.value = false
    return true
  }

  // 加载最新的分析任务（用于学习任务页面等需要taskId的场景）
  async function loadLatestTask() {
    loading.value = true
    error.value = ''

    try {
      // 获取最新的报告历史（只取1条）
      const res = await fetchReportHistory({ limit: 1 })

      if (res.ok && res.data.items.length > 0) {
        const latestReport = res.data.items[0]
        if (latestReport?.taskId) {
          // 使用最新报告的taskId加载完整报告
          await loadReport(latestReport.taskId)
          return true
        } else {
          error.value = '最新分析报告缺少任务ID'
          loading.value = false
          return false
        }
      } else {
        error.value = '暂无分析报告，请先完成一次岗位匹配分析'
        loading.value = false
        return false
      }
    } catch (e) {
      error.value = '加载分析任务失败'
      loading.value = false
      return false
    }
  }

  function clear() {
    report.value = null
    agentRun.value = null
    error.value = ''
  }

  return {
    report,
    agentRun,
    nodes,
    loading,
    error,
    currentTaskId,
    hasIntegrityGuard,
    loadReport,
    loadAgentRun,
    loadLatestTask,
    clear,
  }
})
