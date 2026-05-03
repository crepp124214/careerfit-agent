# CareerFit Agent Phase 2C 多模型后端代理实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 通过后端代理接入国内外常用 OpenAI-compatible 大模型 API，同时保留确定性评分与本地 fallback。

**Architecture:** 后端新增 `llm` 模块，统一读取环境变量、调用 `chat_completions` 或 `responses` 风格 API、校验结构化 JSON，并把结果注入生成型 Agent 节点。前端不接触 API Key，仅通过现有分析流程消费报告。

**Tech Stack:** FastAPI、Pydantic、SQLAlchemy、httpx、pytest、Vue3、TypeScript、Vitest、Docker Compose。

---

## 范围

进入范围：

- 一个 active LLM provider 配置。
- OpenAI-compatible `chat_completions`。
- OpenAI `responses`。
- 生成型节点 LLM 增强：`resume_optimizer`、`interview_coach`、`learning_planner`、`next_best_action`。
- 非法 JSON 一次修复重试。
- 失败回退本地 fallback。
- `/api/capabilities` 增加 `llm` 状态。
- README 与 `.env.example` 或等价配置说明。

不进入范围：

- 前端输入 API Key。
- 多 provider UI 管理。
- 流式输出。
- 调用成本统计。
- RAG、向量入库、文件解析。
- LLM 数字评分。

## 成功标准

- `CAREERFIT_LLM_ENABLED=false` 或缺少 key 时，后端测试主流程保持原有输出形态。
- `CAREERFIT_LLM_ENABLED=true` 且 mock provider 返回合法 JSON 时，报告包含 LLM 结果。
- provider 超时、HTTP 失败、非法 JSON 时，任务仍成功并使用 fallback。
- Agent trace 对外不含 API Key、prompt 原文、完整简历、完整 JD。
- `/api/capabilities` 返回 `llm: ready | unavailable`。
- 后端、前端和文档验证通过。

## 文件结构

```text
backend/
  app/
    core/config.py
    llm/__init__.py
    llm/client.py
    llm/prompts.py
    llm/schemas.py
    llm/service.py
    agents/graph.py
    agents/nodes.py
    main.py
  tests/
    test_llm_client.py
    test_llm_agent_flow.py
frontend/
  src/api/availability.ts
  src/stores/availability.ts
docs/
  superpowers/specs/2026-05-04-careerfit-agent-phase-2c-llm-proxy-design.md
  superpowers/plans/2026-05-04-careerfit-agent-phase-2c-llm-proxy.md
  superpowers/test-plans/2026-05-04-careerfit-agent-phase-2c-test-plan.md
README.md
TODOS.md
```

---

## Task 0：文档与配置范围

**Files:**

- Create: `docs/superpowers/specs/2026-05-04-careerfit-agent-phase-2c-llm-proxy-design.md`
- Create: `docs/superpowers/test-plans/2026-05-04-careerfit-agent-phase-2c-test-plan.md`
- Modify: `TODOS.md`

- [x] **Step 1：确认方案**

用户确认选择 A：OpenAI-compatible 优先，多模型通过后端代理接入。

- [x] **Step 2：写设计文档**

记录后端代理、active provider、api_style、隐私边界和 fallback 策略。

- [x] **Step 3：写测试计划**

覆盖关闭 LLM、mock 成功、失败回退、trace 脱敏和配置说明。

- [ ] **Step 4：同步外部测试计划副本**

Run:

```powershell
Copy-Item -LiteralPath "E:\New project 2\docs\superpowers\test-plans\2026-05-04-careerfit-agent-phase-2c-test-plan.md" -Destination "C:\Users\qwer\.gstack\projects\Newproject\phase-2c-test-plan-2026-05-04-careerfit-agent.md" -Force
```

Expected: 外部副本存在。

---

## Task 1：LLM 配置与能力状态

**Files:**

- Modify: `backend/app/core/config.py`
- Modify: `backend/app/main.py`
- Modify: `backend/pyproject.toml`
- Test: `backend/tests/test_llm_client.py`

- [ ] **Step 1：写失败测试：默认 LLM disabled**

断言默认 settings 中 `llm_enabled` 为 `False`，`/api/capabilities` 返回 `llm: unavailable`。

- [ ] **Step 2：写失败测试：环境变量开启 LLM**

用 monkeypatch 设置 `CAREERFIT_LLM_ENABLED=true`、`CAREERFIT_LLM_API_KEY`、`CAREERFIT_LLM_MODEL`，断言 capability 为 `ready`。

- [ ] **Step 3：实现配置字段**

新增 `llm_enabled`、`llm_provider`、`llm_base_url`、`llm_api_key`、`llm_model`、`llm_api_style`、`llm_timeout_seconds`。

- [ ] **Step 4：新增 httpx 生产依赖**

把 `httpx>=0.27` 从 dev 依赖提升到生产依赖，供后端代理 HTTP 调用使用。

- [ ] **Step 5：运行配置测试**

Run:

```powershell
cd backend
pytest tests/test_llm_client.py::test_llm_capability_defaults_to_unavailable -q
```

Expected: PASS。

---

## Task 2：LLM client 与 schema

**Files:**

- Create: `backend/app/llm/__init__.py`
- Create: `backend/app/llm/client.py`
- Create: `backend/app/llm/schemas.py`
- Test: `backend/tests/test_llm_client.py`

- [ ] **Step 1：写失败测试：chat_completions 请求形状**

用 fake transport 捕获请求，断言 URL 为 `{base_url}/chat/completions`，header 含 Bearer token，body 含 `model` 和 `messages`。

- [ ] **Step 2：写失败测试：responses 请求形状**

断言 `api_style=responses` 时调用 `{base_url}/responses`，body 含 `model` 和 `input`。

- [ ] **Step 3：写失败测试：解析合法 JSON**

mock provider 返回 JSON 文本，断言转换为 Pydantic schema。

- [ ] **Step 4：写失败测试：非法 JSON 一次修复重试**

第一次返回非法 JSON，第二次返回合法 JSON，断言调用两次。

- [ ] **Step 5：实现 client**

使用 `httpx.Client`，设置超时，统一返回文本；不要记录请求正文或 key。

- [ ] **Step 6：实现 schemas**

新增 `LLMReportEnhancement`，包含 `resume_suggestions`、`interview_questions`、`learning_plan`、`next_best_action`。

- [ ] **Step 7：运行 client 测试**

Run:

```powershell
cd backend
pytest tests/test_llm_client.py -q
```

Expected: PASS。

---

## Task 3：Prompt 与 Agent 节点集成

**Files:**

- Create: `backend/app/llm/prompts.py`
- Create: `backend/app/llm/service.py`
- Modify: `backend/app/agents/nodes.py`
- Modify: `backend/app/agents/graph.py`
- Test: `backend/tests/test_llm_agent_flow.py`

- [ ] **Step 1：写失败测试：LLM disabled 使用 fallback**

运行分析主流程，断言报告仍包含本地 fallback 建议。

- [ ] **Step 2：写失败测试：LLM enabled 使用 mock 输出**

monkeypatch LLM service 返回合法增强结果，断言报告中的建议、面试题、学习计划和 Next Best Action 来自 mock。

- [ ] **Step 3：写失败测试：LLM 失败回退**

monkeypatch LLM service 抛异常，断言分析任务仍 `success`，并使用 fallback。

- [ ] **Step 4：写失败测试：trace 不含 prompt 或 key**

断言 `agent_runs` 响应不包含 API Key、完整 JD、完整简历、`messages` 或 `prompt` 原文。

- [ ] **Step 5：实现 prompt builder**

只传结构化 `strengths`、`gaps`、`score_items` 摘要；不传完整原文。

- [ ] **Step 6：实现 service**

`generate_report_enhancement(state)` 负责读取配置、调用 client、校验 schema、返回结果或 `None`。

- [ ] **Step 7：改造节点**

在生成型节点中使用同一份 enhancement；若为空则走现有 fallback。`match_scorer` 不接 LLM。

- [ ] **Step 8：运行 Agent 流程测试**

Run:

```powershell
cd backend
pytest tests/test_llm_agent_flow.py tests/test_analysis_flow.py -q
```

Expected: PASS。

---

## Task 4：文档、配置示例与回归

**Files:**

- Modify: `README.md`
- Modify: `TODOS.md`
- Modify: `docs/superpowers/plans/2026-05-04-careerfit-agent-phase-2c-llm-proxy.md`

- [ ] **Step 1：补 README 配置说明**

写明 OpenAI、DeepSeek、Kimi、Qwen 等 OpenAI-compatible 示例配置；禁止提交真实 key。

- [ ] **Step 2：更新 TODO**

标记 Phase 2C 已完成项和 PII 审计要求。

- [ ] **Step 3：运行后端测试**

Run:

```powershell
cd backend
pytest -q
```

Expected: PASS。

- [ ] **Step 4：运行前端回归**

Run:

```powershell
cd frontend
npm test
npm run typecheck
npm run build
```

Expected: PASS。

- [ ] **Step 5：PII 安全审计**

Run:

```powershell
gstack:cso
```

Expected: 记录 OWASP + STRIDE 结论；若 CLI 不可用，按本地 skill 文档做等价审计并写入 review log。

- [ ] **Step 6：文档检查**

Run:

```powershell
git diff --check
```

Expected: PASS。

---

## 决策记录

| 决策点 | 选择 | 理由 | 回滚条件 |
|---|---|---|---|
| Provider 范围 | 一个 active provider + OpenAI-compatible 配置 | 覆盖常用模型 API，同时避免模型管理平台化 | 用户需要同时配置多个 key 并在 UI 切换 |
| API 风格 | `chat_completions` + `responses` | 兼容国内常见服务，也保留 OpenAI Responses API | 某厂商必须使用专有协议 |
| LLM 接入节点 | 只接生成型节点 | 保持确定性评分可信 | 后续有严格 schema 与评测支持 LLM 辅助评分 |
| 失败策略 | 失败回退本地 fallback | 不让外部 API 稳定性破坏主流程 | 用户明确要求失败即阻断分析 |
| Key 管理 | 后端环境变量 | 防止浏览器泄露 API Key | 后续引入加密密钥管理和账号系统 |
