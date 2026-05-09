import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import Breadcrumb from '@/components/common/Breadcrumb.vue'

async function mountWithRouter(items: Array<{ label: string; to?: string }>) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div/>' } },
      { path: '/reports/:id', component: { template: '<div/>' } },
    ],
  })
  const wrapper = mount(Breadcrumb, {
    props: { items },
    global: { plugins: [router] },
  })
  await router.isReady()
  return wrapper
}

describe('Breadcrumb', () => {
  it('renders items with separator', async () => {
    const wrapper = await mountWithRouter([
      { label: '工作台', to: '/' },
      { label: '报告', to: '/reports/1' },
      { label: '面试训练' },
    ])
    expect(wrapper.text()).toContain('工作台')
    expect(wrapper.text()).toContain('报告')
    expect(wrapper.text()).toContain('面试训练')
  })

  it('renders last item as plain text', async () => {
    const wrapper = await mountWithRouter([
      { label: '工作台', to: '/' },
      { label: '当前页' },
    ])
    const links = wrapper.findAll('a')
    expect(links.length).toBe(1)
  })
})
