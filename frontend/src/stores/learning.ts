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

/**
 * 将后端 snake_case 字段转换为前端 camelCase 别名
 */
function transformTaskData(task: Record<string, unknown>): LearningTask {
  const base = { ...task } as unknown as LearningTask
  
  // 添加 camelCase 别名（方便模板使用）
  return {
    ...base,
    timeInvestment: base.time_investment ?? undefined,
    expectedOutcome: base.expected_outcome ?? undefined,
    specificActions: base.specific_actions ?? undefined,
    isInterviewPrep: base.is_interview_prep ?? false,
  }
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
      // 转换字段名
      tasks.value = res.data.map(t => transformTaskData(t as unknown as Record<string, unknown>))
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
      // 转换字段名
      tasks.value = res.data.map(t => transformTaskData(t as unknown as Record<string, unknown>))
      status.value = 'ready'
      return
    }
    error.value = messageFrom(res)
    status.value = isUnavailable(res) ? 'unavailable' : 'error'
  }

  async function updateStatus(id: number, nextStatus: LearningTaskStatus) {
    const res = await updateLearningTaskStatus(id, nextStatus)
    if (res.ok) {
      // 更新单个任务时也转换字段名
      const updated = transformTaskData(res.data as unknown as Record<string, unknown>)
      tasks.value = tasks.value.map((task) => (task.id === id ? updated : task))
      error.value = null
      status.value = 'ready'
      return
    }
    error.value = messageFrom(res)
    status.value = isUnavailable(res) ? 'unavailable' : 'error'
  }

  return { tasks, status, error, loadTasks, generateFromTask, updateStatus }
})
