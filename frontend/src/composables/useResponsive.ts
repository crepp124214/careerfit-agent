import { computed } from 'vue'
import { useWindowSize } from '@vueuse/core'

export function useResponsive() {
  const { width } = useWindowSize()

  const isMobile = computed(() => width.value < 768)
  const isTablet = computed(() => width.value >= 768 && width.value < 1280)
  const isDesktop = computed(() => width.value >= 1280)

  return { isMobile, isTablet, isDesktop, width }
}
