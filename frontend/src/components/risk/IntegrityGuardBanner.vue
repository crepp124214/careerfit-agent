<script setup lang="ts">
withDefaults(
  defineProps<{
    blockedCount?: number
    summary?: string
  }>(),
  {
    blockedCount: 0,
    summary: '',
  },
)
</script>

<template>
  <section class="integrity-guard-banner" role="alert">
    <div class="integrity-guard-banner__icon" aria-hidden="true">⚠️</div>
    <div class="integrity-guard-banner__body">
      <h3 class="integrity-guard-banner__title">
        Integrity Guard 拦截了 {{ blockedCount }} 条简历建议
      </h3>
      <p v-if="summary" class="integrity-guard-banner__summary">
        {{ summary }}
      </p>
      <p class="integrity-guard-banner__hint">
        被拦截的建议仍会展示，但会标记为高风险，请务必人工复核。
      </p>
    </div>
  </section>
</template>

<style scoped>
.integrity-guard-banner {
  display: flex;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  background-color: var(--color-risk-high-bg);
  border: 1px solid var(--color-risk-high);
  border-radius: var(--rounded-lg);
  color: var(--color-risk-high);
}

.integrity-guard-banner__icon {
  font-size: 20px;
  line-height: 1;
  margin-top: 2px;
}

.integrity-guard-banner__body {
  display: flex;
  flex-direction: column;
  gap: var(--space-xxs);
}

.integrity-guard-banner__title {
  margin: 0;
  font-size: var(--font-body-size);
  font-weight: 600;
  line-height: var(--font-body-line);
}

.integrity-guard-banner__summary {
  margin: 0;
  color: var(--color-ink);
  font-size: var(--font-body-sm-size);
}

.integrity-guard-banner__hint {
  margin: 0;
  color: var(--color-ink-muted);
  font-size: var(--font-caption-size);
}
</style>
