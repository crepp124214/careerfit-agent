# CareerFit Agent Phase 2C 多模型后端代理安全审计记录

日期：2026-05-04

## 审计范围

本次审计覆盖 Phase 2C 新增的大模型后端代理能力：

- LLM 环境变量配置。
- `backend/app/llm/client.py` HTTP 调用边界。
- `backend/app/llm/prompts.py` prompt 构造。
- `backend/app/llm/service.py` schema 校验与一次修复重试。
- `backend/app/agents/nodes.py` 生成型节点接入。
- `backend/app/agents/graph.py` Agent trace 脱敏。
- `docker-compose.yml` LLM 环境变量透传。
- README 配置示例。

## 命令记录

尝试运行：

```powershell
gstack:cso
```

结果：失败。当前 PowerShell 环境没有 `gstack:cso` 可执行入口，错误为 `The term 'gstack:cso' is not recognized`。

替代审计：已读取本地 `gstack:cso` skill 文档，并按 OWASP + STRIDE + LLM Security 关注点做手工等价审计。

## 自动检查记录

已执行关键字检查：

- `CAREERFIT_LLM_API_KEY`
- `llm_api_key`
- `api_key`
- `Authorization`
- `prompt`
- `messages`
- `raw_jd`
- `raw_resume`
- 常见 secret 格式，例如 `sk-`、`AKIA`、`BEGIN PRIVATE KEY`

结论：

- 未发现真实 API Key、私钥或云访问密钥提交。
- 前端没有读取或保存 LLM API Key。
- README 中仅有占位文本 `你的_key`。
- Docker Compose 只通过环境变量透传 Key，不硬编码真实值。

## OWASP 检查

### A01 Broken Access Control

Phase 2C 未新增用户账号、权限或多租户边界。当前仍是单用户本地工作台，不存在跨用户对象访问面。

### A02 Cryptographic Failures

API Key 不在仓库中持久化，不下发前端。当前没有引入自定义加密逻辑。

### A03 Injection

LLM prompt 接收的是已有结构化 `strengths`、`gaps` 和 `score_items` 摘要，不执行代码、不拼接 SQL、不触发 shell。LLM 输出必须经过 Pydantic schema 校验。

### A04 Insecure Design

LLM 失败不阻断主流程，回退本地 fallback。LLM 不参与最终数字评分，避免外部模型污染可信评分。

### A05 Security Misconfiguration

LLM 默认关闭。只有同时配置 `CAREERFIT_LLM_ENABLED=true`、API Key 和 model 时 capability 才进入 `ready`。

### A06 Vulnerable and Outdated Components

新增生产依赖 `httpx>=0.27`，属于成熟 HTTP 客户端。未新增重型或未知供应链依赖。

### A09 Security Logging and Monitoring Failures

当前代码没有记录 prompt、headers 或 API Key。错误信息只返回受控异常，不包含 provider 响应正文。

### A10 SSRF

`CAREERFIT_LLM_BASE_URL` 来自后端环境变量，属于部署者可信配置；前端和用户输入不能修改 base URL。

## STRIDE 威胁模型

| 组件 | Spoofing | Tampering | Repudiation | Information Disclosure | Denial of Service | Elevation of Privilege |
|---|---|---|---|---|---|---|
| LLM 配置 | Key 来自后端环境变量，前端不能伪造 | 部署者可改环境变量 | 本地无审计日志，Phase 2C 可接受 | Key 不下发前端 | 外部 provider 慢会影响分析节点，但有超时 | 不引入账号权限 |
| LLM client | Bearer token 只在请求 header 中使用 | 请求体由 prompt builder 构造 | 未记录调用历史 | 不记录 headers / prompt | 设置 `llm_timeout_seconds` | 无权限提升路径 |
| Prompt builder | 用户简历/JD 间接进入结构化摘要 | 用户输入可能影响 prompt 内容 | 不保存 prompt | 不传完整简历/JD，只传摘要证据 | prompt 长度未做硬限制，后续可加 token budget | 无权限提升路径 |
| Agent trace | trace 使用脱敏快照 | LLM 输出会进入报告 | trace 保存节点状态 | 已拦截 `raw_jd`、`raw_resume`、`prompt`、`messages`、`api_key` | 无新增 DoS 面 | 无权限提升路径 |

## LLM 安全结论

- LLM 不决定 `final_score` 或 `score_breakdown`。
- LLM 输出必须符合 `LLMReportEnhancement` schema。
- 非法 JSON 只允许一次修复重试。
- provider 失败、超时或非法输出时，分析任务回退本地 fallback。
- 简历建议仍经过 `Integrity Guard`。
- `agent_runs` 测试已覆盖不暴露 API Key、prompt、完整 JD、完整简历。

## 残余风险

- Prompt 中仍包含结构化证据摘要，可能包含用户简历/JD 的短片段。这是生成建议所需的最小上下文，风险可接受；后续可增加证据片段长度上限。
- 当前没有 token/cost 上限。Phase 2C 通过单次调用和 timeout 控制风险，后续如开放更多调用入口，应增加 cost budget。
- 当前没有 provider allowlist。`base_url` 由后端环境变量控制，部署者可信；若未来开放前端配置，必须加 allowlist。

## 最终结论

未发现 8/10 以上可信度的安全阻断问题。Phase 2C 可继续交付，但上线真实外部 provider 前应使用最小权限 API Key，并避免把 `.env` 提交到仓库。

免责声明：本记录是 AI 辅助安全审计，不替代专业渗透测试。生产环境处理敏感数据时仍建议进行专业安全评估。

