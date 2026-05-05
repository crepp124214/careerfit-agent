# Playwright E2E 测试

这个目录包含端到端测试，使用 Playwright 运行。

## 运行测试

```bash
# 安装浏览器（首次运行前需要）
npm run playwright:install

# 运行所有测试
npm run test:e2e

# 以可视化模式运行
npm run test:e2e:headed

# 调试模式
npm run test:e2e:debug

# UI 模式
npm run test:e2e:ui

# 查看测试报告
npm run playwright:report
```

## 测试覆盖

- `workspace.spec.ts` - 工作台首页测试
  - 基础结构验证
  - 导航功能
  - 响应式设计

## 配置

测试配置在 `playwright.config.ts` 中，包括：
- 测试目录：`./e2e`
- 基础 URL：`http://127.0.0.1:5173`
- 浏览器：Chrome、Firefox、Safari（桌面 + 移动端）
- 自动启动开发服务器
