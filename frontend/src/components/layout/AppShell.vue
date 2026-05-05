<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { RouterView } from 'vue-router'
import { useAvailabilityStore } from '@/stores/availability'
import { usePreferencesStore } from '@/stores/preferences'
import SideNav from './SideNav.vue'
import MobileNav from './MobileNav.vue'
import StatusBar from './StatusBar.vue'

const availability = useAvailabilityStore()
const prefs = usePreferencesStore()

function applyTheme(theme: string) {
  const root = document.documentElement
  if (theme === 'light') {
    root.setAttribute('data-theme', 'light')
  } else if (theme === 'dark') {
    root.removeAttribute('data-theme')
  } else {
    // system: 跟随系统偏好
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    if (prefersDark) {
      root.removeAttribute('data-theme')
    } else {
      root.setAttribute('data-theme', 'light')
    }
  }
}

// 监听主题变化
watch(() => prefs.theme, applyTheme, { immediate: true })

// 监听系统主题变化
onMounted(() => {
  availability.probe()
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  mediaQuery.addEventListener('change', () => {
    if (prefs.theme === 'system') {
      applyTheme('system')
    }
  })
})
</script>

<template>
  <div class="app-shell">
    <MobileNav class="app-shell__mobile-nav" />
    <SideNav class="app-shell__nav" />
    <div class="app-shell__content">
      <main class="app-shell__main">
        <RouterView v-slot="{ Component }">
          <Transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </main>
      <StatusBar />
    </div>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  background-color: var(--color-canvas);
  color: var(--color-ink);
}

.app-shell__mobile-nav {
  display: none;
}

.app-shell__content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.app-shell__main {
  flex: 1;
  padding: var(--space-lg);
  overflow: auto;
}

.page-fade-enter-active,
.page-fade-leave-active {
  transition:
    opacity var(--motion-duration-slow) var(--motion-easing-emphasized),
    transform var(--motion-duration-slow) var(--motion-easing-emphasized);
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(4px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .app-shell {
    flex-direction: column;
  }

  .app-shell__nav {
    display: none;
  }

  .app-shell__mobile-nav {
    display: block;
    padding: var(--space-sm);
    border-bottom: 1px solid var(--color-hairline);
  }
}
</style>
