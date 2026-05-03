import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import RiskPill from '@/components/risk/RiskPill.vue'

describe('RiskPill', () => {
  describe('颜色 + 文字双通道（CLAUDE.md 硬约束）', () => {
    it('level=high：渲染默认中文文字 "高风险"', () => {
      const wrapper = mount(RiskPill, { props: { level: 'high' } })
      expect(wrapper.text()).toContain('高风险')
    })

    it('level=medium：渲染默认中文文字 "需关注"', () => {
      const wrapper = mount(RiskPill, { props: { level: 'medium' } })
      expect(wrapper.text()).toContain('需关注')
    })

    it('level=low：渲染默认中文文字 "通过"', () => {
      const wrapper = mount(RiskPill, { props: { level: 'low' } })
      expect(wrapper.text()).toContain('通过')
    })

    it('每一档都同时带可见文字和 aria-label，只有颜色没有文字会失败', () => {
      for (const level of ['high', 'medium', 'low'] as const) {
        const wrapper = mount(RiskPill, { props: { level } })
        const visibleText = wrapper.text().trim()
        const ariaLabel = wrapper.attributes('aria-label')
        expect(visibleText.length).toBeGreaterThan(0)
        expect(ariaLabel).toBeDefined()
        expect(ariaLabel?.length ?? 0).toBeGreaterThan(0)
      }
    })

    it('不同 level 必须有不同的视觉变体类名（颜色通道存在）', () => {
      const high = mount(RiskPill, { props: { level: 'high' } })
      const medium = mount(RiskPill, { props: { level: 'medium' } })
      const low = mount(RiskPill, { props: { level: 'low' } })
      const highClass = high.classes().join(' ')
      const mediumClass = medium.classes().join(' ')
      const lowClass = low.classes().join(' ')
      expect(highClass).not.toEqual(mediumClass)
      expect(highClass).not.toEqual(lowClass)
      expect(mediumClass).not.toEqual(lowClass)
    })
  })

  describe('标签 fallback', () => {
    it('未传 label 时使用约定中文标签', () => {
      const wrapper = mount(RiskPill, { props: { level: 'high' } })
      expect(wrapper.text()).toContain('高风险')
    })

    it('传入自定义 label 时覆盖默认值', () => {
      const wrapper = mount(RiskPill, {
        props: { level: 'medium', label: '需复核' },
      })
      expect(wrapper.text()).toContain('需复核')
      expect(wrapper.text()).not.toContain('需关注')
    })

    it('自定义 label 同步反映到 aria-label', () => {
      const wrapper = mount(RiskPill, {
        props: { level: 'low', label: '已校验' },
      })
      expect(wrapper.attributes('aria-label')).toContain('已校验')
    })
  })
})
