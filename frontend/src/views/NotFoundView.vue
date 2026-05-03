<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { FileQuestion, ArrowLeft } from 'lucide-vue-next'
</script>

<template>
  <section class="not-found" data-view="not-found" role="main" aria-label="页面不存在">
    <div class="not-found__card animate-in">
      <FileQuestion :size="48" class="not-found__icon" aria-hidden="true" />
      <h1 class="not-found__title">页面不存在</h1>
      <p class="not-found__detail">请求的路径未匹配任何路由。</p>
      <RouterLink to="/" class="not-found__back">
        <ArrowLeft :size="16" aria-hidden="true" />
        返回工作台
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.not-found {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

.not-found__card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-xxl);
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-xl);
  box-shadow: var(--shadow-sm);
  text-align: center;
  max-width: 400px;
}

.not-found__icon {
  color: var(--color-ink-tertiary);
}

.not-found__title {
  margin: 0;
  font-size: var(--font-headline-size);
  font-weight: var(--font-headline-weight);
  line-height: var(--font-headline-line);
}

.not-found__detail {
  margin: 0;
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-subtle);
  line-height: var(--font-body-sm-line);
}

.not-found__back {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-md);
  background-color: var(--color-primary);
  color: var(--color-on-primary);
  border-radius: var(--rounded-md);
  font-size: var(--font-body-size);
  font-weight: 500;
  text-decoration: none;
  transition:
    background-color var(--motion-duration-fast) var(--motion-easing-standard),
    box-shadow var(--motion-duration-fast) var(--motion-easing-standard);
}

.not-found__back:hover {
  background-color: var(--color-primary-hover);
}

.not-found__back:focus-visible {
  outline: var(--focus-ring-width) solid var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
}
</style>
