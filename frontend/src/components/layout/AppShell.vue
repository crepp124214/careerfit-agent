<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useAvailabilityStore } from '@/stores/availability'
import SideNav from './SideNav.vue'
import MobileNav from './MobileNav.vue'
import StatusBar from './StatusBar.vue'

const availability = useAvailabilityStore()

onMounted(() => {
  availability.probe()
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
  transition: opacity var(--motion-duration-base) var(--motion-easing-standard);
}

.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
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
