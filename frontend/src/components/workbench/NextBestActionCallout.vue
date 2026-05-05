<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { Sparkles, Lock } from 'lucide-vue-next'

type State = 'ready' | 'blocked' | 'empty'

const HEADLINE_CHAR_LIMIT = 24

const props = withDefaults(
  defineProps<{
    state: State
    headline?: string
    actionLabel?: string
    ctaTo?: string
    waitingReason?: string
  }>(),
  {
    headline: '',
    actionLabel: '',
    ctaTo: '',
    waitingReason: '',
  },
)

const emit = defineEmits<{
  (e: 'action'): void
}>()

const isReady = computed(() => props.state === 'ready')
const isBlocked = computed(() => props.state === 'blocked')
const isEmpty = computed(() => props.state === 'empty')

const headlineText = computed(() => props.headline)

const headlineNeedsClamp = computed(
  () => headlineText.value.length > HEADLINE_CHAR_LIMIT,
)

const shouldRenderLink = computed(() => isReady.value && props.ctaTo.length > 0)

const ctaAriaLabel = computed(() => {
  const label = props.actionLabel || '继续'
  if (!headlineText.value) return label
  return `${label}：${headlineText.value}`
})

function onAction() {
  if (!isReady.value) return
  emit('action')
}
</script>

<template>
  <section
    class="nba"
    :class="{
      'nba--blocked': isBlocked,
      'nba--empty': isEmpty,
    }"
    role="region"
    aria-label="下一步建议"
  >
    <div v-if="!isEmpty" class="nba__icon-wrap" aria-hidden="true">
      <Sparkles v-if="isReady" :size="18" class="nba__icon" />
      <Lock v-else :size="18" class="nba__icon nba__icon--locked" />
    </div>

    <div class="nba__body">
      <p class="nba__eyebrow">下一步建议</p>

      <h2
        v-if="!isEmpty"
        data-testid="headline"
        class="nba__headline"
        :class="{ 'nba__headline--clamp': headlineNeedsClamp }"
      >
        {{ headlineText }}
      </h2>

      <p v-if="isEmpty" class="nba__empty">
        当前没有推荐行动，完成一次匹配分析后再回来查看。
      </p>

      <p v-if="isBlocked && waitingReason" class="nba__waiting">
        {{ waitingReason }}
      </p>

      <RouterLink
        v-if="shouldRenderLink"
        class="nba__cta"
        :to="ctaTo"
        :aria-label="ctaAriaLabel"
      >
        {{ actionLabel }}
      </RouterLink>

      <button
        v-else-if="!isEmpty"
        type="button"
        class="nba__cta"
        :disabled="isBlocked"
        :aria-label="ctaAriaLabel"
        @click="onAction"
      >
        {{ actionLabel }}
      </button>
    </div>
  </section>
</template>

<style scoped>
.nba {
  display: flex;
  gap: var(--space-md);
  padding: var(--space-lg);
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-xl);
  box-shadow: var(--shadow-sm);
}

.nba--blocked {
  background-color: var(--color-surface-2);
  border-color: rgba(245, 165, 36, 0.2);
}

.nba--empty {
  border-style: dashed;
  box-shadow: none;
}

.nba__icon-wrap {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--rounded-md);
  background-color: rgba(107, 117, 224, 0.12);
}

.nba--blocked .nba__icon-wrap {
  background-color: var(--color-risk-medium-bg);
}

.nba__icon {
  color: var(--color-primary);
}

.nba__icon--locked {
  color: var(--color-risk-medium);
}

.nba__body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.nba__eyebrow {
  margin: 0;
  font-size: var(--font-eyebrow-size);
  font-weight: var(--font-eyebrow-weight);
  letter-spacing: var(--font-eyebrow-letter);
  text-transform: uppercase;
  color: var(--color-ink-subtle);
}

.nba__headline {
  margin: 0;
  font-size: var(--font-headline-size);
  font-weight: var(--font-headline-weight);
  line-height: var(--font-headline-line);
  letter-spacing: var(--font-headline-letter);
  color: var(--color-ink);
}

.nba__headline--clamp {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
}

.nba__empty {
  margin: 0;
  color: var(--color-ink-subtle);
  font-size: var(--font-body-size);
  line-height: var(--font-body-line);
}

.nba__waiting {
  margin: 0;
  color: var(--color-risk-medium);
  font-size: var(--font-body-sm-size);
}

.nba__cta {
  align-self: flex-start;
  margin-top: var(--space-xs);
  background-color: var(--color-primary);
  color: var(--color-on-primary);
  border: 1px solid var(--color-primary);
  border-radius: var(--rounded-md);
  padding: 8px 14px;
  font-family: var(--font-family-sans);
  font-size: var(--font-button-size);
  font-weight: var(--font-button-weight);
  text-decoration: none;
  cursor: pointer;
  transition:
    background-color var(--motion-duration-fast) var(--motion-easing-standard),
    box-shadow var(--motion-duration-fast) var(--motion-easing-standard);
}

.nba__cta:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
  box-shadow: var(--shadow-sm);
}

.nba__cta:active:not(:disabled) {
  transform: scale(0.98);
}

.nba__cta:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

@media (max-width: 768px) {
  .nba {
    padding: var(--space-md);
  }

  .nba__headline {
    font-size: var(--font-card-title-size);
  }

  .nba__cta {
    padding: 12px 18px;
    min-height: 44px;
  }
}
</style>
