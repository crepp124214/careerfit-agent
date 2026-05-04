# CareerFit Agent Phase 2F 报告导出测试计划

日期：2026-05-04

## 后端测试

| ID | 测试用例 | 前置条件 | 步骤 | 预期结果 |
|---|---|---|---|---|
| E1 | Markdown 导出 | 数据库有报告 | GET /api/reports/{id}/export?format=markdown | 200 OK，Content-Type: text/markdown，内容包含岗位名称和分数 |
| E2 | Markdown 内容完整性 | 报告含完整数据 | 导出 Markdown | 包含评分详情、技能评分、优势、缺口、建议、面试题、学习任务 |
| E3 | PDF 导出 | 数据库有报告 | GET /api/reports/{id}/export?format=pdf | 200 OK，Content-Type: application/pdf，body 非空 |
| E4 | 不存在的报告导出 | 报告 ID 不存在 | GET /api/reports/9999/export?format=markdown | 404 Not Found |
| E5 | 不支持的格式 | format=docx | GET /api/reports/{id}/export?format=docx | 400 Bad Request |
| E6 | 证据链脱敏 | 报告含证据 | 导出 Markdown | 不包含完整简历原文或 JD 原文 |

## 前端测试

| ID | 测试用例 | 预期结果 |
|---|---|---|
| F1 | 导出按钮存在 | 报告页显示"导出"按钮 |
| F2 | Markdown 下载 | 点击 Markdown 导出，触发浏览器下载 |
| F3 | PDF 下载 | 点击 PDF 导出，触发浏览器下载 |
