import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { fetchBackendCapabilities } from '@/api/availability'

type Capability = 'jobs' | 'resumes' | 'analysis' | 'reports' | 'agentRuns' | 'learning'
type CapabilityState = 'unknown' | 'ready' | 'unavailable'

const ALL_CAPABILITIES: Capability[] = [
  'jobs',
  'resumes',
  'analysis',
  'reports',
  'agentRuns',
  'learning',
]

export const useAvailabilityStore = defineStore('availability', () => {
  const states = ref<Record<Capability, CapabilityState>>({
    jobs: 'unknown',
    resumes: 'unknown',
    analysis: 'unknown',
    reports: 'unknown',
    agentRuns: 'unknown',
    learning: 'unknown',
  })

  const isLoading = ref(false)

  const allReady = computed(() =>
    ALL_CAPABILITIES.every((c) => states.value[c] === 'ready'),
  )

  const anyUnavailable = computed(() =>
    ALL_CAPABILITIES.some((c) => states.value[c] === 'unavailable'),
  )

  const statusLabel = computed(() => {
    if (isLoading.value) return '探测中…'
    if (allReady.value) return '已连接'
    if (anyUnavailable.value) return '部分未上线'
    return '后端未连接'
  })

  function setCapability(cap: Capability, state: CapabilityState) {
    states.value[cap] = state
  }

  async function probe() {
    isLoading.value = true
    const res = await fetchBackendCapabilities()
    if (!res.ok) {
      for (const cap of ALL_CAPABILITIES) {
        states.value[cap] = 'unavailable'
      }
      isLoading.value = false
      return
    }
    const caps = res.capabilities
    for (const cap of ALL_CAPABILITIES) {
      states.value[cap] = caps[cap] ? 'ready' : 'unavailable'
    }
    isLoading.value = false
  }

  return {
    states,
    isLoading,
    allReady,
    anyUnavailable,
    statusLabel,
    setCapability,
    probe,
  }
})
