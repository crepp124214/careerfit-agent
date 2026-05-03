import { computed } from 'vue'
import { useAvailabilityStore } from '@/stores/availability'

export function useBackendStatus() {
  const store = useAvailabilityStore()

  const jobsReady = computed(() => store.states.jobs === 'ready')
  const resumesReady = computed(() => store.states.resumes === 'ready')
  const analysisReady = computed(() => store.states.analysis === 'ready')

  return {
    store,
    jobsReady,
    resumesReady,
    analysisReady,
  }
}
