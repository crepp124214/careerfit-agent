<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

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

const headlineClasses = computed(() => {
  return [
    'next-best-action__headline',
    headlineNeedsClamp.value ? 'next-best-action__headline--clamp' : '',
  ].filter(Boolean)
})

function onAction() {
  if (!isReady.value) return
  emit('action')
}
</script>

<template>
  <section
    class="next-best-action"
    :class="{
      'next-best-action--blocked': isBlocked,
      'next-best-action--empty': isEmpty,
    }"
    role="region"
    aria-label="下一步建议"
  >
    <span
      v-if="!isEmpty"
      data-testid="accent"
      class="next-best-action__accent next-best-action__leading-accent"
      aria-hidden="true"
    />
    <div class="next-best-action__body">
      <p class="next-best-action__eyebrow">下一步建议</p>

      <h2
        v-if="!isEmpty"
        data-testid="headline"
        :class="headlineClasses"
      >
        {{ headlineText }}
      </h2>

      <p v-if="isEmpty" class="next-best-action__empty">
        当前没有推荐行动，完成一次匹配分析后再回来查看。
      </p>

      <p v-if="isBlocked && waitingReason" class="next-best-action__waiting">
        {{ waitingReason }}
      </p>

      <RouterLink
        v-if="shouldRenderLink"
        class="next-best-action__cta"
        :to="ctaTo"
        :aria-label="ctaAriaLabel"
      >
        {{ actionLabel }}
      </RouterLink>

      <button
        v-else-if="!isEmpty"
        type="button"
        class="next-best-action__cta"
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
.next-best-action {
  position: relative;
  display: flex;
  gap: var(--space-md);
  padding: var(--space-lg) 28px;
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  overflow: hidden;
}

.next-best-action__accent {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 4px;
  background-color: var(--color-primary);
}

.next-best-action--blocked .next-best-action__accent {
  background-color: var(--color-risk-medium);
}

.next-best-action--empty {
  border-style: dashed;
}

.next-best-action__body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  padding-left: var(--space-sm);
}

.next-best-action__eyebrow {
  margin: 0;
  font-size: var(--font-eyebrow-size);
  font-weight: var(--font-eyebrow-weight);
  letter-spacing: var(--font-eyebrow-letter);
  text-transform: uppercase;
  color: var(--color-ink-subtle);
}

.next-best-action__headline {
  margin: 0;
  font-size: var(--font-headline-size);
  font-weight: var(--font-headline-weight);
  line-height: var(--font-headline-line);
  letter-spacing: var(--font-headline-letter);
  color: var(--color-ink);
}

.next-best-action__headline--clamp {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
}

.next-best-action__empty {
  margin: 0;
  color: var(--color-ink-subtle);
  font-size: var(--font-body-size);
  line-height: var(--font-body-line);
}

.next-best-action__waiting {
  margin: 0;
  color: var(--color-risk-medium);
  font-size: var(--font-body-sm-size);
}

.next-best-action__cta {
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
  transition: background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.next-best-action__cta:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
}

.next-best-action__cta:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}
</style>
