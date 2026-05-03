import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { fetchReport } from '@/api/reports'
import type { Report } from '@/api/reports'
import { fetchAgentRun } from '@/api/agentRuns'
import type { AgentRun, AgentNode } from '@/api/agentRuns'

export const useAnalysesStore = defineStore('analyses', () => {
  const report = ref<Report | null>(null)
  const agentRun = ref<AgentRun | null>(null)
  const loading = ref(false)
  const error = ref('')

  const nodes = computed<AgentNode[]>(() => agentRun.value?.nodes ?? [])

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
    hasIntegrityGuard,
    loadReport,
    loadAgentRun,
    clear,
  }
})
