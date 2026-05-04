<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useInterviewStore } from '@/stores/interview'
import { useAvailabilityStore } from '@/stores/availability'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'

const store = useInterviewStore()
const availability = useAvailabilityStore()
const route = useRoute()

const filterSkill = ref('')
const filterCategory = ref('')
const filterDifficulty = ref('')

onMounted(() => {
  const id = Number(route.params.id)
  if (id) store.fetchSession(id)
})

const session = computed(() => store.currentSession)

const filteredQuestions = computed(() => {
  if (!session.value) return []
  return session.value.questions.filter((q) => {
    if (filterSkill.value && q.skill !== filterSkill.value) return false
    if (filterCategory.value && q.category !== filterCategory.value) return false
    if (filterDifficulty.value && q.difficulty !== filterDifficulty.value) return false
    return true
  })
})

const uniqueSkills = computed(() => {
  if (!session.value) return []
  return [...new Set(session.value.questions.map((q) => q.skill))]
})

const categoryLabel: Record<string, string> = {
  basic: '基础题',
  project_deep_dive: '项目深挖',
  scenario_design: '场景设计',
}

const difficultyLabel: Record<string, string> = {
  easy: '简单',
  medium: '中等',
  hard: '困难',
}

const statusLabel: Record<string, string> = {
  not_started: '未开始',
  practicing: '练习中',
  completed: '已完成',
  skipped: '跳过',
}

function statusTone(status: string) {
  if (status === 'completed') return 'success'
  if (status === 'practicing') return 'info'
  if (status === 'skipped') return 'warning'
  return 'neutral'
}

async function cycleStatus(questionId: number, currentStatus: string) {
  const nextMap: Record<string, string> = {
    not_started: 'practicing',
    practicing: 'completed',
  }
  const next = nextMap[currentStatus]
  if (next) {
    await store.updateQuestionStatus(session.value!.id, questionId, { status: next })
  }
}

async function skipQuestion(questionId: number) {
  await store.updateQuestionStatus(session.value!.id, questionId, { status: 'skipped' })
}

async function saveNotes(questionId: number, notes: string) {
  await store.updateQuestionStatus(session.value!.id, questionId, { notes })
}

const notesMap = ref<Record<number, string>>({})

function getLocalNotes(qid: number): string {
  return notesMap.value[qid] ?? session.value?.questions.find((q) => q.id === qid)?.notes ?? ''
}

function setLocalNotes(qid: number, val: string) {
  notesMap.value[qid] = val
}

function blurNotes(qid: number) {
  const val = notesMap.value[qid]
  if (val !== undefined) {
    saveNotes(qid, val)
  }
}
</script>

<template>
  <section class="interview-detail" data-view="interview-detail" role="main" aria-label="面试训练详情">
    <BackendNotReadyNotice
      v-if="availability.states.interview === 'unavailable' || store.isUnavailable"
      feature="面试训练"
      waiting-for="后端面试训练服务"
    />

    <div v-else-if="store.isLoading" class="interview-detail__loading" aria-live="polite">
      加载中…
    </div>

    <div v-else-if="store.error" class="interview-detail__error" role="alert">
      <p>加载失败：{{ store.error }}</p>
    </div>

    <template v-else-if="session">
      <header class="interview-detail__header">
        <h1 class="interview-detail__title">{{ session.jobTitle }}</h1>
        <div class="interview-detail__progress">
          <span class="interview-detail__progress-text">
            进度 {{ session.completedQuestions }}/{{ session.totalQuestions }} ({{ store.progressPercent }}%)
          </span>
          <div class="interview-detail__progress-bar">
            <div
              class="interview-detail__progress-fill"
              :style="{ width: `${store.progressPercent}%` }"
            />
          </div>
        </div>
      </header>

      <div class="interview-detail__filters">
        <select v-model="filterSkill" class="interview-detail__select" aria-label="按技能筛选">
          <option value="">全部技能</option>
          <option v-for="s in uniqueSkills" :key="s" :value="s">{{ s }}</option>
        </select>
        <select v-model="filterCategory" class="interview-detail__select" aria-label="按类别筛选">
          <option value="">全部类别</option>
          <option value="basic">基础题</option>
          <option value="project_deep_dive">项目深挖</option>
          <option value="scenario_design">场景设计</option>
        </select>
        <select v-model="filterDifficulty" class="interview-detail__select" aria-label="按难度筛选">
          <option value="">全部难度</option>
          <option value="easy">简单</option>
          <option value="medium">中等</option>
          <option value="hard">困难</option>
        </select>
      </div>

      <ul class="interview-detail__questions">
        <li
          v-for="q in filteredQuestions"
          :key="q.id"
          class="interview-detail__question"
        >
          <div class="interview-detail__question-header">
            <span class="interview-detail__question-skill">{{ q.skill }}</span>
            <span class="interview-detail__question-cat">{{ categoryLabel[q.category] || q.category }}</span>
            <span :class="['interview-detail__question-diff', `interview-detail__question-diff--${q.difficulty}`]">
              {{ difficultyLabel[q.difficulty] || q.difficulty }}
            </span>
            <span v-if="q.source === 'rag'" class="interview-detail__question-source">知识库</span>
          </div>

          <p class="interview-detail__question-text">{{ q.question }}</p>

          <details v-if="q.answerHint" class="interview-detail__hint">
            <summary class="interview-detail__hint-toggle">回答提示</summary>
            <p class="interview-detail__hint-text">{{ q.answerHint }}</p>
          </details>

          <ul v-if="q.followUps.length > 0" class="interview-detail__follow-ups">
            <li v-for="(fu, i) in q.followUps" :key="i" class="interview-detail__follow-up">
              追问：{{ fu }}
            </li>
          </ul>

          <div class="interview-detail__question-actions">
            <button
              type="button"
              :class="['interview-detail__status-btn', `interview-detail__status-btn--${statusTone(q.status)}`]"
              :disabled="q.status === 'completed' || q.status === 'skipped'"
              @click="cycleStatus(q.id, q.status)"
            >
              {{ statusLabel[q.status] || q.status }}
            </button>
            <button
              v-if="q.status === 'not_started' || q.status === 'practicing'"
              type="button"
              class="interview-detail__skip-btn"
              @click="skipQuestion(q.id)"
            >
              跳过
            </button>
          </div>

          <div class="interview-detail__notes">
            <textarea
              :value="getLocalNotes(q.id)"
              class="interview-detail__notes-input"
              placeholder="练习笔记…"
              rows="2"
              @input="setLocalNotes(q.id, ($event.target as HTMLTextAreaElement).value)"
              @blur="blurNotes(q.id)"
            />
          </div>
        </li>
      </ul>

      <p v-if="filteredQuestions.length === 0" class="interview-detail__no-match">
        没有匹配的题目，请调整筛选条件。
      </p>
    </template>
  </section>
</template>

<style scoped>
.interview-detail {
  padding: var(--space-lg);
  max-width: 900px;
  margin: 0 auto;
}

.interview-detail__loading,
.interview-detail__error {
  text-align: center;
  padding: var(--space-xl);
  color: var(--color-ink-subtle);
}

.interview-detail__header {
  margin-bottom: var(--space-md);
}

.interview-detail__title {
  font-size: var(--font-h2-size);
  font-weight: 600;
  margin-bottom: var(--space-xs);
}

.interview-detail__progress {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.interview-detail__progress-text {
  font-size: var(--font-caption-size);
  color: var(--color-ink-muted);
  white-space: nowrap;
}

.interview-detail__progress-bar {
  flex: 1;
  height: 6px;
  background: var(--color-surface-2);
  border-radius: 3px;
  overflow: hidden;
}

.interview-detail__progress-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.interview-detail__filters {
  display: flex;
  gap: var(--space-sm);
  margin-bottom: var(--space-md);
  flex-wrap: wrap;
}

.interview-detail__select {
  padding: var(--space-xs) var(--space-sm);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-sm);
  background: var(--color-surface-1);
  font-size: var(--font-caption-size);
}

.interview-detail__questions {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.interview-detail__question {
  background: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-md);
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.interview-detail__question-header {
  display: flex;
  gap: var(--space-xs);
  align-items: center;
  flex-wrap: wrap;
}

.interview-detail__question-skill {
  font-size: var(--font-caption-size);
  font-weight: 600;
  color: var(--color-primary);
  padding: 2px 6px;
  background: var(--color-surface-2);
  border-radius: var(--rounded-xs);
}

.interview-detail__question-cat {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

.interview-detail__question-diff {
  font-size: var(--font-caption-size);
  padding: 1px 6px;
  border-radius: var(--rounded-xs);
  font-weight: 500;
}

.interview-detail__question-diff--easy {
  background: #dcfce7;
  color: #16a34a;
}

.interview-detail__question-diff--medium {
  background: #fef9c3;
  color: #ca8a04;
}

.interview-detail__question-diff--hard {
  background: #fee2e2;
  color: #dc2626;
}

.interview-detail__question-source {
  font-size: var(--font-caption-size);
  color: var(--color-ink-tertiary);
  font-style: italic;
}

.interview-detail__question-text {
  font-size: var(--font-body-size);
  line-height: var(--font-body-line);
  margin: 0;
}

.interview-detail__hint {
  margin-top: var(--space-xxs);
}

.interview-detail__hint-toggle {
  font-size: var(--font-caption-size);
  color: var(--color-primary);
  cursor: pointer;
}

.interview-detail__hint-text {
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-muted);
  margin: var(--space-xxs) 0 0;
}

.interview-detail__follow-ups {
  list-style: none;
  padding: 0;
  margin: var(--space-xxs) 0 0;
}

.interview-detail__follow-up {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
  padding-left: var(--space-sm);
  border-left: 2px solid var(--color-hairline);
  margin-bottom: 2px;
}

.interview-detail__question-actions {
  display: flex;
  gap: var(--space-xs);
  margin-top: var(--space-xs);
}

.interview-detail__status-btn {
  font-size: var(--font-caption-size);
  padding: 4px 12px;
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-sm);
  cursor: pointer;
  font-weight: 500;
  transition: background 0.15s ease;
}

.interview-detail__status-btn:disabled {
  opacity: 0.6;
  cursor: default;
}

.interview-detail__status-btn--success {
  background: #dcfce7;
  color: #16a34a;
  border-color: #16a34a;
}

.interview-detail__status-btn--info {
  background: #dbeafe;
  color: #2563eb;
  border-color: #2563eb;
}

.interview-detail__status-btn--warning {
  background: #fef3c7;
  color: #d97706;
  border-color: #d97706;
}

.interview-detail__status-btn--neutral {
  background: var(--color-surface-2);
  color: var(--color-ink-subtle);
}

.interview-detail__skip-btn {
  font-size: var(--font-caption-size);
  padding: 4px 8px;
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-sm);
  background: transparent;
  color: var(--color-ink-muted);
  cursor: pointer;
}

.interview-detail__skip-btn:hover {
  background: var(--color-surface-2);
}

.interview-detail__notes {
  margin-top: var(--space-xs);
}

.interview-detail__notes-input {
  width: 100%;
  padding: var(--space-xs);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-sm);
  font-size: var(--font-caption-size);
  resize: vertical;
  font-family: inherit;
}

.interview-detail__no-match {
  text-align: center;
  color: var(--color-ink-tertiary);
  padding: var(--space-lg);
}
</style>
