import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import NextBestActionCallout from '@/components/workbench/NextBestActionCallout.vue'

describe('NextBestActionCallout', () => {
  describe('state=ready', () => {
    it('渲染 lavender 左色条', () => {
      const wrapper = mount(NextBestActionCallout, {
        props: {
          state: 'ready',
          headline: '更新简历版本以补齐 LangGraph 经验',
          actionLabel: '生成新简历版本',
        },
      })
      const accent = wrapper.find('[data-testid="accent"]')
      expect(accent.exists()).toBe(true)
      expect(accent.classes().join(' ')).toMatch(/accent|stripe|leading/)
    })

    it('渲染 headline 文案', () => {
      const wrapper = mount(NextBestActionCallout, {
        props: {
          state: 'ready',
          headline: '更新简历版本以补齐 LangGraph 经验',
          actionLabel: '生成新简历版本',
        },
      })
      expect(wrapper.text()).toContain('更新简历版本以补齐 LangGraph 经验')
    })

    it('渲染主行动按钮且未禁用', () => {
      const wrapper = mount(NextBestActionCallout, {
        props: {
          state: 'ready',
          headline: '更新简历版本以补齐 LangGraph 经验',
          actionLabel: '生成新简历版本',
        },
      })
      const button = wrapper.find('button')
      expect(button.exists()).toBe(true)
      expect(button.text()).toContain('生成新简历版本')
      expect(button.attributes('disabled')).toBeUndefined()
    })

    it('点击主按钮触发 action 事件', async () => {
      const wrapper = mount(NextBestActionCallout, {
        props: {
          state: 'ready',
          headline: '更新简历版本以补齐 LangGraph 经验',
          actionLabel: '生成新简历版本',
        },
      })
      await wrapper.find('button').trigger('click')
      expect(wrapper.emitted('action')).toBeTruthy()
    })

    it('传入 ctaTo 时渲染指向学习任务的可访问链接', async () => {
      const router = createRouter({
        history: createMemoryHistory(),
        routes: [{ path: '/interview', name: 'interview', component: { template: '<div />' } }],
      })
      const wrapper = mount(NextBestActionCallout, {
        props: {
          state: 'ready',
          headline: '优先补齐 Docker 的可验证证据',
          actionLabel: '查看学习任务',
          ctaTo: '/interview?tab=learning',
        },
        global: { plugins: [router] },
      })
      await router.isReady()

      const link = wrapper.find('a[href="/interview?tab=learning"]')
      expect(link.exists()).toBe(true)
      expect(link.attributes('aria-label')).toBe('查看学习任务：优先补齐 Docker 的可验证证据')
    })
  })

  describe('state=blocked', () => {
    it('按钮处于 disabled 状态', () => {
      const wrapper = mount(NextBestActionCallout, {
        props: {
          state: 'blocked',
          headline: '需要先完成一次分析才能生成下一步',
          actionLabel: '生成新简历版本',
          waitingReason: '当前没有可用的分析报告',
        },
      })
      const button = wrapper.find('button')
      expect(button.exists()).toBe(true)
      expect(button.attributes('disabled')).toBeDefined()
    })

    it('展示等待原因文案', () => {
      const wrapper = mount(NextBestActionCallout, {
        props: {
          state: 'blocked',
          headline: '需要先完成一次分析才能生成下一步',
          actionLabel: '生成新简历版本',
          waitingReason: '当前没有可用的分析报告',
        },
      })
      expect(wrapper.text()).toContain('当前没有可用的分析报告')
    })
  })

  describe('state=empty', () => {
    it('渲染 ink-subtle "当前没有推荐行动" 文案', () => {
      const wrapper = mount(NextBestActionCallout, {
        props: { state: 'empty' },
      })
      expect(wrapper.text()).toContain('当前没有推荐行动')
    })

    it('不渲染主行动按钮', () => {
      const wrapper = mount(NextBestActionCallout, {
        props: { state: 'empty' },
      })
      expect(wrapper.find('button').exists()).toBe(false)
    })
  })

  describe('headline 截断', () => {
    it('超过 24 个汉字时附加换行类，避免溢出', () => {
      const longHeadline = '这是一个非常长的下一步行动文案'.repeat(2)
      expect(longHeadline.length).toBeGreaterThan(24)
      const wrapper = mount(NextBestActionCallout, {
        props: {
          state: 'ready',
          headline: longHeadline,
          actionLabel: '继续',
        },
      })
      const headline = wrapper.find('[data-testid="headline"]')
      expect(headline.exists()).toBe(true)
      const classes = headline.classes().join(' ')
      expect(classes).toMatch(/wrap|clamp|truncate/)
    })

    it('小于等于 24 个汉字时不应用截断类', () => {
      const wrapper = mount(NextBestActionCallout, {
        props: {
          state: 'ready',
          headline: '更新简历版本',
          actionLabel: '继续',
        },
      })
      const headline = wrapper.find('[data-testid="headline"]')
      expect(headline.exists()).toBe(true)
      const classes = headline.classes().join(' ')
      expect(classes).not.toMatch(/clamp/)
    })
  })
})
