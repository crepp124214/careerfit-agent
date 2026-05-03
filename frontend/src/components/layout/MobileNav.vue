<script setup lang="ts">
import { ref } from 'vue'
import { useAvailabilityStore } from '@/stores/availability'
const availability = useAvailabilityStore()
const open = ref(false)

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
      <span class="mobile-nav__hamburger" aria-hidden="true">
        <span class="mobile-nav__bar" />
        <span class="mobile-nav__bar" />
        <span class="mobile-nav__bar" />
      </span>
    </button>

    <div
      v-if="open"
      id="mobile-nav-menu"
      class="mobile-nav__overlay"
      @click.self="close"
    >
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
            <span>{{ item.label }}</span>
            <span v-if="!isReady(item.cap)" aria-hidden="true">🔒</span>
          </router-link>
        </li>
      </ul>
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
    background: none;
    border: 1px solid var(--color-hairline);
    border-radius: var(--rounded-md);
    padding: var(--space-xs);
    cursor: pointer;
  }

  .mobile-nav__hamburger {
    display: flex;
    flex-direction: column;
    gap: 3px;
  }

  .mobile-nav__bar {
    display: block;
    width: 18px;
    height: 2px;
    background-color: var(--color-ink);
  }

  .mobile-nav__overlay {
    position: fixed;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.4);
    z-index: 100;
  }

  .mobile-nav__list {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    background-color: var(--color-canvas);
    border-bottom: 1px solid var(--color-hairline);
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
    justify-content: space-between;
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
}
</style>
