import { ref, watch, type Ref } from 'vue'

const NAMESPACE = 'careerfit:pref:'
const MAX_STRING_LENGTH = 1024
const BLOCKED_KEYS = ['raw_jd', 'raw_resume']

function isBlocked(value: unknown): boolean {
  if (typeof value === 'string' && value.length > MAX_STRING_LENGTH) {
    console.warn('[useLocalStorageRef] value exceeds 1KB limit, write rejected')
    return true
  }
  if (typeof value === 'object' && value !== null) {
    const keys = Object.keys(value as Record<string, unknown>)
    for (const key of keys) {
      if (BLOCKED_KEYS.includes(key)) {
        console.warn(`[useLocalStorageRef] blocked key "${key}" detected, write rejected`)
        return true
      }
    }
  }
  return false
}

function tryGet(key: string): string | null {
  try {
    return localStorage.getItem(key)
  } catch {
    return null
  }
}

function trySet(key: string, value: string): boolean {
  try {
    localStorage.setItem(key, value)
    return true
  } catch {
    return false
  }
}

export function useLocalStorageRef<T>(key: string, defaultValue: T): Ref<T> {
  const namespaced = key.startsWith(NAMESPACE)
  if (!namespaced) {
    console.warn(`[useLocalStorageRef] key "${key}" does not use namespace "${NAMESPACE}", falling back to memory`)
  }

  let initial: T = defaultValue
  if (namespaced) {
    const raw = tryGet(key)
    if (raw !== null) {
      try {
        initial = JSON.parse(raw) as T
      } catch {
        initial = defaultValue
      }
    }
  }

  const r = ref<T>(initial) as Ref<T>

  watch(
    r,
    (newValue) => {
      if (isBlocked(newValue)) {
        return
      }
      if (namespaced) {
        trySet(key, JSON.stringify(newValue))
      }
    },
    { deep: true },
  )

  return r
}
