import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import OnboardingWizard from '@/components/workbench/OnboardingWizard.vue'

function mountWithRouter() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/analysis', name: 'analysis-run', component: { template: '<div/>' } }],
  })
  return mount(OnboardingWizard, {
    global: { plugins: [router] },
  })
}

describe('OnboardingWizard', () => {
  it('renders step 1 by default', () => {
    const wrapper = mountWithRouter()
    expect(wrapper.text()).toContain('粘贴岗位描述')
  })

  it('has skip button', () => {
    const wrapper = mountWithRouter()
    expect(wrapper.find('[data-testid="wizard-skip"]').exists()).toBe(true)
  })

  it('emits dismiss when skip clicked', async () => {
    const wrapper = mountWithRouter()
    await wrapper.find('[data-testid="wizard-skip"]').trigger('click')
    expect(wrapper.emitted('dismiss')).toBeTruthy()
  })

  it('shows progress bar', () => {
    const wrapper = mountWithRouter()
    expect(wrapper.find('[data-testid="wizard-progress"]').exists()).toBe(true)
  })
})
