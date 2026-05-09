<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import LearningTasksView from './LearningTasksView.vue'
import InterviewListView from './InterviewListView.vue'
import InterviewBankView from './InterviewBankView.vue'

const route = useRoute()
const router = useRouter()

const TABS = [
  { key: 'learning', label: '学习任务' },
  { key: 'training', label: '模拟面试' },
  { key: 'bank', label: '题目生成' },
] as const

type TabKey = (typeof TABS)[number]['key']

const activeTab = computed<TabKey>(() => {
  const tab = route.query.tab as string
  if (tab === 'learning' || tab === 'training' || tab === 'bank') return tab
  return 'learning'
})

function switchTab(key: TabKey) {
  router.replace({ query: { ...route.query, tab: key } })
}
</script>

<template>
  <div class="interview-view">
    <header class="interview-view__tabs" role="tablist" aria-label="面试模块切换">
      <button
        v-for="tab in TABS"
        :key="tab.key"
        role="tab"
        :aria-selected="activeTab === tab.key"
        :aria-controls="`interview-panel-${tab.key}`"
        :class="[
          'interview-view__tab',
          { 'interview-view__tab--active': activeTab === tab.key },
        ]"
        @click="switchTab(tab.key)"
      >
        {{ tab.label }}
      </button>
    </header>

    <div
      v-if="activeTab === 'learning'"
      id="interview-panel-learning"
      role="tabpanel"
    >
      <LearningTasksView />
    </div>
    <div
      v-if="activeTab === 'training'"
      id="interview-panel-training"
      role="tabpanel"
    >
      <InterviewListView />
    </div>
    <div
      v-if="activeTab === 'bank'"
      id="interview-panel-bank"
      role="tabpanel"
    >
      <InterviewBankView />
    </div>
  </div>
</template>

<style scoped>
.interview-view__tabs {
  display: flex;
  gap: 0;
  border-bottom: 2px solid var(--color-hairline);
  margin-bottom: var(--space-lg);
}

.interview-view__tab {
  padding: var(--space-sm) var(--space-lg);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  font-size: var(--font-body-size);
  font-weight: 500;
  color: var(--color-ink-muted);
  cursor: pointer;
  transition:
    color var(--motion-duration-fast) var(--motion-easing-standard),
    border-bottom-color var(--motion-duration-fast) var(--motion-easing-standard),
    background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.interview-view__tab:hover {
  color: var(--color-ink);
  background-color: var(--color-surface-2);
}

.interview-view__tab--active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.interview-view__tab:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: -2px;
  border-radius: var(--rounded-sm);
}
</style>
