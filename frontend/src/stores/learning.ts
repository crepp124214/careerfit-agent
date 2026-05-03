import { ref } from 'vue'
import { defineStore } from 'pinia'
import {
  fetchLearningTasks,
  generateLearningTasks,
  updateLearningTaskStatus,
  type LearningTask,
  type LearningTaskStatus,
} from '@/api/learning'
import { isUnavailable } from '@/api/client'

type LearningStoreStatus = 'idle' | 'loading' | 'ready' | 'unavailable' | 'error'

function messageFrom(res: { message?: string }) {
  return res.message ?? '学习任务请求失败'
}

export const useLearningStore = defineStore('learning', () => {
  const tasks = ref<LearningTask[]>([])
  const status = ref<LearningStoreStatus>('idle')
  const error = ref<string | null>(null)

  async function loadTasks() {
    status.value = 'loading'
    error.value = null
    const res = await fetchLearningTasks()
    if (res.ok) {
      tasks.value = res.data
      status.value = 'ready'
      return
    }
    tasks.value = []
    error.value = messageFrom(res)
    status.value = isUnavailable(res) ? 'unavailable' : 'error'
  }

  async function generateFromTask(taskId: number | string) {
    status.value = 'loading'
    error.value = null
    const res = await generateLearningTasks(taskId)
    if (res.ok) {
      tasks.value = res.data
      status.value = 'ready'
      return
    }
    error.value = messageFrom(res)
    status.value = isUnavailable(res) ? 'unavailable' : 'error'
  }

  async function updateStatus(id: number, nextStatus: LearningTaskStatus) {
    const res = await updateLearningTaskStatus(id, nextStatus)
    if (res.ok) {
      tasks.value = tasks.value.map((task) => (task.id === id ? res.data : task))
      error.value = null
      status.value = 'ready'
      return
    }
    error.value = messageFrom(res)
    status.value = isUnavailable(res) ? 'unavailable' : 'error'
  }

  return { tasks, status, error, loadTasks, generateFromTask, updateStatus }
})
