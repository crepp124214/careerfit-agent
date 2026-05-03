import { defineStore } from 'pinia'
import { useLocalStorageRef } from '@/composables/useLocalStorageRef'

export type Theme = 'system' | 'dark' | 'light'
export type Density = 'compact' | 'relaxed'

export const usePreferencesStore = defineStore('preferences', () => {
  const theme = useLocalStorageRef<Theme>('careerfit:pref:theme', 'system')
  const density = useLocalStorageRef<Density>('careerfit:pref:density', 'compact')
  const recentLimit = useLocalStorageRef<number>('careerfit:pref:recentLimit', 10)

  return { theme, density, recentLimit }
})
