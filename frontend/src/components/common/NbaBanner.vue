<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { Sparkles } from 'lucide-vue-next'

defineProps<{
  label: string
  description?: string
  ctaTo?: string
  ctaLabel?: string
}>()

const emit = defineEmits<{
  (e: 'cta-click'): void
}>()
</script>

<template>
  <aside class="nba-banner" role="complementary" aria-label="下一步建议">
    <Sparkles :size="16" class="nba-banner__icon" aria-hidden="true" />
    <div class="nba-banner__body">
      <p class="nba-banner__label">{{ label }}</p>
      <p v-if="description" class="nba-banner__desc">{{ description }}</p>
    </div>
    <RouterLink
      v-if="ctaTo"
      :to="ctaTo"
      class="nba-banner__cta"
    >
      {{ ctaLabel || '前往' }}
    </RouterLink>
    <button
      v-else
      type="button"
      class="nba-banner__cta"
      @click="emit('cta-click')"
    >
      {{ ctaLabel || '继续' }}
    </button>
  </aside>
</template>

<style scoped>
.nba-banner {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  margin-top: var(--space-lg);
  background-color: rgba(107, 117, 224, 0.08);
  border: 1px solid rgba(107, 117, 224, 0.2);
  border-radius: var(--rounded-md);
}

.nba-banner__icon {
  flex-shrink: 0;
  color: var(--color-primary);
}

.nba-banner__body {
  flex: 1;
}

.nba-banner__label {
  margin: 0;
  font-size: var(--font-body-sm-size);
  font-weight: 500;
  color: var(--color-ink);
}

.nba-banner__desc {
  margin: 2px 0 0;
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

.nba-banner__cta {
  flex-shrink: 0;
  padding: 6px 12px;
  background-color: var(--color-primary);
  color: var(--color-on-primary);
  border: none;
  border-radius: var(--rounded-md);
  font-size: var(--font-button-size);
  font-weight: var(--font-button-weight);
  text-decoration: none;
  cursor: pointer;
  transition: background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.nba-banner__cta:hover {
  background-color: var(--color-primary-hover);
}
</style>
