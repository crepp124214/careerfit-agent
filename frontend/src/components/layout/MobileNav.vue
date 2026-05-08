<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
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
  Target,
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
  'interview-bank': Target,
  settings: Settings,
}

const availability = useAvailabilityStore()
const route = useRoute()
const open = ref(false)

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
  { label: '面试准备', route: '/learning', name: 'learning', cap: 'learning', group: 'insights' },
  { label: '面试训练', route: '/interview', name: 'interview', cap: 'interview', group: 'insights' },
  { label: '面试题库', route: '/interview-bank', name: 'interview-bank', cap: null, group: 'insights' },
  { label: '设置', route: '/settings', name: 'settings', cap: null, group: 'system' },
]

const GROUP_LABELS: Record<string, string> = {
  core: '核心',
  insights: '洞察',
  system: '',
}

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

watch(() => route.path, close)
</script>

<template>
  <nav class="mobile-nav" aria-label="主导航">
    <button
      class="mobile-nav__toggle"
      type="button"
      :aria-expanded="open"
      aria-controls="mobile-nav-drawer"
      aria-label="打开导航菜单"
      @click="toggle"
    >
      <Menu :size="20" aria-hidden="true" />
    </button>

    <Transition name="drawer">
      <div
        v-if="open"
        class="mobile-nav__backdrop"
        @click="close"
      >
        <div
          id="mobile-nav-drawer"
          class="mobile-nav__drawer"
          @click.stop
        >
          <div class="mobile-nav__drawer-header">
            <div class="mobile-nav__brand">
              <svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true">
                <rect x="2" y="2" width="20" height="20" rx="6" fill="var(--color-primary)" />
                <text x="12" y="16" text-anchor="middle" fill="var(--color-on-primary)" font-size="11" font-weight="600">CF</text>
              </svg>
              <span class="mobile-nav__brand-name">CareerFit</span>
            </div>
            <button class="mobile-nav__close" type="button" aria-label="关闭导航" @click="close">
              <X :size="18" aria-hidden="true" />
            </button>
          </div>

          <div class="mobile-nav__drawer-body">
            <template v-for="(item, idx) in ITEMS" :key="item.name">
              <div v-if="idx > 0 && ITEMS[idx - 1]?.group !== item.group" class="mobile-nav__divider" />
              <div v-if="idx === 0 || ITEMS[idx - 1]?.group !== item.group" class="mobile-nav__group-label">
                {{ GROUP_LABELS[item.group] }}
              </div>
              <router-link
                :to="item.route"
                class="mobile-nav__link"
                :class="{
                  'mobile-nav__link--active': route.name === item.name,
                  'mobile-nav__link--muted': !isReady(item.cap),
                }"
                @click="close"
              >
                <component :is="ICON_MAP[item.name]" :size="16" class="mobile-nav__icon" aria-hidden="true" />
                <span>{{ item.label }}</span>
                <Lock v-if="!isReady(item.cap)" :size="12" class="mobile-nav__lock" aria-hidden="true" />
              </router-link>
            </template>
          </div>
        </div>
      </div>
    </Transition>
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
    min-width: 44px;
    min-height: 44px;
    cursor: pointer;
    color: var(--color-ink);
  }

  .mobile-nav__backdrop {
    position: fixed;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.4);
    z-index: 100;
  }

  .mobile-nav__drawer {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    width: 280px;
    background-color: var(--color-surface-1);
    border-right: 1px solid var(--color-hairline);
    display: flex;
    flex-direction: column;
    overflow-y: auto;
  }

  .mobile-nav__drawer-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-md) var(--space-lg);
    border-bottom: 1px solid var(--color-hairline);
    min-height: 56px;
  }

  .mobile-nav__brand {
    display: flex;
    align-items: center;
    gap: var(--space-sm);
  }

  .mobile-nav__brand-name {
    font-size: var(--font-body-lg-size);
    font-weight: 600;
    color: var(--color-ink);
    letter-spacing: -0.3px;
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
    min-width: 44px;
    min-height: 44px;
    border-radius: var(--rounded-sm);
  }

  .mobile-nav__close:hover {
    background-color: var(--color-surface-2);
  }

  .mobile-nav__drawer-body {
    padding: var(--space-sm);
    display: flex;
    flex-direction: column;
    gap: 1px;
  }

  .mobile-nav__group-label {
    padding: var(--space-md) var(--space-sm) var(--space-xs);
    font-size: var(--font-eyebrow-size);
    font-weight: var(--font-eyebrow-weight);
    letter-spacing: var(--font-eyebrow-letter);
    text-transform: uppercase;
    color: var(--color-ink-tertiary);
  }

  .mobile-nav__divider {
    height: 1px;
    background-color: var(--color-hairline);
    margin: var(--space-xs) var(--space-sm);
  }

  .mobile-nav__link {
    display: flex;
    align-items: center;
    gap: var(--space-sm);
    padding: 8px var(--space-sm);
    min-height: 36px;
    text-decoration: none;
    color: var(--color-ink-muted);
    font-size: var(--font-body-size);
    border-radius: var(--rounded-md);
    transition:
      background-color var(--motion-duration-fast) var(--motion-easing-standard),
      color var(--motion-duration-fast) var(--motion-easing-standard);
  }

  .mobile-nav__link:hover {
    background-color: var(--color-surface-2);
    color: var(--color-ink);
  }

  .mobile-nav__link--active {
    background-color: rgba(107, 117, 224, 0.12);
    color: var(--color-primary);
    font-weight: 500;
  }

  .mobile-nav__link--muted {
    color: var(--color-ink-subtle);
  }

  .mobile-nav__icon {
    flex-shrink: 0;
    color: var(--color-ink-tertiary);
  }

  .mobile-nav__link--active .mobile-nav__icon {
    color: var(--color-primary);
  }

  .mobile-nav__lock {
    margin-left: auto;
    color: var(--color-ink-tertiary);
    opacity: 0.5;
  }

  .drawer-enter-active,
  .drawer-leave-active {
    transition: opacity var(--motion-duration-base) var(--motion-easing-standard);
  }

  .drawer-enter-from,
  .drawer-leave-to {
    opacity: 0;
  }

  .drawer-enter-active .mobile-nav__drawer,
  .drawer-leave-active .mobile-nav__drawer {
    transition: transform var(--motion-duration-base) var(--motion-easing-emphasized);
  }

  .drawer-enter-from .mobile-nav__drawer {
    transform: translateX(-100%);
  }

  .drawer-leave-to .mobile-nav__drawer {
    transform: translateX(-100%);
  }
}
</style>
