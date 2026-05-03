import { describe, expect, it, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'

import SettingsView from '@/views/SettingsView.vue'

describe('SettingsView', () => {
  function createRouterInstance() {
    return createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/settings', name: 'settings', component: SettingsView }],
    })
  }

  async function mountView() {
    const pinia = createPinia()
    setActivePinia(pinia)
    const router = createRouterInstance()
    await router.push('/settings')
    await router.isReady()
    const wrapper = mount(SettingsView, {
      global: { plugins: [pinia, router] },
    })
    return { wrapper, pinia }
  }

  beforeEach(() => {
    localStorage.clear()
    vi.restoreAllMocks()
  })

  it('渲染主题选择', async () => {
    const { wrapper } = await mountView()
    expect(wrapper.text()).toContain('主题')
  })

  it('亮色主题 disabled 并标注 Phase 2', async () => {
    const { wrapper } = await mountView()
    const lightOption = wrapper.find('[data-testid="theme-light"]')
    expect(lightOption.exists()).toBe(true)
    expect(lightOption.attributes('disabled')).toBeDefined()
    expect(wrapper.text()).toContain('Phase 2')
  })

  it('渲染布局密度选择', async () => {
    const { wrapper } = await mountView()
    expect(wrapper.text()).toContain('布局密度')
  })

  it('渲染隐私提示文案', async () => {
    const { wrapper } = await mountView()
    expect(wrapper.text()).toContain('浏览器')
  })

  it('不渲染账号/登录/邮箱相关 UI', async () => {
    const { wrapper } = await mountView()
    const text = wrapper.text().toLowerCase()
    expect(text).not.toContain('登录')
    expect(text).not.toContain('注册')
    expect(text).not.toContain('邮箱')
    expect(text).not.toContain('用户名')
  })
})
