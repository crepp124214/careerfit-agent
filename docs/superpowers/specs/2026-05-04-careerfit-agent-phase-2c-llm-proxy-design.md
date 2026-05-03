# CareerFit Agent Phase 2C 多模型后端代理设计

日期：2026-05-04

## 背景

Phase 2B 已补齐历史趋势与版本对比。下一阶段用户希望接入国内外常用大模型 API，并明确选择“后端代理”而不是前端直连。项目必须继续遵守隐私与可信度边界：API Key 不进前端，最终数字评分仍由确定性规则计算，LLM 只增强生成型建议。

## 目标

- 后端支持一个当前激活的大模型配置，可通过环境变量切换不同厂商。
- 优先支持 OpenAI-compatible API，覆盖常见国内外服务的最小公共协议。
- LLM 只接入生成型节点：简历优化建议、面试问题、学习计划和 Next Best Action。
- LLM 失败、未配置或返回非法结构时，自动回退到当前本地确定性 fallback。
- Agent trace 对外仍只展示脱敏摘要，不泄露 API Key、完整简历、完整 JD 或 prompt 原文。

## 非目标

- 不做前端输入 API Key。
- 不做多账号、多租户或用户级模型配置。
- 不做模型市场、计费、调用统计看板。
- 不做流式输出。
- 不让 LLM 决定最终分数。
- 不引入 RAG、向量入库或文件解析。

## 支持范围

Phase 2C 使用一个通用配置：

```env
CAREERFIT_LLM_ENABLED=true
CAREERFIT_LLM_PROVIDER=openai
CAREERFIT_LLM_BASE_URL=https://api.openai.com/v1
CAREERFIT_LLM_API_KEY=...
CAREERFIT_LLM_MODEL=...
CAREERFIT_LLM_API_STYLE=chat_completions
```

`CAREERFIT_LLM_API_STYLE` 支持：

- `chat_completions`：OpenAI-compatible `/chat/completions`，用于 DeepSeek、Kimi、通义千问兼容模式、智谱兼容模式、火山方舟兼容模式等。
- `responses`：OpenAI `/responses`，用于 OpenAI 官方 Responses API。

首版只允许一个 active provider，避免引入复杂的 provider 列表、前端管理和密钥轮换。

## 数据流

```text
前端点击执行分析
  -> POST /api/analysis
  -> analysis_service.run_workflow
  -> 确定性解析、评分、缺口分析
  -> 生成型节点尝试调用 LLM
  -> Pydantic 校验 LLM 输出
  -> Integrity Guard 检查简历建议
  -> 失败则使用本地 fallback
  -> 保存报告和脱敏 Agent trace
```

## 后端模块

新增：

- `backend/app/llm/client.py`：统一 HTTP 客户端，按 `api_style` 调用 provider。
- `backend/app/llm/schemas.py`：LLM 输出 Pydantic schema。
- `backend/app/llm/prompts.py`：中文 prompt 构造，只传必要摘要，不传无关原文。
- `backend/app/llm/service.py`：面向 Agent 节点的安全调用入口。

修改：

- `backend/app/core/config.py`：新增 LLM 环境变量。
- `backend/app/agents/nodes.py`：生成型节点尝试使用 LLM，失败回退。
- `backend/app/agents/graph.py`：trace 继续脱敏，并标记节点是否使用 `llm_enabled` / `fallback_used`，不保存 prompt 原文。
- `backend/app/main.py`：`/api/capabilities` 增加 `llm` 状态。
- `backend/pyproject.toml`：生产依赖增加 `httpx`。

## 输出结构

LLM 必须返回 JSON，后端校验为：

```text
resume_suggestions:
  - title
    suggestion
    jd_requirement
    resume_evidence
    risk_level

interview_questions:
  - skill
    question

learning_plan:
  - skill
    task

next_best_action:
  title
  description
  target_skill
```

如果 JSON 解析失败，允许一次“修复 JSON”重试；仍失败则回退。

## 隐私与安全

- API Key 只来自后端环境变量，不写入仓库、不下发前端。
- 不在日志、trace、异常详情中保存 prompt 原文。
- prompt 只包含已结构化的优势、缺口、证据摘要和评分项，不传完整简历/JD。
- 简历优化建议仍必须经过 Integrity Guard。
- LLM 结果不得覆盖确定性评分。
- 由于 Phase 2C 触碰 Agent prompt 装配，完成后必须记录 PII 安全审计；如果 `gstack:cso` CLI 不可用，按本地 skill 文档做等价审计并记录。

## 成功标准

- 未配置 LLM 时，现有分析主流程行为保持不变。
- 配置 LLM 且 mock provider 成功时，报告使用 LLM 生成的建议、面试题、学习计划和 Next Best Action。
- 配置 LLM 但 provider 失败、超时或返回非法 JSON 时，报告回退到本地 fallback，分析任务仍成功。
- Agent trace 不包含 API Key、完整 prompt、完整简历或完整 JD。
- 前端不接触 API Key。
- 后端、前端、typecheck、build 和文档检查通过；Docker smoke 取决于本机 Docker daemon 状态。
