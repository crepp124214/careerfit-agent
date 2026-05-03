# CareerFit Agent Phase 2C 测试计划：多模型后端代理

日期：2026-05-04

## 测试目标

验证后端代理可以安全接入国内外常用 OpenAI-compatible 大模型 API，同时保持确定性评分、隐私脱敏和失败回退。

## 后端配置测试

命令：

```powershell
cd backend
pytest tests/test_llm_client.py -q
```

覆盖：

- 默认 `CAREERFIT_LLM_ENABLED=false` 时 capability 为 `llm: unavailable`。
- 配置 `CAREERFIT_LLM_ENABLED=true`、API Key 和 model 后 capability 为 `llm: ready`。
- 缺少 API Key 或 model 时，即使 enabled 也不能进入 ready。

## LLM client 测试

覆盖：

- `chat_completions` 调用 `{base_url}/chat/completions`。
- `responses` 调用 `{base_url}/responses`。
- Authorization header 使用后端环境变量中的 API Key。
- 请求体包含 model 和输入内容。
- 响应 JSON 文本能被 Pydantic schema 校验。
- 非法 JSON 最多修复重试一次。
- provider HTTP 失败、超时、非法结构会抛出受控错误，不泄露 key。

## Agent 流程测试

命令：

```powershell
cd backend
pytest tests/test_llm_agent_flow.py tests/test_analysis_flow.py -q
```

覆盖：

- LLM disabled 时分析主流程行为保持原样。
- LLM enabled 且 mock 成功时，报告使用 LLM 生成的简历建议、面试题、学习计划和 Next Best Action。
- LLM enabled 但 provider 失败时，分析任务仍 `success`，报告使用 fallback。
- LLM 不改变 `final_score`、`score_breakdown` 或 scoring version。
- Integrity Guard 仍在简历建议展示前运行。
- Agent trace 不包含 API Key、prompt 原文、完整 JD、完整简历。

## 前端回归

Phase 2C 不让前端接触 API Key，只需保证现有页面不回退：

```powershell
cd frontend
npm test
npm run typecheck
npm run build
```

覆盖：

- 工作台仍可执行分析。
- 报告页仍展示结构化建议。
- 设置页不显示或保存 API Key。
- localStorage / IndexedDB 不出现 LLM key、prompt、简历原文、JD 原文。

## 手工真实 API smoke

在本地 `.env` 或 shell 环境配置一个真实 provider：

```env
CAREERFIT_LLM_ENABLED=true
CAREERFIT_LLM_PROVIDER=deepseek
CAREERFIT_LLM_BASE_URL=https://api.deepseek.com/v1
CAREERFIT_LLM_API_KEY=你的_key
CAREERFIT_LLM_MODEL=deepseek-chat
CAREERFIT_LLM_API_STYLE=chat_completions
```

运行：

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

验收：

- 创建岗位和简历后执行分析成功。
- 报告包含更自然的中文建议。
- 评分仍由确定性规则产生。
- `/api/agent-runs/{task_id}` 不出现 API Key、prompt 原文、完整 JD、完整简历。

## PII 安全审计

由于 Phase 2C 触碰 Agent prompt 装配，完成后必须运行：

```powershell
gstack:cso
```

如果当前环境没有可执行入口，必须按本地 `gstack:cso` skill 文档做等价 OWASP + STRIDE 审计，并把失败命令、替代审计结论和残余风险写入 review log。

