import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { compareResumes } from '@/api/resumes'
import type { ResumeDiff, DiffSection, DiffSummary, ScoreContext } from '@/api/resumes'

export type DiffStatus = 'idle' | 'loading' | 'ready' | 'error' | 'empty'

export const useResumeDiffStore = defineStore('resumeDiff', () => {
  const fromId = ref<string | null>(null)
  const toId = ref<string | null>(null)
  const diff = ref<ResumeDiff | null>(null)
  const status = ref<DiffStatus>('idle')
  const error = ref('')

  const sections = computed<DiffSection[]>(() => diff.value?.sections ?? [])
  const summary = computed<DiffSummary | null>(() => diff.value?.summary ?? null)
  const scoreContext = computed<ScoreContext | null>(() => diff.value?.scoreContext ?? null)

  const hasValidSelection = computed(() => {
    return fromId.value !== null && toId.value !== null && fromId.value !== toId.value
  })

  async function load() {
    if (!fromId.value || !toId.value) {
      error.value = '请选择两个简历版本'
      status.value = 'error'
      return false
    }

    if (fromId.value === toId.value) {
      error.value = '不能选择相同的简历版本'
      status.value = 'error'
      return false
    }

    status.value = 'loading'
    error.value = ''

    const res = await compareResumes(fromId.value, toId.value)

    if (!res.ok) {
      status.value = 'error'
      error.value = res.message
      return false
    }

    diff.value = res.data
    status.value = 'ready'
    return true
  }

  function setFromId(id: string | null) {
    fromId.value = id
  }

  function setToId(id: string | null) {
    toId.value = id
  }

  function clear() {
    fromId.value = null
    toId.value = null
    diff.value = null
    status.value = 'idle'
    error.value = ''
  }

  return {
    fromId,
    toId,
    diff,
    status,
    error,
    sections,
    summary,
    scoreContext,
    hasValidSelection,
    load,
    setFromId,
    setToId,
    clear,
  }
})
