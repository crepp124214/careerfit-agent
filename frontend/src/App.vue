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
:root {
  color-scheme: dark;
  font-family:
    Inter,
    'PingFang SC',
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    Roboto,
    sans-serif;
  background-color: #010102;
  color: #f7f8f8;
}

body {
  margin: 0;
}

.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-shell__header {
  padding: 16px 24px;
  border-bottom: 1px solid rgba(247, 248, 248, 0.08);
}

.app-shell__brand {
  font-weight: 600;
  letter-spacing: 0.02em;
}

.app-shell__main {
  flex: 1;
  padding: 24px;
}

.view-placeholder h1 {
  margin: 0 0 12px;
  font-size: 24px;
  font-weight: 600;
}

.view-placeholder p {
  margin: 4px 0;
  color: rgba(247, 248, 248, 0.72);
}
</style>
