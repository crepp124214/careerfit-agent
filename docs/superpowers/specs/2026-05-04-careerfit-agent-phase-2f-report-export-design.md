# CareerFit Agent Phase 2F 报告导出设计文档

日期：2026-05-04

## 目标

支持将分析报告导出为 Markdown 和 PDF 格式，方便用户保存、分享和打印。

## 当前状态

- 报告数据结构已稳定，包含总分、分项评分、证据链、缺口、简历建议、面试题、学习任务和 Next Best Action。
- 前端报告页只支持在线查看，无法导出。

## 范围

### 进入范围

- `GET /api/reports/{id}/export?format=markdown` — 导出 Markdown。
- `GET /api/reports/{id}/export?format=pdf` — 导出 PDF。
- 前端报告页添加"导出"按钮，支持 Markdown 和 PDF 两种格式。
- Markdown 导出使用纯 Python 字符串拼接，不引入模板引擎。
- PDF 导出使用 Playwright 浏览器渲染（前端已有 Playwright），或使用 `weasyprint` / `reportlab`。

### 不进入范围

- 自定义导出模板。
- 导出历史记录。
- 批量导出。
- 导出面试训练会话。

## API 设计

### GET /api/reports/{id}/export?format=markdown

返回 `Content-Type: text/markdown; charset=utf-8`，文件名 `report-{id}.md`。

### GET /api/reports/{id}/export?format=pdf

返回 `Content-Type: application/pdf`，文件名 `report-{id}.pdf`。

## Markdown 格式

```markdown
# CareerFit 匹配分析报告

## 基本信息

- 岗位：{job_title}
- 简历：{candidate_name} — {version_label}
- 分析时间：{created_at}
- 最终分数：{final_score}/100

## 评分详情

| 维度 | 分数 |
|------|------|
| 技能匹配 | {skill_score} |
| 项目经验 | {project_score} |
| ... | ... |

## 技能评分

### {skill_name}

- 评分：{score}/100
- JD 证据：{jd_evidence}
- 简历证据：{resume_evidence}
- 知识库标准：{knowledge_evidence}

## 优势

{strengths}

## 缺口

{gaps}

## 简历优化建议

{suggestions}

## 面试题

{interview_questions}

## 学习任务

{learning_plan}

## 下一步建议

{next_best_action}
```

## PDF 格式

使用 `weasyprint` 将 HTML 渲染为 PDF。HTML 使用与 Markdown 相同的数据，但带 CSS 样式。

## 技术选型

- Markdown 导出：纯 Python 字符串拼接。
- PDF 导出：`weasyprint`（轻量，不依赖浏览器，支持中文）。

## 隐私约束

- 导出内容包含评分和建议，但不包含完整简历原文或 JD 原文。
- 证据链仅包含片段引用，不包含完整文档。
