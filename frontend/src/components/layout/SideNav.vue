<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAvailabilityStore } from '@/stores/availability'
import {
  LayoutDashboard,
  Briefcase,
  FileText,
  Clock,
  GitCompare,
  BookOpen,
  Settings,
  Lock,
} from 'lucide-vue-next'

const ICON_MAP: Record<string, typeof LayoutDashboard> = {
  workspace: LayoutDashboard,
  jobs: Briefcase,
  resumes: FileText,
  history: Clock,
  'version-diff': GitCompare,
  learning: BookOpen,
  settings: Settings,
}

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
    <header class="side-nav__brand">
      <svg class="side-nav__logo" width="24" height="24" viewBox="0 0 24 24" aria-hidden="true">
        <rect x="2" y="2" width="20" height="20" rx="6" fill="var(--color-primary)" />
        <text x="12" y="16" text-anchor="middle" fill="var(--color-on-primary)" font-size="11" font-weight="600">CF</text>
      </svg>
      <span class="side-nav__brand-name">CareerFit</span>
    </header>
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
          <component :is="ICON_MAP[item.name]" :size="16" class="side-nav__icon" aria-hidden="true" />
          <span class="side-nav__label">{{ item.label }}</span>
          <Lock v-if="!isReady(item.cap)" :size="12" class="side-nav__lock" aria-hidden="true" />
        </router-link>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.side-nav {
  width: 200px;
  flex-shrink: 0;
  padding: 0;
  border-right: 1px solid var(--color-hairline);
  background-color: var(--color-surface-3);
  display: flex;
  flex-direction: column;
}

.side-nav__brand {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-md);
  height: 56px;
  border-bottom: 1px solid var(--color-hairline);
  flex-shrink: 0;
}

.side-nav__logo {
  flex-shrink: 0;
}

.side-nav__brand-name {
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
  color: var(--color-ink);
  letter-spacing: var(--font-card-title-letter);
}

.side-nav__list {
  list-style: none;
  margin: 0;
  padding: var(--space-xs) 0;
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
  gap: var(--space-sm);
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

.side-nav__icon {
  flex-shrink: 0;
  color: var(--color-ink-tertiary);
}

.side-nav__link--active .side-nav__icon {
  color: var(--color-primary);
}

.side-nav__label {
  flex: 1;
}

.side-nav__lock {
  flex-shrink: 0;
  color: var(--color-ink-tertiary);
  opacity: 0.6;
}
</style>
