import { describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'

describe('BackendNotReadyNotice', () => {
  describe('必填 props（CEO C1：runtime 校验）', () => {
    it('feature 为必填', async () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
      mount(BackendNotReadyNotice, {
        // 故意省略 feature，验证 Vue runtime validator 触发 warn
        props: { waitingFor: 'jobs API' } as never,
      })
      const warned = warn.mock.calls.some((call) =>
        call.some((arg) => typeof arg === 'string' && arg.toLowerCase().includes('feature')),
      )
      expect(warned).toBe(true)
      warn.mockRestore()
    })

    it('waitingFor 为必填', async () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
      mount(BackendNotReadyNotice, {
        // 故意省略 waitingFor，验证 Vue runtime validator 触发 warn
        props: { feature: '历史趋势' } as never,
      })
      const warned = warn.mock.calls.some((call) =>
        call.some((arg) => typeof arg === 'string' && arg.toLowerCase().includes('waitingfor')),
      )
      expect(warned).toBe(true)
      warn.mockRestore()
    })

    it('feature 是空字符串时拒绝并发警告', async () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
      mount(BackendNotReadyNotice, {
        props: { feature: '', waitingFor: 'jobs API' },
      })
      const warned = warn.mock.calls.some((call) =>
        call.some((arg) => typeof arg === 'string' && arg.toLowerCase().includes('feature')),
      )
      expect(warned).toBe(true)
      warn.mockRestore()
    })
  })

  describe('默认文案', () => {
    it('渲染默认占位文案，包含 feature 与 waitingFor 名称', () => {
      const wrapper = mount(BackendNotReadyNotice, {
        props: { feature: '历史趋势', waitingFor: 'analyses.history 接口' },
      })
      expect(wrapper.text()).toContain('历史趋势')
      expect(wrapper.text()).toContain('analyses.history 接口')
      expect(wrapper.text()).toMatch(/(尚未上线|等待后端)/)
    })

    it('支持额外的中文 description prop 用于补充说明', () => {
      const wrapper = mount(BackendNotReadyNotice, {
        props: {
          feature: '历史趋势',
          waitingFor: 'analyses.history 接口',
          description: '后端聚合接口完成后，此处会展示真实趋势。',
        },
      })
      expect(wrapper.text()).toContain('后端聚合接口完成后')
    })
  })

  describe('禁止 mock 数据', () => {
    it('渲染输出不包含示例 / sample / demo 等假数据关键字', () => {
      const wrapper = mount(BackendNotReadyNotice, {
        props: { feature: '版本对比', waitingFor: 'resumes.diff 接口' },
      })
      const text = wrapper.text()
      expect(text).not.toMatch(/示例|sample|demo|mock/i)
    })

    it('渲染输出不包含看似真实的分数或百分比', () => {
      const wrapper = mount(BackendNotReadyNotice, {
        props: { feature: '版本对比', waitingFor: 'resumes.diff 接口' },
      })
      const text = wrapper.text()
      // 占位组件不允许出现 78、85.5、92% 这类貌似真实的评分
      expect(text).not.toMatch(/\b\d{1,3}(?:\.\d+)?%?\b/)
    })
  })

  describe('无障碍 role', () => {
    it('默认 role 为 status（非紧急通知）', () => {
      const wrapper = mount(BackendNotReadyNotice, {
        props: { feature: '历史趋势', waitingFor: 'analyses.history 接口' },
      })
      const role = wrapper.attributes('role')
      expect(['status', 'alert']).toContain(role)
    })

    it('支持 severity=alert 时切换为 role=alert', () => {
      const wrapper = mount(BackendNotReadyNotice, {
        props: {
          feature: '历史趋势',
          waitingFor: 'analyses.history 接口',
          severity: 'alert',
        },
      })
      expect(wrapper.attributes('role')).toBe('alert')
    })
  })
})
