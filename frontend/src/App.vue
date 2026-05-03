<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="app-shell">
    <header class="app-shell__header">
      <span class="app-shell__brand">CareerFit Agent</span>
    </header>
    <main class="app-shell__main">
      <RouterView />
    </main>
  </div>
</template>

<style>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--color-canvas);
  color: var(--color-ink);
}

.app-shell__header {
  padding: var(--space-md) var(--space-lg);
  border-bottom: 1px solid var(--color-hairline);
}

.app-shell__brand {
  font-weight: var(--font-card-title-weight);
  letter-spacing: var(--font-eyebrow-letter);
}

.app-shell__main {
  flex: 1;
  padding: var(--space-lg);
}

.view-placeholder h1 {
  margin: 0 0 var(--space-sm);
  font-size: var(--font-headline-size);
  font-weight: var(--font-headline-weight);
  line-height: var(--font-headline-line);
  letter-spacing: var(--font-headline-letter);
}

.view-placeholder p {
  margin: var(--space-xxs) 0;
  color: var(--color-ink-muted);
}
</style>
