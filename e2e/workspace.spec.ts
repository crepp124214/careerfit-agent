import { test, expect } from '@playwright/test'

test.describe('工作台首页', () => {
  test('应该显示工作台标题', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('h1')).toContainText('个人求职成长工作台')
  })

  test('应该显示 Next Best Action 组件', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('[aria-label="下一步建议"]')).toBeVisible()
  })

  test('应该显示岗位选择器', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('[aria-label="岗位选择"]')).toBeVisible()
  })

  test('应该显示简历选择器', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('[aria-label="简历选择"]')).toBeVisible()
  })
})

test.describe('导航', () => {
  test('应该能够导航到岗位页面', async ({ page }) => {
    await page.goto('/')
    await page.click('text=岗位')
    await expect(page).toHaveURL(/\/jobs/)
  })

  test('应该能够导航到简历页面', async ({ page }) => {
    await page.goto('/')
    await page.click('text=简历')
    await expect(page).toHaveURL(/\/resumes/)
  })

  test('应该能够导航到设置页面', async ({ page }) => {
    await page.goto('/')
    await page.click('text=设置')
    await expect(page).toHaveURL(/\/settings/)
  })
})

test.describe('响应式设计', () => {
  test('移动端应该显示移动导航', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/')
    await expect(page.locator('.app-shell__mobile-nav')).toBeVisible()
  })

  test('桌面端应该显示侧边导航', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 })
    await page.goto('/')
    await expect(page.locator('.side-nav')).toBeVisible()
  })
})
