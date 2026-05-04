# CareerFit Agent Phase 2F 报告导出实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 支持将分析报告导出为 Markdown 和 PDF 格式。

**Architecture:** 后端新增导出 API，Markdown 用纯 Python 拼接，PDF 用 weasyprint 渲染 HTML。前端报告页添加导出按钮。

---

## Task 0：计划与文档门

- [x] **Step 1：确认 Phase 2F 范围**

报告导出 Markdown + PDF，不做自定义模板、批量导出或导出历史。

- [x] **Step 2：创建设计文档**

- [ ] **Step 3：创建测试计划**

- [ ] **Step 4：更新 TODOS**

---

## Task 1：后端 Markdown 导出

**Files:**

- Create: `backend/app/services/export_service.py`
- Modify: `backend/app/api/routes/reports.py`

- [ ] **Step 1：实现 Markdown 生成函数**

`generate_markdown_report(report, job, resume)` — 从报告数据生成 Markdown 字符串。

- [ ] **Step 2：新增导出 API 路由**

`GET /api/reports/{id}/export?format=markdown` — 返回 Markdown 文件。

- [ ] **Step 3：写测试**

测试 Markdown 导出返回正确内容和 Content-Type。

---

## Task 2：后端 PDF 导出

**Files:**

- Modify: `backend/pyproject.toml`
- Modify: `backend/app/services/export_service.py`
- Modify: `backend/app/api/routes/reports.py`

- [ ] **Step 1：安装 weasyprint 依赖**

- [ ] **Step 2：实现 PDF 生成函数**

`generate_pdf_report(report, job, resume)` — 从报告数据生成 HTML，再用 weasyprint 渲染为 PDF。

- [ ] **Step 3：新增 PDF 导出路由**

`GET /api/reports/{id}/export?format=pdf` — 返回 PDF 文件。

- [ ] **Step 4：写测试**

测试 PDF 导出返回正确 Content-Type 和非空内容。

---

## Task 3：前端导出按钮

**Files:**

- Modify: `frontend/src/views/ReportView.vue`

- [ ] **Step 1：添加导出按钮**

在报告页标题区域添加"导出"下拉按钮，支持 Markdown 和 PDF。

- [ ] **Step 2：实现导出下载逻辑**

点击后调用 `/api/reports/{id}/export?format=xxx`，触发浏览器下载。

---

## Task 4：全量回归与文档同步

- [ ] **Step 1：后端全量测试**

- [ ] **Step 2：前端 typecheck 和 build**

- [ ] **Step 3：浏览器端到端测试**

- [ ] **Step 4：文档同步**

---

## 决策记录

| 决策点 | 选择 | 理由 | 回滚条件 |
|---|---|---|---|
| Markdown 生成方式 | 纯 Python 字符串拼接 | 不引入模板引擎依赖 | 格式复杂度增加 |
| PDF 生成方式 | weasyprint | 轻量，支持中文，不依赖浏览器 | weasyprint 安装困难 |
| 导出 API 路径 | GET /api/reports/{id}/export | RESTful，与报告 API 同组 | 需要异步生成 |
