# CareerFit Agent Phase 1 审查与安全收口记录

日期：2026-05-03
分支：`codex/phase-2a-learning-loop`
范围：Phase 1 完成后的 Phase 1.5 收口，覆盖产品边界、设计验收、工程质量门与 PII 安全基线。

## 审查结论摘要

### plan-ceo-review：Hold Scope

结论：通过，保持 Phase 1 的单用户个人求职成长工作台定位。

- 不扩大到 HR 端、导师端、登录、多租户或协作分享。
- 不把产品降级成一次性 Demo；下一阶段继续围绕“报告 -> Next Best Action -> 学习任务 -> 新简历版本 -> 再分析”闭环推进。
- Phase 2A 只做学习任务闭环真实化，不引入报告导出、PDF/DOCX 解析、外部课程爬取或生产级 worker。

### plan-design-review：体验门

结论：通过，Phase 1 的设计方向可以作为 Phase 2A 基线。

- 工作台仍是第一屏，不能改成营销首页。
- `Next Best Action` 必须继续放在工作台首屏和报告头部显眼位。
- 风险信息继续执行色彩 + 文字双通道，不允许只靠红黄绿表达风险。
- `/learning` 从“功能尚未上线”升级为真实任务视图时，仍必须保留空、加载、错误、部分数据、后端不可用状态。

### plan-eng-review：工程质量门

结论：通过，但 Phase 2A 需要先补学习任务的持久化边界和状态机测试。

- 后端 route 继续只做请求解析、依赖注入和响应返回；学习任务生成逻辑放到 `backend/app/services/learning_service.py`。
- 学习任务必须关联 `analysis_tasks` 与 `analysis_reports`，并保留 `schema_version`。
- 生成任务必须幂等，同一报告重复生成不得产生重复任务。
- 前端不得用 mock 数据假装学习任务存在；learning capability 未 ready 时继续显示 `BackendNotReadyNotice`。

## gstack:cso 安全审计记录

### 执行情况

计划要求运行：

```powershell
gstack:cso
```

实际结果：当前 PowerShell 环境没有 `gstack:cso` 可执行入口。

```text
The term 'gstack:cso' is not recognized as a name of a cmdlet, function, script file, or executable program.
```

处理方式：已读取本地 `gstack:cso` skill 文档，并按其“本地代码审计 + OWASP + STRIDE”要求完成一次 PII 入口基线审查。本记录不是说 CLI 命令成功运行，而是记录命令不可用后的人工等价审计结果。

### 审计范围

- 简历/JD 输入入口：`backend/app/api/routes/jobs.py`、`backend/app/api/routes/resumes.py`
- 解析与证据提取：`backend/app/services/job_service.py`、`backend/app/services/resume_service.py`
- Agent 节点与 trace：`backend/app/agents/nodes.py`、`backend/app/agents/graph.py`
- 报告与 Agent run schema：`backend/app/schemas/reports.py`
- 前端本地存储：`frontend/src/composables/useLocalStorageRef.ts`、`frontend/src/stores/preferences.ts`
- 环境与容器：`backend/app/core/config.py`、`docker-compose.yml`
- 秘钥模式扫描：API key、数据库 URL、密码、私钥常见模式

### OWASP 结论

| 类别 | 结论 | 证据 |
|---|---|---|
| A01 Broken Access Control | Phase 1 是单用户本地工作台，无账号边界；Phase 2A 不引入登录或多租户。当前 API 没有用户隔离，不得部署为多用户服务。 | `AGENTS.md` 明确禁止登录和多租户。 |
| A02 Cryptographic Failures | 未发现 API key 或私钥提交；Docker 示例数据库密码为本地开发默认值。 | 秘钥扫描只命中 `.env.example`、`docker-compose.yml` 示例配置。 |
| A03 Injection | 解析逻辑为本地正则和确定性评分，无 SQL 字符串拼接。 | SQLAlchemy ORM 查询，未见手写 SQL。 |
| A04 Insecure Design | 发现一个设计风险：`JobRead` / `ResumeRead` 当前返回 `raw_text`，管理视图会拿到完整 JD/简历原文。单用户本地可接受，但生产化前必须改成详情权限或脱敏摘要。 | `backend/app/schemas/jobs.py`、`backend/app/schemas/resumes.py`。 |
| A05 Security Misconfiguration | CORS 只允许本地前端地址；Docker 端口直接暴露本地服务，符合开发态。 | `backend/app/main.py`、`docker-compose.yml`。 |
| A06 Vulnerable Components | 本次未运行依赖漏洞库查询；Phase 2A 实现后需补 `npm audit` 或等价 dependency audit。 | 当前任务为 PII 入口基线。 |
| A09 Logging and Monitoring Failures | 未发现后端显式记录原始简历/JD 的日志；Agent trace 对外响应已有递归脱敏。 | `backend/app/agents/graph.py`。 |
| A10 SSRF | 当前无外部 URL 抓取、文件上传或远程资源解析。 | Phase 1 范围不含爬取和 PDF/DOCX 解析。 |

### STRIDE 结论

| 威胁 | 当前判断 | Phase 2A 要求 |
|---|---|---|
| Spoofing | 无账号系统，不存在身份冒充边界；也因此不能对公网多用户部署。 | 不引入账号，不把单用户数据当多用户隔离数据。 |
| Tampering | 学习任务状态更新会成为新写入口，需要明确合法状态流转。 | `not_started`、`doing`、`done`、`paused` 必须由 schema 和 service 双层约束。 |
| Repudiation | 现有 `analysis_tasks`、`analysis_reports`、`agent_runs` 可追踪主路径；学习任务更新还没有审计字段。 | `updated_at` 必须更新，后续如需要可加本地事件日志。 |
| Information Disclosure | Agent trace 对外脱敏有效；但岗位/简历管理 API 返回 `raw_text`。 | 学习任务响应不得包含 `raw_text`、`raw_jd`、`raw_resume` 或完整证据原文。 |
| Denial of Service | 输入长度只靠 Pydantic 最小长度，没有最大长度。 | Phase 2A 不新增大文本入口；后续应给 JD/简历原文补最大长度。 |
| Elevation of Privilege | 无权限系统，无提权路径；同样说明不能上线为共享服务。 | Phase 2A 不新增权限概念。 |

## 安全发现

### S1：岗位与简历读取 API 返回原始文本

严重性：Medium

位置：

- `backend/app/schemas/jobs.py`
- `backend/app/schemas/resumes.py`

说明：`JobRead` 与 `ResumeRead` 包含 `raw_text`，这会让前端管理页拿到完整 JD 和简历原文。Phase 1 是本地单用户工作台，这不是立即阻塞项；但它是 PII 泄露面，生产化、多用户或分享能力之前必须拆分为内部详情 schema 与 UI 脱敏摘要 schema。

Phase 2A 处理：学习任务 API 不得沿用该模式。任务响应只能包含短标题、维度、理由和证据引用，不返回原文。

### S2：输入长度缺少上限

严重性：Low

位置：

- `backend/app/schemas/jobs.py`
- `backend/app/schemas/resumes.py`

说明：`raw_text` 只有 `min_length=20`，没有 `max_length`。本地开发影响有限，但长文本可能拖慢解析、评分和 trace 持久化。

Phase 2A 处理：不新增大文本入口。后续 Phase 2B 或安全修复任务应给 JD/简历文本补最大长度，并加测试。

### S3：本地存储黑名单未覆盖 `agent_trace_raw`

严重性：Low

位置：

- `frontend/src/composables/useLocalStorageRef.ts`

说明：当前黑名单覆盖 `raw_jd`、`raw_resume` 和 1KB 以上字符串，测试计划曾要求覆盖 `agent_trace_raw`。由于 `preferences` store 当前只保存主题、密度和 recentLimit，未发现实际写入 trace 的路径。

Phase 2A 处理：新增 `learning` store 时不得复用 localStorage 保存任务详情；后续可把 `agent_trace_raw` 加入黑名单测试。

## Phase 2A 安全门

- 学习任务生成必须从 `analysis_reports.learning_plan`、`gaps`、`next_best_action` 派生，不得读取或返回原始简历/JD。
- `evidence_refs` 只能保存证据 ID、维度或短摘要，不保存完整证据句子。
- 状态更新 route 不接受任意 JSON 合并，只接受枚举状态。
- 前端 learning store 不写 localStorage / IndexedDB。
- `Next Best Action` 跳转只允许携带任务 ID 或分析任务 ID，不允许把报告正文放进 query。

## 后续修复建议

- Phase 2A 内强制：学习任务 API 不返回任何原始文本。
- Phase 2B 前建议：新增 `JobSummaryRead` / `ResumeSummaryRead`，管理列表不返回 `raw_text`。
- 生产化前必须：引入明确部署边界、密钥管理、依赖漏洞扫描和输入大小限制。
