import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ResumePreviewCard from '@/components/preview/ResumePreviewCard.vue'
import type { ResumePreviewResponse } from '@/api/preview'

const mockData: ResumePreviewResponse = {
  name: '张三',
  skills: ['Python', 'SQL', 'Docker'],
  projects: [{ name: '电商平台', role: '后端开发', highlights: ['设计订单系统'] }],
  education: [{ school: '北京大学', major: '计算机科学', degree: '本科' }],
  experience_years: 3,
}

describe('ResumePreviewCard', () => {
  it('renders name and skills', () => {
    const wrapper = mount(ResumePreviewCard, {
      props: { data: mockData },
    })
    expect(wrapper.text()).toContain('张三')
    expect(wrapper.text()).toContain('Python')
  })

  it('renders projects', () => {
    const wrapper = mount(ResumePreviewCard, {
      props: { data: mockData },
    })
    expect(wrapper.text()).toContain('电商平台')
  })

  it('renders education', () => {
    const wrapper = mount(ResumePreviewCard, {
      props: { data: mockData },
    })
    expect(wrapper.text()).toContain('北京大学')
  })

  it('shows empty state when no skills', () => {
    const emptyData = { ...mockData, skills: [] }
    const wrapper = mount(ResumePreviewCard, {
      props: { data: emptyData },
    })
    expect(wrapper.text()).toContain('未提取到技能')
  })
})
