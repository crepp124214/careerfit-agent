<script setup lang="ts">
import { RouterView } from 'vue-router'
import SideNav from './SideNav.vue'
import MobileNav from './MobileNav.vue'
import StatusBar from './StatusBar.vue'
</script>

<template>
  <div class="app-shell">
    <MobileNav class="app-shell__mobile-nav" />
    <SideNav class="app-shell__nav" />
    <div class="app-shell__content">
      <main class="app-shell__main">
        <RouterView />
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
