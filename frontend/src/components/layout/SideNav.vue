<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAvailabilityStore } from '@/stores/availability'

interface NavItem {
  label: string
  route: string
  name: string
  cap: 'jobs' | 'resumes' | 'analysis' | 'reports' | 'agentRuns' | 'learning' | null
}

const ITEMS: NavItem[] = [
  { label: '工作台', route: '/', name: 'workspace', cap: null },
  { label: '岗位', route: '/jobs', name: 'jobs', cap: 'jobs' },
  { label: '简历', route: '/resumes', name: 'resumes', cap: 'resumes' },
  { label: '历史', route: '/history', name: 'history', cap: 'reports' },
  { label: '对比', route: '/diff', name: 'version-diff', cap: 'reports' },
  { label: '学习', route: '/learning', name: 'learning', cap: 'learning' },
  { label: '设置', route: '/settings', name: 'settings', cap: null },
]

const route = useRoute()
const availability = useAvailabilityStore()

function isReady(cap: NavItem['cap']) {
  if (cap === null) return true
  return availability.states[cap] === 'ready'
}

const activeName = computed(() => route.name as string | undefined)
</script>

<template>
  <nav class="side-nav" aria-label="主导航">
    <ul class="side-nav__list">
      <li v-for="item in ITEMS" :key="item.name" class="side-nav__item">
        <router-link
          :to="item.route"
          :class="[
            'side-nav__link',
            {
              'side-nav__link--active': activeName === item.name,
              'side-nav__link--muted': !isReady(item.cap),
            },
          ]"
        >
          <span class="side-nav__label">{{ item.label }}</span>
          <span v-if="!isReady(item.cap)" class="side-nav__lock" aria-hidden="true">🔒</span>
        </router-link>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.side-nav {
  width: 180px;
  flex-shrink: 0;
  padding: var(--space-md) 0;
  border-right: 1px solid var(--color-hairline);
}

.side-nav__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.side-nav__item {
  margin: 0;
}

.side-nav__link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-xs);
  padding: 8px var(--space-md);
  text-decoration: none;
  color: var(--color-ink);
  font-size: var(--font-body-size);
  line-height: var(--font-body-line);
  border-radius: 0 var(--rounded-sm) var(--rounded-sm) 0;
  transition:
    background-color var(--motion-duration-fast) var(--motion-easing-standard),
    color var(--motion-duration-fast) var(--motion-easing-standard);
}

.side-nav__link:hover {
  background-color: var(--color-surface-2);
}

.side-nav__link--active {
  background-color: var(--color-surface-2);
  color: var(--color-ink);
  font-weight: 500;
}

.side-nav__link--muted {
  color: var(--color-ink-subtle);
}

.side-nav__link--muted:hover {
  color: var(--color-ink-muted);
}

.side-nav__lock {
  font-size: 10px;
  opacity: 0.6;
}
</style>
