<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, watch } from 'vue'
import { X } from 'lucide-vue-next'

const props = withDefaults(
  defineProps<{
    open: boolean
    title?: string
    description?: string
    closable?: boolean
    width?: string
  }>(),
  {
    title: '',
    description: '',
    closable: true,
    width: '480px',
  },
)

const emit = defineEmits<{
  (e: 'close'): void
}>()

const dialogStyle = computed(() => ({ width: props.width, maxWidth: '90vw' }))

function handleBackdrop(event: MouseEvent) {
  if (!props.closable) return
  if (event.target === event.currentTarget) {
    emit('close')
  }
}

function handleKey(event: KeyboardEvent) {
  if (!props.open) return
  if (event.key === 'Escape' && props.closable) {
    emit('close')
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKey)
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKey)
})

watch(
  () => props.open,
  (next) => {
    if (typeof document === 'undefined') return
    document.body.style.overflow = next ? 'hidden' : ''
  },
)
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="props.open" class="modal-backdrop" @mousedown="handleBackdrop">
        <div
          class="modal"
          role="dialog"
          aria-modal="true"
          :aria-label="props.title || undefined"
          :style="dialogStyle"
        >
          <header v-if="props.title || props.closable" class="modal__header">
            <div>
              <h2 v-if="props.title" class="modal__title">{{ props.title }}</h2>
              <p v-if="props.description" class="modal__description">{{ props.description }}</p>
            </div>
            <button
              v-if="props.closable"
              type="button"
              class="modal__close"
              aria-label="关闭"
              @click="emit('close')"
            >
              <X :size="18" aria-hidden="true" />
            </button>
          </header>
          <div class="modal__body">
            <slot />
          </div>
          <footer v-if="$slots.footer" class="modal__footer">
            <slot name="footer" />
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-overlay);
  padding: var(--space-md);
}

.modal {
  background-color: var(--color-surface-4);
  color: var(--color-ink);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  padding: var(--space-lg);
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  max-height: 80vh;
  overflow: auto;
}

.modal__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-md);
}

.modal__title {
  margin: 0;
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
  line-height: var(--font-card-title-line);
}

.modal__description {
  margin: 4px 0 0;
  color: var(--color-ink-subtle);
  font-size: var(--font-body-sm-size);
}

.modal__close {
  background: transparent;
  border: 0;
  color: var(--color-ink-muted);
  font-size: 22px;
  cursor: pointer;
  line-height: 1;
  padding: 4px 8px;
  border-radius: var(--rounded-sm);
  transition: background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.modal__close:hover {
  background-color: var(--color-surface-2);
}

.modal__body {
  font-size: var(--font-body-size);
  line-height: var(--font-body-line);
}

.modal__footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-xs);
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity var(--motion-duration-base) var(--motion-easing-emphasized);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal,
.modal-leave-active .modal {
  transition:
    opacity var(--motion-duration-base) var(--motion-easing-emphasized),
    transform var(--motion-duration-base) var(--motion-easing-emphasized);
}

.modal-enter-from .modal {
  opacity: 0;
  transform: scale(0.96) translateY(8px);
}

.modal-leave-to .modal {
  opacity: 0;
  transform: scale(0.98) translateY(-4px);
}
</style>
