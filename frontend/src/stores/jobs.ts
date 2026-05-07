import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { fetchJobs, createJob, fetchJob, compareJobs as apiCompareJobs } from '@/api/jobs'
import type { Job, CreateJobPayload, CompareItem } from '@/api/jobs'

export const useJobsStore = defineStore('jobs', () => {
  const list = ref<Job[]>([])
  const loading = ref(false)
  const error = ref('')
  const selectedId = ref<number | null>(null)
  const compareData = ref<CompareItem[] | null>(null)
  const compareMode = ref(false)
  const compareSelection = ref<Set<number>>(new Set())
  const compareLoading = ref(false)

  const selectedJob = computed(() =>
    list.value.find((j) => j.id === selectedId.value) ?? null,
  )

  const compareEnabled = computed(() => compareSelection.value.size >= 2)

  async function load() {
    loading.value = true
    error.value = ''
    const res = await fetchJobs()
    if (!res.ok) {
      error.value = res.message
      loading.value = false
      return
    }
    list.value = res.data
    loading.value = false
  }

  async function add(payload: CreateJobPayload) {
    const res = await createJob(payload)
    if (!res.ok) {
      error.value = res.message
      return
    }
    list.value.unshift(res.data)
    selectedId.value = res.data.id
  }

  async function loadOne(id: number) {
    const res = await fetchJob(String(id))
    if (!res.ok) {
      error.value = res.message
      return null
    }
    return res.data
  }

  function select(id: number | null) {
    selectedId.value = id
  }

  function toggleCompareMode() {
    compareMode.value = !compareMode.value
    compareSelection.value = new Set()
    compareData.value = null
  }

  function toggleCompareSelection(jobId: number) {
    const next = new Set(compareSelection.value)
    if (next.has(jobId)) {
      next.delete(jobId)
    } else {
      if (next.size >= 5) return
      next.add(jobId)
    }
    compareSelection.value = next
  }

  async function runCompare() {
    const ids = Array.from(compareSelection.value)
    if (ids.length < 2) return
    compareLoading.value = true
    error.value = ''
    try {
      const res = await apiCompareJobs(ids)
      if (res.ok) {
        compareData.value = res.data.items
      } else {
        error.value = res.message
      }
    } finally {
      compareLoading.value = false
    }
  }

  function clearCompare() {
    compareData.value = null
    compareSelection.value = new Set()
    compareMode.value = false
  }

  return {
    list,
    loading,
    error,
    selectedId,
    selectedJob,
    compareData,
    compareMode,
    compareSelection,
    compareLoading,
    compareEnabled,
    load,
    add,
    loadOne,
    select,
    toggleCompareMode,
    toggleCompareSelection,
    runCompare,
    clearCompare,
  }
})
