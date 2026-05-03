import { describe, expect, it, vi, beforeEach } from 'vitest'
import { nextTick } from 'vue'
import { setActivePinia, createPinia } from 'pinia'
import { useLocalStorageRef } from '@/composables/useLocalStorageRef'

describe('useLocalStorageRef', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.restoreAllMocks()
  })

  describe('命名空间', () => {
    it('接受 careerfit:pref:* 命名空间的 key', () => {
      const ref = useLocalStorageRef('careerfit:pref:theme', 'light')
      expect(ref.value).toBe('light')
    })

    it('拒绝非命名空间 key 并回退到内存', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
      const ref = useLocalStorageRef('theme', 'light')
      expect(ref.value).toBe('light')
      expect(warn).toHaveBeenCalled()
      warn.mockRestore()
    })
  })

  describe('序列化对称', () => {
    it('写入对象后读取一致', async () => {
      const ref = useLocalStorageRef('careerfit:pref:layout', { density: 'compact' })
      ref.value = { density: 'relaxed' }
      await nextTick()
      const stored = JSON.parse(localStorage.getItem('careerfit:pref:layout')!)
      expect(stored).toEqual({ density: 'relaxed' })
    })

    it('从 localStorage 恢复已有值', () => {
      localStorage.setItem('careerfit:pref:theme', JSON.stringify('dark'))
      const ref = useLocalStorageRef('careerfit:pref:theme', 'light')
      expect(ref.value).toBe('dark')
    })
  })

  describe('白名单校验', () => {
    it('拒绝写入 raw_jd 字段并发出警告', async () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
      const ref = useLocalStorageRef('careerfit:pref:data', { raw_jd: 'test' })
      ref.value = { raw_jd: 'blocked content' } as never
      await nextTick()
      expect(warn).toHaveBeenCalled()
      warn.mockRestore()
    })

    it('拒绝写入 raw_resume 字段并发出警告', async () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
      const ref = useLocalStorageRef('careerfit:pref:data', { raw_resume: 'test' })
      ref.value = { raw_resume: 'blocked content' } as never
      await nextTick()
      expect(warn).toHaveBeenCalled()
      warn.mockRestore()
    })

    it('拒绝写入超过 1KB 的字符串并发出警告', async () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
      const ref = useLocalStorageRef('careerfit:pref:big', '')
      const bigString = 'x'.repeat(1025)
      ref.value = bigString
      await nextTick()
      expect(warn).toHaveBeenCalled()
      warn.mockRestore()
    })

    it('允许写入 1KB 以内的字符串', () => {
      const ref = useLocalStorageRef('careerfit:pref:small', '')
      const smallString = 'x'.repeat(1024)
      ref.value = smallString
      expect(ref.value).toBe(smallString)
    })
  })

  describe('localStorage 不可用时降级', () => {
    it('localStorage 抛异常时回退到内存', () => {
      const original = Object.getOwnPropertyDescriptor(Storage.prototype, 'setItem')
      Object.defineProperty(Storage.prototype, 'setItem', {
        value: () => { throw new Error('quota exceeded') },
        configurable: true,
      })
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
      const ref = useLocalStorageRef('careerfit:pref:fallback', 'initial')
      ref.value = 'updated'
      expect(ref.value).toBe('updated')
      warn.mockRestore()
      if (original) {
        Object.defineProperty(Storage.prototype, 'setItem', original)
      }
    })
  })
})
