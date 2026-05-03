import { computed } from 'vue'
import { usePreferredReducedMotion } from '@vueuse/core'

export function useA11y() {
  const motionPreference = usePreferredReducedMotion()
  const prefersReducedMotion = computed(() => motionPreference.value === 'reduce')

  return { prefersReducedMotion }
}
