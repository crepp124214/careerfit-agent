import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { fetchJobs, createJob, fetchJob } from '@/api/jobs'
import type { Job, CreateJobPayload } from '@/api/jobs'

export const useJobsStore = defineStore('jobs', () => {
  const list = ref<Job[]>([])
  const loading = ref(false)
  const error = ref('')
  const selectedId = ref<number | null>(null)

  const selectedJob = computed(() =>
    list.value.find((j) => j.id === selectedId.value) ?? null,
  )

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

  return {
    list,
    loading,
    error,
    selectedId,
    selectedJob,
    load,
    add,
    loadOne,
    select,
  }
})
