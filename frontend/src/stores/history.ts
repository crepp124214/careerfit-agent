import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { fetchReportHistory } from '@/api/reports'
import type { HistoryItem, HistoryParams } from '@/api/reports'

export type HistoryStatus = 'idle' | 'loading' | 'ready' | 'error' | 'empty'

export const useHistoryStore = defineStore('history', () => {
  const items = ref<HistoryItem[]>([])
  const status = ref<HistoryStatus>('idle')
  const error = ref('')

  const latest = computed<HistoryItem | null>(() => items.value[0] ?? null)

  const scoreDelta = computed<number | null>(() => {
    if (items.value.length < 2) return null
    const first = items.value[0]
    const second = items.value[1]
    if (!first || !second) return null
    return first.finalScore - second.finalScore
  })

  const hasEnoughData = computed(() => items.value.length >= 2)

  async function load(params?: HistoryParams) {
    status.value = 'loading'
    error.value = ''

    const res = await fetchReportHistory(params)

    if (!res.ok) {
      status.value = 'error'
      error.value = res.message
      return false
    }

    items.value = res.data.items
    status.value = items.value.length === 0 ? 'empty' : 'ready'
    return true
  }

  function clear() {
    items.value = []
    status.value = 'idle'
    error.value = ''
  }

  return {
    items,
    status,
    error,
    latest,
    scoreDelta,
    hasEnoughData,
    load,
    clear,
  }
})
