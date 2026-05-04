<script setup lang="ts">
import { ref } from 'vue'
import { useAvailabilityStore } from '@/stores/availability'
import {
  Menu,
  X,
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

const availability = useAvailabilityStore()
const open = ref(false)

interface NavItem {
  label: string
  route: string
  name: string
  cap: 'jobs' | 'resumes' | 'analysis' | 'reports' | 'agentRuns' | 'learning' | 'interview' | null
}

const ITEMS: NavItem[] = [
  { label: '工作台', route: '/', name: 'workspace', cap: null },
  { label: '岗位', route: '/jobs', name: 'jobs', cap: 'jobs' },
  { label: '简历', route: '/resumes', name: 'resumes', cap: 'resumes' },
  { label: '历史', route: '/history', name: 'history', cap: 'reports' },
  { label: '对比', route: '/diff', name: 'version-diff', cap: 'reports' },
  { label: '学习', route: '/learning', name: 'learning', cap: 'learning' },
  { label: '面试', route: '/interview', name: 'interview', cap: 'interview' },
  { label: '设置', route: '/settings', name: 'settings', cap: null },
]

function isReady(cap: NavItem['cap']) {
  if (cap === null) return true
  return availability.states[cap] === 'ready'
}

function toggle() {
  open.value = !open.value
}

function close() {
  open.value = false
}
</script>

<template>
  <nav class="mobile-nav" aria-label="主导航">
    <button
      class="mobile-nav__toggle"
      type="button"
      :aria-expanded="open"
      aria-controls="mobile-nav-menu"
      aria-label="打开导航菜单"
      @click="toggle"
    >
      <Menu :size="20" aria-hidden="true" />
    </button>

    <div
      v-if="open"
      id="mobile-nav-menu"
      class="mobile-nav__overlay"
      @click.self="close"
    >
      <div class="mobile-nav__panel">
        <div class="mobile-nav__panel-header">
          <span class="mobile-nav__panel-title">CareerFit</span>
          <button class="mobile-nav__close" type="button" aria-label="关闭导航" @click="close">
            <X :size="18" aria-hidden="true" />
          </button>
        </div>
        <ul class="mobile-nav__list" role="menu">
          <li
            v-for="item in ITEMS"
            :key="item.name"
            class="mobile-nav__item"
            role="none"
          >
            <router-link
              :to="item.route"
              class="mobile-nav__link"
              :class="{ 'mobile-nav__link--muted': !isReady(item.cap) }"
              role="menuitem"
              @click="close"
            >
              <component :is="ICON_MAP[item.name]" :size="16" class="mobile-nav__icon" aria-hidden="true" />
              <span>{{ item.label }}</span>
              <Lock v-if="!isReady(item.cap)" :size="12" class="mobile-nav__lock" aria-hidden="true" />
            </router-link>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.mobile-nav {
  display: none;
}

@media (max-width: 768px) {
  .mobile-nav {
    display: block;
  }

  .mobile-nav__toggle {
    display: flex;
    align-items: center;
    justify-content: center;
    background: none;
    border: 1px solid var(--color-hairline);
    border-radius: var(--rounded-md);
    padding: var(--space-xs);
    cursor: pointer;
    color: var(--color-ink);
  }

  .mobile-nav__overlay {
    position: fixed;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.4);
    z-index: 100;
  }

  .mobile-nav__panel {
    background-color: var(--color-surface-3);
    border-bottom: 1px solid var(--color-hairline);
  }

  .mobile-nav__panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-md);
    border-bottom: 1px solid var(--color-hairline);
  }

  .mobile-nav__panel-title {
    font-size: var(--font-card-title-size);
    font-weight: var(--font-card-title-weight);
    color: var(--color-ink);
  }

  .mobile-nav__close {
    display: flex;
    align-items: center;
    justify-content: center;
    background: none;
    border: 0;
    color: var(--color-ink-muted);
    cursor: pointer;
    padding: var(--space-xxs);
    border-radius: var(--rounded-sm);
  }

  .mobile-nav__close:hover {
    background-color: var(--color-surface-2);
  }

  .mobile-nav__list {
    list-style: none;
    margin: 0;
    padding: var(--space-md);
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .mobile-nav__link {
    display: flex;
    align-items: center;
    gap: var(--space-sm);
    padding: var(--space-sm) var(--space-md);
    text-decoration: none;
    color: var(--color-ink);
    font-size: var(--font-body-size);
    border-radius: var(--rounded-md);
  }

  .mobile-nav__link:hover {
    background-color: var(--color-surface-2);
  }

  .mobile-nav__link--muted {
    color: var(--color-ink-subtle);
  }

  .mobile-nav__icon {
    flex-shrink: 0;
    color: var(--color-ink-tertiary);
  }

  .mobile-nav__lock {
    margin-left: auto;
    color: var(--color-ink-tertiary);
    opacity: 0.6;
  }
}
</style>
