<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useInterviewStore } from '@/stores/interview'
import { useAvailabilityStore } from '@/stores/availability'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'

const store = useInterviewStore()
const availability = useAvailabilityStore()
const router = useRouter()

onMounted(() => {
  if (availability.states.interview === 'ready' || availability.states.interview === 'unknown') {
    store.fetchSessions()
  }
})

function openSession(id: number) {
  router.push(`/interview/${id}`)
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    created: '未开始',
    in_progress: '练习中',
    completed: '已完成',
  }
  return map[status] || status
}

function statusTone(status: string) {
  if (status === 'completed') return 'success'
  if (status === 'in_progress') return 'info'
  return 'neutral'
}
</script>

<template>
  <section class="interview-list" data-view="interview-list" role="main" aria-label="面试训练">
    <h1 class="interview-list__title">面试训练</h1>

    <BackendNotReadyNotice
      v-if="availability.states.interview === 'unavailable' || store.isUnavailable"
      feature="面试训练"
      waiting-for="后端面试训练服务"
    />

    <div v-else-if="store.isLoading" class="interview-list__loading" aria-live="polite">
      加载中…
    </div>

    <div v-else-if="store.error" class="interview-list__error" role="alert">
      <p>加载失败：{{ store.error }}</p>
      <button type="button" class="interview-list__retry" @click="store.fetchSessions()">重试</button>
    </div>

    <div v-else-if="store.sessions.length === 0" class="interview-list__empty">
      <p>暂无面试训练会话</p>
      <p class="interview-list__hint">完成一次匹配分析后，可以从报告页创建面试训练。</p>
    </div>

    <ul v-else class="interview-list__items">
      <li
        v-for="session in store.sessions"
        :key="session.id"
        class="interview-list__card"
        tabindex="0"
        role="button"
        @click="openSession(session.id)"
        @keydown.enter="openSession(session.id)"
      >
        <div class="interview-list__card-header">
          <span class="interview-list__card-title">{{ session.jobTitle }}</span>
          <span :class="['interview-list__badge', `interview-list__badge--${statusTone(session.status)}`]">
            {{ statusLabel(session.status) }}
          </span>
        </div>
        <div class="interview-list__card-meta">
          <span>{{ session.totalQuestions }} 道题</span>
          <span>已完成 {{ session.completedQuestions }}/{{ session.totalQuestions }}</span>
        </div>
        <div class="interview-list__progress-bar">
          <div
            class="interview-list__progress-fill"
            :style="{ width: `${session.totalQuestions > 0 ? (session.completedQuestions / session.totalQuestions) * 100 : 0}%` }"
          />
        </div>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.interview-list {
  padding: var(--space-lg);
  max-width: 800px;
  margin: 0 auto;
}

.interview-list__title {
  font-size: var(--font-h2-size);
  font-weight: 600;
  margin-bottom: var(--space-md);
}

.interview-list__loading,
.interview-list__empty {
  text-align: center;
  padding: var(--space-xl) var(--space-md);
  color: var(--color-ink-subtle);
}

.interview-list__hint {
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-tertiary);
  margin-top: var(--space-xs);
}

.interview-list__error {
  text-align: center;
  padding: var(--space-md);
  color: var(--color-status-error, #dc2626);
}

.interview-list__retry {
  margin-top: var(--space-xs);
  padding: var(--space-xs) var(--space-md);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-sm);
  background: var(--color-surface-1);
  cursor: pointer;
}

.interview-list__items {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.interview-list__card {
  background: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  padding: var(--space-md);
  cursor: pointer;
  transition:
    border-color var(--motion-duration-fast) var(--motion-easing-standard),
    box-shadow var(--motion-duration-fast) var(--motion-easing-standard);
}

.interview-list__card:hover {
  border-color: var(--color-hairline-strong);
  box-shadow: var(--shadow-sm);
}

.interview-list__card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-xs);
}

.interview-list__card-title {
  font-weight: 600;
  font-size: var(--font-body-size);
}

.interview-list__badge {
  font-size: var(--font-caption-size);
  padding: 2px 8px;
  border-radius: var(--rounded-xs);
  font-weight: 500;
}

.interview-list__badge--success {
  background: var(--color-status-success-bg, #dcfce7);
  color: var(--color-status-success, #16a34a);
}

.interview-list__badge--info {
  background: var(--color-status-info-bg, #dbeafe);
  color: var(--color-status-info, #2563eb);
}

.interview-list__badge--neutral {
  background: var(--color-surface-2);
  color: var(--color-ink-subtle);
}

.interview-list__card-meta {
  display: flex;
  gap: var(--space-md);
  font-size: var(--font-caption-size);
  color: var(--color-ink-muted);
  margin-bottom: var(--space-xs);
}

.interview-list__progress-bar {
  height: 4px;
  background: var(--color-surface-2);
  border-radius: 2px;
  overflow: hidden;
}

.interview-list__progress-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: 2px;
  transition: width 0.3s ease;
}
</style>
