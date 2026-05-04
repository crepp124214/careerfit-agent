import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import {
  createSession as apiCreateSession,
  listSessions as apiListSessions,
  getSession as apiGetSession,
  updateQuestion as apiUpdateQuestion,
  isInterviewNotReady,
} from '@/api/interview'
import type { InterviewSession, InterviewSessionDetail } from '@/api/interview'

export const useInterviewStore = defineStore('interview', () => {
  const sessions = ref<InterviewSession[]>([])
  const currentSession = ref<InterviewSessionDetail | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const isUnavailable = ref(false)

  const progressPercent = computed(() => {
    if (!currentSession.value || currentSession.value.totalQuestions === 0) return 0
    return Math.round(
      (currentSession.value.completedQuestions / currentSession.value.totalQuestions) * 100,
    )
  })

  async function fetchSessions(status?: string) {
    isLoading.value = true
    error.value = null
    try {
      const resp = await apiListSessions(status)
      sessions.value = resp.items
      isUnavailable.value = false
    } catch (err) {
      if (isInterviewNotReady(err)) {
        isUnavailable.value = true
        sessions.value = []
      } else {
        error.value = err instanceof Error ? err.message : 'unknown_error'
      }
    } finally {
      isLoading.value = false
    }
  }

  async function fetchSession(id: number) {
    isLoading.value = true
    error.value = null
    try {
      currentSession.value = await apiGetSession(id)
      isUnavailable.value = false
    } catch (err) {
      if (isInterviewNotReady(err)) {
        isUnavailable.value = true
        currentSession.value = null
      } else {
        error.value = err instanceof Error ? err.message : 'unknown_error'
      }
    } finally {
      isLoading.value = false
    }
  }

  async function createSession(reportId: number, includeRag = true) {
    isLoading.value = true
    error.value = null
    try {
      const resp = await apiCreateSession(reportId, includeRag)
      isUnavailable.value = false
      return resp.session
    } catch (err) {
      if (isInterviewNotReady(err)) {
        isUnavailable.value = true
      } else {
        error.value = err instanceof Error ? err.message : 'unknown_error'
      }
      return null
    } finally {
      isLoading.value = false
    }
  }

  async function updateQuestionStatus(
    sessionId: number,
    questionId: number,
    data: { status?: string; notes?: string },
  ) {
    try {
      const result = await apiUpdateQuestion(sessionId, questionId, data)
      if (currentSession.value && currentSession.value.id === sessionId) {
        const q = currentSession.value.questions.find((q) => q.id === questionId)
        if (q) {
          if (data.status) q.status = result.status
          if (data.notes !== undefined) q.notes = result.notes
        }
        if (data.status) {
          const completed = currentSession.value.questions.filter(
            (q) => q.status === 'completed' || q.status === 'skipped',
          ).length
          currentSession.value.completedQuestions = completed
          if (completed >= currentSession.value.totalQuestions) {
            currentSession.value.status = 'completed'
          } else if (completed > 0 || data.status === 'practicing') {
            currentSession.value.status = 'in_progress'
          }
        }
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'unknown_error'
    }
  }

  return {
    sessions,
    currentSession,
    isLoading,
    error,
    isUnavailable,
    progressPercent,
    fetchSessions,
    fetchSession,
    createSession,
    updateQuestionStatus,
  }
})
