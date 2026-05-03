import { describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import type { AgentNode } from '@/api/agentRuns'
import AgentTraceTimeline from '@/components/report/AgentTraceTimeline.vue'

describe('AgentTraceTimeline', () => {
  const SAMPLE_NODES: AgentNode[] = [
    {
      name: '需求解析',
      status: 'success' as const,
      duration: 1200,
      summary: '已提取 JD 中 8 项核心要求',
      length: 2400,
      field_names: ['title', 'requirements', 'company'],
    },
    {
      name: '简历匹配',
      status: 'success' as const,
      duration: 800,
      summary: '匹配度评分完成',
      length: 1800,
      field_names: ['education', 'experience', 'skills'],
    },
    {
      name: 'Integrity Guard',
      status: 'failed' as const,
      duration: 50,
      summary: '拦截了 2 条夸大表述',
      length: 300,
      field_names: ['blocked_items'],
      error: 'Integrity guard blocked 2 items',
    },
  ]

  describe('脱敏渲染', () => {
    it('渲染节点 summary 文案', () => {
      const wrapper = mount(AgentTraceTimeline, {
        props: { nodes: SAMPLE_NODES },
      })
      expect(wrapper.text()).toContain('已提取 JD 中 8 项核心要求')
      expect(wrapper.text()).toContain('匹配度评分完成')
    })

    it('渲染 length 与 field_names 脱敏字段', () => {
      const wrapper = mount(AgentTraceTimeline, {
        props: { nodes: SAMPLE_NODES },
      })
      expect(wrapper.text()).toContain('2400')
      expect(wrapper.text()).toContain('requirements')
    })

    it('如果 props 中包含 raw_jd 或 raw_resume，不渲染原文', () => {
      const nodesWithRaw: AgentNode[] = [
        {
          name: '需求解析',
          status: 'success',
          duration: 1200,
          summary: '已提取 JD 中 8 项核心要求',
          length: 2400,
          field_names: ['title', 'requirements', 'company'],
          raw_jd: '这是一段完整的 JD 原文，不应该被渲染到 UI 中',
          raw_resume: '这是一段完整的简历原文，不应该被渲染到 UI 中',
        },
      ]
      const wrapper = mount(AgentTraceTimeline, {
        props: { nodes: nodesWithRaw },
      })
      expect(wrapper.text()).not.toContain('这是一段完整的 JD 原文')
      expect(wrapper.text()).not.toContain('这是一段完整的简历原文')
    })

    it('包含 raw_jd 时触发 dev-only 警告', () => {
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
      const nodesWithRaw: AgentNode[] = [
        {
          name: '需求解析',
          status: 'success',
          duration: 1200,
          summary: '已提取 JD 中 8 项核心要求',
          length: 2400,
          field_names: ['title', 'requirements', 'company'],
          raw_jd: '不应渲染的原文',
        },
      ]
      mount(AgentTraceTimeline, {
        props: { nodes: nodesWithRaw },
      })
      const warned = warn.mock.calls.some((call) =>
        call.some(
          (arg) =>
            typeof arg === 'string' &&
            (arg.toLowerCase().includes('raw') || arg.toLowerCase().includes('desensitiz')),
        ),
      )
      expect(warned).toBe(true)
      warn.mockRestore()
    })
  })

  describe('节点状态配色', () => {
    it('status=success 渲染 risk-low 色 + 文字标签', () => {
      const wrapper = mount(AgentTraceTimeline, {
        props: {
          nodes: [
            {
              name: '测试节点',
              status: 'success',
              duration: 100,
              summary: '完成',
              length: 50,
              field_names: [],
            },
          ],
        },
      })
      const text = wrapper.text()
      expect(text).toContain('成功')
    })

    it('status=failed 渲染 risk-high 色 + 文字标签', () => {
      const wrapper = mount(AgentTraceTimeline, {
        props: {
          nodes: [
            {
              name: '失败节点',
              status: 'failed',
              duration: 50,
              summary: '出错了',
              length: 20,
              field_names: [],
              error: 'something broke',
            },
          ],
        },
      })
      expect(wrapper.text()).toContain('失败')
    })

    it('status=running 渲染 info-trace 色 + 文字标签', () => {
      const wrapper = mount(AgentTraceTimeline, {
        props: {
          nodes: [
            {
              name: '进行中节点',
              status: 'running',
              duration: 0,
              summary: '执行中…',
              length: 0,
              field_names: [],
            },
          ],
        },
      })
      expect(wrapper.text()).toContain('进行中')
    })
  })

  describe('长列表折叠', () => {
    it('超过 5 个节点时默认折叠', () => {
      const manyNodes = Array.from({ length: 8 }, (_, i) => ({
        name: `节点 ${i + 1}`,
        status: 'success' as const,
        duration: 100,
        summary: `摘要 ${i + 1}`,
        length: 50,
        field_names: [],
      }))
      const wrapper = mount(AgentTraceTimeline, {
        props: { nodes: manyNodes },
      })
      expect(wrapper.text()).toContain('节点 1')
      expect(wrapper.text()).toContain('节点 5')
    })

    it('提供展开按钮显示全部节点', () => {
      const manyNodes = Array.from({ length: 8 }, (_, i) => ({
        name: `节点 ${i + 1}`,
        status: 'success' as const,
        duration: 100,
        summary: `摘要 ${i + 1}`,
        length: 50,
        field_names: [],
      }))
      const wrapper = mount(AgentTraceTimeline, {
        props: { nodes: manyNodes },
      })
      const expandBtn = wrapper.find('button')
      expect(expandBtn.exists()).toBe(true)
    })
  })
})
