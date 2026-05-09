import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import JdPreviewCard from '@/components/preview/JdPreviewCard.vue'
import type { JdPreviewResponse } from '@/api/preview'

const mockData: JdPreviewResponse = {
  title: '后端开发工程师',
  category: 'software_engineering',
  skills: [
    { name: 'Python', level: 'project_practice', category: 'programming' },
    { name: 'SQL', level: 'mentioned', category: 'database' },
  ],
  requirements: ['3年经验', '本科及以上'],
  domain_keywords: ['后端开发'],
}

describe('JdPreviewCard', () => {
  it('renders title and skills', () => {
    const wrapper = mount(JdPreviewCard, {
      props: { data: mockData },
    })
    expect(wrapper.text()).toContain('后端开发工程师')
    expect(wrapper.text()).toContain('Python')
    expect(wrapper.text()).toContain('SQL')
  })

  it('renders requirements', () => {
    const wrapper = mount(JdPreviewCard, {
      props: { data: mockData },
    })
    expect(wrapper.text()).toContain('3年经验')
  })

  it('shows empty state when data has no skills', () => {
    const emptyData = { ...mockData, skills: [] }
    const wrapper = mount(JdPreviewCard, {
      props: { data: emptyData },
    })
    expect(wrapper.text()).toContain('未提取到技能')
  })
})
