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
  MessageSquare,
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
  interview: MessageSquare,
  settings: Settings,
}

interface NavItem {
  label: string
  route: string
  name: string
  cap: 'jobs' | 'resumes' | 'analysis' | 'reports' | 'agentRuns' | 'learning' | 'interview' | null
  group: 'core' | 'insights' | 'system'
}

const ITEMS: NavItem[] = [
  { label: '工作台', route: '/', name: 'workspace', cap: null, group: 'core' },
  { label: '岗位', route: '/jobs', name: 'jobs', cap: 'jobs', group: 'core' },
  { label: '简历', route: '/resumes', name: 'resumes', cap: 'resumes', group: 'core' },
  { label: '历史', route: '/history', name: 'history', cap: 'reports', group: 'insights' },
  { label: '对比', route: '/diff', name: 'version-diff', cap: 'reports', group: 'insights' },
  { label: '学习', route: '/learning', name: 'learning', cap: 'learning', group: 'insights' },
  { label: '面试', route: '/interview', name: 'interview', cap: 'interview', group: 'insights' },
  { label: '设置', route: '/settings', name: 'settings', cap: null, group: 'system' },
]

const GROUP_LABELS: Record<string, string> = {
  core: '核心',
  insights: '洞察',
  system: '',
}

const groupedItems = computed(() => {
  const groups: Record<string, NavItem[]> = {}
  for (const item of ITEMS) {
    const key = item.group
    if (!groups[key]) groups[key] = []
    groups[key].push(item)
  }
  return groups
})

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
      <div class="side-nav__logo-wrap">
        <svg class="side-nav__logo" width="22" height="22" viewBox="0 0 24 24" aria-hidden="true">
          <rect x="2" y="2" width="20" height="20" rx="6" fill="var(--color-primary)" />
          <text x="12" y="16" text-anchor="middle" fill="var(--color-on-primary)" font-size="11" font-weight="600">CF</text>
        </svg>
      </div>
      <span class="side-nav__brand-name">CareerFit</span>
    </header>

    <div class="side-nav__scroll">
      <template v-for="(items, group) in groupedItems" :key="group">
        <div v-if="GROUP_LABELS[group]" class="side-nav__group-label">
          {{ GROUP_LABELS[group] }}
        </div>
        <ul class="side-nav__list">
          <li v-for="item in items" :key="item.name" class="side-nav__item">
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
        <div class="side-nav__divider" />
      </template>
    </div>
  </nav>
</template>

<style scoped>
.side-nav {
  width: 220px;
  flex-shrink: 0;
  border-right: 1px solid var(--color-hairline);
  background-color: var(--color-surface-1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.side-nav__brand {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-lg);
  height: 56px;
  border-bottom: 1px solid var(--color-hairline);
  flex-shrink: 0;
}

.side-nav__logo-wrap {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--rounded-md);
  background-color: rgba(107, 117, 224, 0.12);
  flex-shrink: 0;
}

.side-nav__logo {
  flex-shrink: 0;
}

.side-nav__brand-name {
  font-size: var(--font-body-lg-size);
  font-weight: 600;
  color: var(--color-ink);
  letter-spacing: -0.3px;
}

.side-nav__scroll {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-sm) var(--space-sm);
}

.side-nav__group-label {
  padding: var(--space-md) var(--space-sm) var(--space-xs);
  font-size: var(--font-eyebrow-size);
  font-weight: var(--font-eyebrow-weight);
  letter-spacing: var(--font-eyebrow-letter);
  text-transform: uppercase;
  color: var(--color-ink-tertiary);
}

.side-nav__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.side-nav__item {
  margin: 0;
}

.side-nav__link {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 8px var(--space-sm);
  min-height: 36px;
  text-decoration: none;
  color: var(--color-ink-muted);
  font-size: var(--font-body-size);
  line-height: var(--font-body-line);
  border-radius: var(--rounded-md);
  transition:
    background-color var(--motion-duration-fast) var(--motion-easing-standard),
    color var(--motion-duration-fast) var(--motion-easing-standard);
}

.side-nav__link:hover {
  background-color: var(--color-surface-2);
  color: var(--color-ink);
}

.side-nav__link--active {
  background-color: rgba(107, 117, 224, 0.12);
  color: var(--color-primary);
  font-weight: 500;
}

.side-nav__link--active:hover {
  background-color: rgba(107, 117, 224, 0.18);
  color: var(--color-primary);
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
  transition: color var(--motion-duration-fast) var(--motion-easing-standard);
}

.side-nav__link:hover .side-nav__icon {
  color: var(--color-ink-subtle);
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
  opacity: 0.5;
}

.side-nav__divider {
  height: 1px;
  background-color: var(--color-hairline);
  margin: var(--space-xs) var(--space-sm);
}

@media (max-width: 768px) {
  .side-nav {
    display: none;
  }
}
</style>
