import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { fetchResumes, createResume, fetchResume } from '@/api/resumes'
import type { Resume, CreateResumePayload } from '@/api/resumes'

export const useResumesStore = defineStore('resumes', () => {
  const list = ref<Resume[]>([])
  const loading = ref(false)
  const error = ref('')
  const selectedId = ref<string | null>(null)

  const selectedResume = computed(() =>
    list.value.find((r) => r.id === selectedId.value) ?? null,
  )

  async function load() {
    loading.value = true
    error.value = ''
    const res = await fetchResumes()
    if (!res.ok) {
      error.value = res.message
      loading.value = false
      return
    }
    list.value = res.data
    loading.value = false
  }

  async function add(payload: CreateResumePayload) {
    const res = await createResume(payload)
    if (!res.ok) {
      error.value = res.message
      return
    }
    list.value.unshift(res.data)
    selectedId.value = res.data.id
  }

  async function loadOne(id: string) {
    const res = await fetchResume(id)
    if (!res.ok) {
      error.value = res.message
      return null
    }
    return res.data
  }

  function select(id: string | null) {
    selectedId.value = id
  }

  return {
    list,
    loading,
    error,
    selectedId,
    selectedResume,
    load,
    add,
    loadOne,
    select,
  }
})
