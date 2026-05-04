# CareerFit Agent Phase 2E 面试训练闭环测试计划

日期：2026-05-04

## 测试范围

Phase 2E 新增的面试训练闭环功能，包括后端 API、服务层逻辑和前端页面。

## 后端测试

### test_interview_service.py

| ID | 测试用例 | 前置条件 | 步骤 | 预期结果 |
|---|---|---|---|---|
| S1 | 创建面试训练会话 | 数据库有报告（含 interview_questions） | 调用 create_session(db, report_id=1, include_rag=False) | 返回 InterviewSession，total_questions > 0，status="created" |
| S2 | 创建会话幂等 | 同一 report_id 已创建过会话 | 再次调用 create_session | 返回已有会话，不重复创建 |
| S3 | RAG 补充面试题 | 数据库有 interview 类型知识库文档 | 调用 create_session(db, report_id=1, include_rag=True) | 题目数 > 仅报告题目数，部分题目 source="rag" |
| S4 | RAG 题目去重 | RAG 文档中有与报告重复的题目 | 创建会话 | 不出现重复题目 |
| S5 | 题目分类 | 报告有不同类型面试题 | 创建会话 | basic/project_deep_dive/scenario_design 分类正确 |
| S6 | 难度分配 | 不同技能和类别 | 创建会话 | easy/medium/hard 分配合理 |
| S7 | 列出会话 | 数据库有多个会话 | 调用 list_sessions | 返回会话列表，按创建时间倒序 |
| S8 | 按状态筛选会话 | 数据库有不同状态会话 | 调用 list_sessions(status="completed") | 只返回 completed 状态会话 |
| S9 | 获取会话详情 | 数据库有会话和题目 | 调用 get_session(db, session_id=1) | 返回会话详情含完整题目列表 |
| S10 | 更新题目状态 | 题目当前 status="not_started" | 调用 update_question(db, sid, qid, status="practicing") | 状态更新成功 |
| S11 | 状态流转校验 — 合法 | 题目 status="practicing" | 更新为 "completed" | 成功 |
| S12 | 状态流转校验 — 非法 | 题目 status="not_started" | 直接更新为 "completed" | 拒绝，返回错误 |
| S13 | 更新题目笔记 | 题目存在 | 调用 update_question(db, sid, qid, notes="需要加强") | 笔记更新成功 |
| S14 | 完成进度自动更新 | 会话有 3 道题 | 将 1 道题标记为 completed | session.completed_questions = 1 |
| S15 | 会话状态自动更新 | 会话所有题目都 completed | 更新最后一道题 | session.status = "completed" |

### test_interview_api.py

| ID | 测试用例 | 步骤 | 预期结果 |
|---|---|---|---|
| A1 | POST /api/interview/sessions | 发送 {report_id: 1, include_rag: true} | 201 Created，返回会话数据 |
| A2 | POST 重复创建 | 同一 report_id 再次 POST | 200 OK，返回已有会话 |
| A3 | GET /api/interview/sessions | 列出所有会话 | 200 OK，返回列表 |
| A4 | GET /api/interview/sessions/{id} | 获取会话详情 | 200 OK，含题目列表 |
| A5 | PATCH 题目状态 | 更新为 practicing | 200 OK |
| A6 | PATCH 非法状态跳转 | not_started → completed | 422 Unprocessable Entity |
| A7 | PATCH 题目笔记 | 更新 notes | 200 OK |
| A8 | GET 不存在的会话 | GET /api/interview/sessions/9999 | 404 Not Found |
| A9 | capabilities 包含 interview | GET /api/capabilities | interview: "ready" |

## 前端测试

### 面试训练列表页

| ID | 测试用例 | 预期结果 |
|---|---|---|
| F1 | 空状态 | 显示"暂无面试训练会话"提示 |
| F2 | 加载状态 | 显示加载动画 |
| F3 | 错误状态 | 显示错误提示和重试按钮 |
| F4 | 后端不可用 | 显示 BackendNotReadyNotice |
| F5 | 有数据 | 显示会话卡片列表 |

### 面试训练详情页

| ID | 测试用例 | 预期结果 |
|---|---|---|
| F6 | 题目列表展示 | 显示所有题目，含技能标签、类别、难度 |
| F7 | 筛选功能 | 按技能/类别/难度筛选 |
| F8 | 状态切换 | 点击切换练习状态 |
| F9 | 笔记输入 | 输入笔记并保存 |
| F10 | 进度条 | 显示完成百分比 |

### 报告页 CTA

| ID | 测试用例 | 预期结果 |
|---|---|---|
| F11 | "开始面试训练"按钮 | 点击跳转到创建会话 |

## 集成测试

| ID | 测试用例 | 步骤 | 预期结果 |
|---|---|---|---|
| I1 | 端到端：创建会话 → 练习 → 完成 | 1. 从报告创建会话 2. 逐题练习 3. 全部完成 | 会话状态从 created → in_progress → completed |
| I2 | RAG 补充端到端 | 创建含 RAG 的会话 | 题目包含 rag 来源 |
