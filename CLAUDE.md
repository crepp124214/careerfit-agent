# CareerFit Agent 项目协作约束

本文件是本仓库的项目级工作约束。后续所有设计、计划、实现、审查和交付都必须优先遵守这里的规则；如果用户在当前对话中给出更新指令，以用户最新指令为准。

## 语言与文档

- 所有项目文档必须使用中文编写，包括设计文档、实施计划、测试计划、TODO、README、评审记录和阶段总结。
- 代码标识符、文件名、API 路径、命令、错误信息、第三方库名称可以保留英文。
- 面向用户的最终说明默认使用中文。
- 如果引用已有英文内容，必须补充中文解释，避免只留下英文结论。
- 新增文档、重写文档、追加评审记录时，都必须先检查是否满足中文文档约束。
- 不允许新增只有英文说明的 Markdown 文档；如果第三方模板是英文，必须改写为中文说明后再提交。

## 当前文档基线

以下文档已经完成中文化，后续修改必须保持中文：

- `docs/superpowers/specs/2026-05-02-careerfit-agent-design.md`
- `docs/superpowers/plans/2026-05-02-careerfit-agent-phase-1.md`
- `docs/superpowers/test-plans/2026-05-02-careerfit-agent-test-plan.md`
- `docs/DESIGN.md`（视觉设计系统；YAML token key 保留英文以兼容 `npx @google/design.md lint`，描述与正文为中文）
- `TODOS.md`
- `CLAUDE.md`

外部同步副本：

- `C:\Users\qwer\.gstack\projects\Newproject\main-test-plan-2026-05-02-careerfit-agent.md`

如果修改了项目内测试计划，必须同步更新上面的 gstack 测试计划副本。

## 实施文档实时更新

- 执行任何实现任务时，必须实时更新对应实施计划中的 checklist 状态。
- 当前 Phase 1 实施计划位置：
  `docs/superpowers/plans/2026-05-02-careerfit-agent-phase-1.md`
- 每完成一个步骤，立即把该步骤从 `- [ ]` 改为 `- [x]`。
- 如果执行时发现计划不准确，必须先更新计划，再继续实现。
- 如果新增、删除或调整任务范围，必须同步更新：
  - 实施计划
  - 测试计划
  - `TODOS.md`
  - 设计文档中的相关约束，若变更影响产品或架构决策
- 不允许出现“代码已经变了，但计划文档还是旧的”的状态。
- 每次提交代码前，检查本次变更是否影响实施计划、测试计划、设计文档或 `TODOS.md`。
- 如果影响，必须把文档更新和代码变更放在同一个提交，除非用户明确要求拆分。
- 如果某一步执行失败，必须在实施计划对应步骤附近记录失败原因、已验证命令和下一步修正方向。
- 如果因为环境限制无法运行某个验证命令，必须在最终说明中写清楚未运行原因，并在实施计划中保留该步骤未完成。

## gstack 与 superpowers 协作约束

### 分工

官方仓库：[`superpowers`](https://github.com/obra/superpowers) 与 [`gstack`](https://github.com/garrytan/gstack)。两者都是 Claude Code 的 plugin/skill，通过 `Skill` 工具或 `/<skill-name>` 调用。

`superpowers` 用于生成和执行结构化工作流，按用途分组：

- 会话入口：
  - `using-superpowers`：会话开始时读取，建立"先查 skill 再回答"的纪律。
- 设计与计划：
  - `brainstorming`：产品/功能构思和设计确认。
  - `writing-plans`：把已确认设计拆成可执行实施计划。
- 实施：
  - `subagent-driven-development` 或 `executing-plans`：按计划实施。
  - `dispatching-parallel-agents`：并行子 Agent，可拆分前后端独立验证。
  - `using-git-worktrees`：worktree 隔离开发，匹配"先修计划再改代码"原则。
- 测试与调试：
  - `test-driven-development`：红-绿-重构循环；评分规则、Integrity Guard、证据链单测必须走这条路径。
  - `systematic-debugging`：4 阶段根因分析；适用 LangGraph 节点失败、LLM 非法 JSON 修复重试场景。
- 完成与交付：
  - `requesting-code-review`：commit 前的代码自审清单。
  - `verification-before-completion`：完成前验证。
  - `finishing-a-development-branch`：合并、PR、清理的决策流程。

`gstack` 用于增强审查和质量门：

- 立项前：
  - `office-hours`：YC 式六问重新框定；建议放在 `brainstorming` 之前。
- 计划审查：
  - `autoplan`：自动跑 CEO、Design、Eng、DevEx 四份审查。
  - `plan-ceo-review`：产品和范围审查；本项目必须以 "Hold Scope" 模式调用，避免反向扩大 CareerFit 边界。
  - `plan-design-review`：体验和 UI 计划审查（信息性）。
  - `plan-eng-review`：工程架构、测试、性能和风险审查；**这是唯一强制门**，输出的测试计划会被 `qa` 自动消费。
  - `plan-devex-review`：DX 审查（信息性）。
  - `plan-tune`：校准审查问题敏感度。
- 实施期：
  - `review`：staff-eng 级代码审查，配合 `superpowers:requesting-code-review`。
  - `investigate`：根因调查。
- 完成与回归：
  - `qa` / `qa-only`：用 `plan-eng-review` 写出的测试计划做回归测试。
  - `health`：typecheck / lint / test / 死代码仪表盘。
  - `cso`：OWASP + STRIDE 安全审计；本项目对简历/JD 输入解析、Agent prompt 装配、向量入库这些 PII 入口必跑。
- 部署：
  - `ship` / `land-and-deploy` / `canary`：发布相关；Phase 1 不强制使用，Phase 2+ 视部署形态启用。

### 顺序

推荐默认顺序（粗体为强制门）：

```text
gstack:office-hours
  -> superpowers:brainstorming
  -> gstack:autoplan（其中 plan-eng-review 强制；plan-ceo-review 用 Hold Scope 模式）
  -> superpowers:writing-plans
  -> superpowers:subagent-driven-development 或 superpowers:executing-plans
     （内部使用 superpowers:test-driven-development、superpowers:systematic-debugging）
  -> superpowers:requesting-code-review + gstack:review
  -> gstack:qa
  -> superpowers:verification-before-completion
  -> superpowers:finishing-a-development-branch
```

实施阶段的推荐顺序：

```text
读取 CLAUDE.md
  -> 读取当前实施计划
  -> 执行一个 checklist 步骤
  -> 更新 checklist
  -> 运行对应验证
  -> 更新测试计划或 TODO，若范围变化
  -> 提交
```

### 冲突处理

- 如果 `gstack` 审查结论和 `superpowers` 计划冲突，优先采用更具体、更接近当前实现阶段的结论。
- 如果两者都合理但方向不同，必须记录为决策点，不得静默选择。
- 如果冲突涉及用户明确表达过的边界，以用户边界优先。
- 如果 `gstack` 要求扩大范围，而用户已明确拒绝该范围，不扩大，只把它记录到 `TODOS.md` 的延后事项。
- 如果 `superpowers` 计划遗漏了 `gstack` 已通过的质量门，必须先更新计划再执行。
- 如果执行中发现计划和代码现实冲突，先修计划，再改代码。
- 本项目当前明确边界：
  - 单用户个人求职成长工作台。
  - 不做 HR 端。
  - 不做导师端。
  - 不做登录和多租户。
  - 不把项目降级成一次性 Demo。

## Agent 编码行为准则

参考来源：[forrestchang/andrej-karpathy-skills 的 CLAUDE.md](https://github.com/forrestchang/andrej-karpathy-skills/blob/main/CLAUDE.md)。

- 本节是通用的 Agent 编码行为约束，对本仓库所有写代码、改代码、提交代码的操作生效。
- 当本节与下文的项目专属约束（产品边界、Phase 1 验收门、隐私安全、评分约束、前后端实现约束等）冲突时，以项目专属约束优先。
- 权衡：本节规则倾向于谨慎而非速度；对于明确简单的任务，可以使用判断力，但不得用"小任务"作为绕过约束的理由。

### 1. 编码前先思考

不要替用户做假设。不要隐藏困惑。必须把权衡显式表达出来。

实现之前必须做到：

- 显式陈述自己的假设；如果不确定，先提问，不要直接动手。
- 如果用户的请求存在多种合理解释，必须列出来给用户判断，不允许静默选一种继续。
- 如果存在更简单的方案，必须说明；必要时反向推动用户重新考虑。
- 如果有任何不清楚的点，立即停下来，明确指出哪里不清楚，并提问。

### 2. 简单优先

只写解决问题所需的最少代码，不写任何投机性内容。

- 不允许实现用户没有要求的功能。
- 不允许给只用一次的代码做抽象。
- 不允许加入未被请求的"灵活性"或"可配置性"。
- 不允许为不可能发生的场景写错误处理。
- 如果写出 200 行代码、但 50 行就能解决，必须重写。

自查标准：一位资深工程师会不会觉得这段代码过度复杂？如果会，就简化。

### 3. 外科手术式修改

只动必须动的代码。只清理由自己引入的副作用。

修改既有代码时：

- 不要"顺便改进"相邻的代码、注释或格式。
- 不要重构没有出问题的部分。
- 即使自己有不同偏好，也要匹配既有风格。
- 如果发现无关的死代码，提一下，不要直接删除。

当本次修改产生孤儿代码时：

- 删除因本次修改而不再被使用的 import、变量、函数。
- 不要顺手删除原本就存在的死代码，除非用户明确要求。

判定标准：每一行被改动的代码都必须能直接追溯到用户的请求。

### 4. 目标驱动执行

定义成功标准。围绕标准循环验证，直到达成。

把任务转换成可验证的目标：

- "加校验" → "为非法输入写测试，再让测试通过"。
- "修 bug" → "写一个能复现 bug 的测试，再让它通过"。
- "重构 X" → "保证重构前后测试都通过"。

多步任务必须先列出简短计划：

```text
1. [步骤] → 验证：[检查方式]
2. [步骤] → 验证：[检查方式]
3. [步骤] → 验证：[检查方式]
```

强成功标准能让 Agent 独立循环；弱标准（如"让它跑起来"）会要求不断追问澄清。

判断本节是否生效的指标：

- 提交 diff 中与请求无关的改动更少。
- 因过度设计导致返工的次数更少。
- 澄清问题在动手实现之前提出，而不是在出错之后才暴露。

## 当前核心产品约束

- 项目必须围绕“计算机应届生个人求职成长闭环”展开。
- 核心闭环是：

```text
目标岗位
  -> 简历版本
  -> 匹配分析
  -> 证据链评分
  -> 能力缺口
  -> 诚实简历优化
  -> Next Best Action
  -> 学习任务
  -> 新简历版本
  -> 再分析和趋势对比
```

- `Next Best Action` 是必要能力，不是可选装饰。
- 可解释评分、证据链、Integrity Guard、Agent 运行轨迹是核心能力，不得当作后续优化。
- 简历优化必须遵守：只允许增强表达，不允许新增事实。
- Phase 1 范围按前后端拆分：
  - **后端 Phase 1**：先证明一条可信主路径，不追求功能铺满。主路径定义为：

```text
创建目标岗位
  -> 创建简历版本
  -> 执行分析
  -> 确定性评分
  -> 生成证据链报告
  -> 运行 Integrity Guard
  -> 展示 Agent 运行轨迹
  -> 给出 Next Best Action
```

  - **前端 Phase 1**：完整功能网站。所有规划页面与周边模块（历史趋势、版本对比、学习任务、设置等）都必须可交互、状态完整、UX 抛光达标，详见“前端实现约束”和“Phase 1 验收门 / 前端 Phase 1 验收门”。
- 主路径优先级是**后端独立约束**，前端不受其束缚；前端可在后端主路径未完工时，先把所有页面铺出来。
- 后端范围内：如果某个功能不能增强主路径的可信度，默认延后到 `TODOS.md`。
- 前端范围内：如果某个页面或模块还没有对应后端能力，**不得用 mock 数据假装**，必须用用户可见的“功能未上线 / 等待后端 X”状态告知用户。

## 实现约束

- 后端先完成可信端到端闭环，再扩展功能；前端不受此约束，可并行实现完整网站，但缺口必须用用户可见的状态告知，禁止 mock 数据假装。
- 后端优先保证：
  - Pydantic 输出结构稳定。
  - 确定性评分可复现。
  - Agent 节点可追踪。
  - 报告结论可关联 JD 证据和简历证据。
  - Agent Trace 对 UI 展示脱敏。
- 前端优先保证：
  - 首屏是工作台，不是营销页。
  - 支持空状态、加载状态、失败状态、部分数据状态。
  - 报告结构化展示，避免大段 AI 生成文本。
  - 风险信息不能只靠颜色表达。
- 测试优先覆盖：
  - 评分规则。
  - Integrity Guard。
  - 分析任务主流程。
  - 证据链完整性。
  - Agent Trace 脱敏。
  - Docker 启动路径。

## Phase 1 验收门

Phase 1 验收门按前后端独立判定，两条都达成才算 Phase 1 完成。

### 后端 Phase 1 验收门

- 可以通过 API 创建目标岗位。
- 可以通过 API 创建简历版本。
- 可以选择一个岗位和一个简历版本执行分析。
- 分析任务会持久化 `analysis_tasks`、`analysis_reports` 和 `agent_runs`。
- 报告包含总分、分项评分、优势、缺口、简历建议、面试题、学习计划和 `Next Best Action`。
- 每个评分项至少能追溯到 JD 证据和简历证据。
- `Agent Trace` 对 UI 展示的原始 JD 和简历文本必须脱敏。
- `Integrity Guard` 能阻止无证据指标和夸大职责。
- Docker Compose 可以启动 backend、postgres。

### 前端 Phase 1 验收门

- 所有规划页面（工作台、报告、岗位/简历管理、Agent trace、历史趋势、版本对比、学习任务、设置）全部存在且路由可达。
- 每个页面都支持完整状态机：空、加载、错误、部分数据。
- UX 抛光达标：完整响应式（桌面 + 平板 + 移动端）、键盘可达、ARIA 标签齐全、对比度 WCAG AA、关键交互有动效过渡。
- 后端缺口的页面/模块必须用**用户可见**的“功能未上线 / 等待后端 X”提示告知，禁止 mock 数据假装。
- 风险信息必须色 + 文字双通道。
- 报告结构化展示，避免大段 AI 生成文本堆叠。
- `Next Best Action` 在工作台首屏与报告头部固定显眼位呈现。
- 本地偏好（主题、布局偏好、最近打开等）通过 localStorage / IndexedDB 持久化；**禁止**在本地存储中保存简历原文、JD 原文或 Agent trace 原文。
- 不引入真实账号、登录或多租户。
- Docker Compose 可以启动 frontend。

不满足以上任意一项，不得声称 Phase 1 完成。

## 隐私与安全约束

- 简历、JD、Agent 输入输出都可能包含敏感信息，默认按敏感数据处理。
- 不得在日志、控制台、前端 trace、异常详情中直接输出完整简历原文。
- Agent trace 的 UI 展示必须使用脱敏摘要；服务端内部保存原始快照时，必须明确只用于调试和本地开发。
- `.env`、API Key、模型 Key、数据库密码不得提交到仓库。
- Docker 和前端构建不得暴露后端环境变量。
- 文件上传功能未进入 Phase 1 时，不得临时加入未验证的 PDF/DOCX 解析依赖。
- 简历/JD 输入解析、Agent prompt 装配、向量入库这些 PII 入口，必须由 `gstack:cso` 跑过 OWASP + STRIDE 安全审计；Phase 1 至少留一份基线报告，PII 入口逻辑变更后必须重跑。
- 前端 localStorage / IndexedDB 仅存储 UI 偏好、视图状态和必要元数据（如最近打开的报告 ID、岗位 ID）；不得存储简历原文、JD 原文、Agent trace 原文或任何 PII 内容。前端会话过期或浏览器清空数据后必须能优雅恢复，不依赖本地存储中的内容真实性。

## 评分、RAG 与 Agent 可信度约束

- 最终数字分数必须由确定性评分规则计算，LLM 不得直接决定最终分数。
- 所有评分维度必须 clamp 到 0-100。
- 评分报告必须保存原始评分因子，便于复现和调试。
- RAG 检索结果只能作为证据和标准来源；如果检索不到相关文档，必须标记“知识库证据不足”，不得编造来源。
- Agent 节点输出必须通过 Pydantic schema 或等价结构校验。
- LLM 返回非法 JSON 时，最多允许一次修复重试；仍失败则记录失败节点，不得吞掉错误。
- Integrity Guard 必须在最终简历建议展示前运行。
- 简历优化建议必须包含：
  - 原始依据
  - 优化表达
  - 关联 JD 要求
  - 使用的简历证据
  - 风险等级

## 后端实现约束

- API route 不写业务逻辑，只做参数接收、依赖注入和响应返回。
- Service 层负责编排用例，例如创建分析任务、运行工作流、写入报告。
- Scoring 层只放确定性评分逻辑，不调用 LLM、不访问数据库。
- Agent 层负责节点输入输出、prompt/fallback、trace，不直接处理 HTTP。
- RAG 层负责种子知识、chunk、embedding、retrieval，不混入评分公式。
- 数据库 JSON 字段必须包含 `schema_version`。
- 测试环境优先使用 SQLite 或轻量替身；Docker 环境使用 PostgreSQL + pgvector。
- 如果 SQLite 和 PostgreSQL 行为不一致，必须在计划中记录，并补充 PostgreSQL 集成测试或 Docker smoke test。

## 前端实现约束

- 前端 Phase 1 目标是**完整功能网站**，不是 MVP；具体覆盖范围与验收标准见“Phase 1 验收门 / 前端 Phase 1 验收门”。
- 第一屏必须是“个人求职工作台”，不得做营销首页。
- 所有规划页面（工作台、报告、岗位/简历管理、Agent trace、历史趋势、版本对比、学习任务、设置）都必须存在且路由可达，缺一不可。
- 每个页面必须支持完整状态机：空、加载、错误、部分数据。
- **后端缺口的诚实告知规则**：当前端某页面/模块对应的后端能力尚未实现时，必须以**用户可见**的方式提示，例如 inline banner、灰底卡片或独立空状态文案，明确写出“功能尚未上线”或“等待后端 X 完成”。**禁止**用 mock 数据、假数据、硬编码示例数据填充该区域；也禁止把该页面或路由直接隐藏导致用户感知不到功能存在。
- 报告必须结构化展示，避免大段 AI 生成文本堆叠。
- `Next Best Action` 必须在报告头部或工作台显眼位置展示。
- 风险提示必须色 + 文字双通道，不能只依赖颜色。
- 所有按钮、输入框和错误提示必须有清晰状态：默认、hover、focus、active、disabled、loading、error。
- 完整响应式：桌面、平板、移动端三套断点都达标，移动端不再仅“保证报告可读”，工作台与所有核心页面都必须可用。
- 完整无障碍：键盘可达、ARIA 标签齐全、对比度满足 WCAG AA。
- UX 抛光：状态切换、模态、Trace 展开等关键交互必须有动效过渡，避免硬切换。
- 周边模块（历史趋势、版本对比、学习任务、个人偏好设置）必须可交互；后端能力未到位时按上面的“诚实告知规则”处理。
- 本地偏好/会话使用 localStorage / IndexedDB，仅存 UI 偏好、视图状态、最近打开元数据；**禁止**存储简历原文、JD 原文、Agent trace 原文等 PII 内容。
- 不引入真实账号系统、登录、注册或多租户。CLAUDE.md 关于“不做登录和多租户”的硬边界保持不变。
- 前端为支撑完整功能网站可以引入必要的 UI 组件库、动效库、图表/可视化库、状态管理库、表单库；新增依赖仍需满足“依赖与技术取舍”节的通用原则。

## 依赖与技术取舍

- 不为小功能引入重依赖。
- 新增依赖前必须确认：
  - 是否是 Phase 1 主路径必需。
  - 是否已有标准库或现有依赖可完成。
  - 是否会增加 Docker 构建复杂度。
- Phase 1 后端不引入 Celery、Redis、复杂权限库、PDF/DOCX 解析库，除非用户明确要求。
- Phase 1 前端为支撑完整功能网站，可按需引入 UI 组件库、动效库、图表/可视化库、状态管理库、表单库；选型仍需满足上述“是否已有可用替代”“是否会增加 Docker 构建复杂度”的检查，并且不得引入真实账号/多租户相关库。
- LangGraph 可以先通过兼容 workflow boundary 接入；如果实际实现先用本地顺序 runner，也必须保留后续替换为 LangGraph 的边界。

## 验证命令基线

根据本次变更范围运行对应命令：

- 后端变更：

```powershell
cd backend
pytest -q
```

- 前端变更：

```powershell
cd frontend
npm test
```

- Docker 或环境变更：

```powershell
docker compose up --build
```

- 文档变更：

```powershell
git diff --check
```

- 计划或测试计划变更后：用 `gstack:qa-only` 校验现有测试计划仍可执行（即 `plan-eng-review` 写出的测试计划与代码现状是否一致）。
- 周期性健康检查：用 `gstack:health` 看 typecheck / lint / test / 死代码状态，建议每个里程碑前跑一次。
- PII 入口逻辑变更后：用 `gstack:cso` 复核 OWASP + STRIDE 安全审计，确保未引入新的注入或泄露面。

如果命令无法运行，必须说明原因，不能把未验证内容说成已通过。

## Git 与交付

- 每个独立任务完成并验证后再提交。
- 提交信息使用英文 Conventional Commits，例如：
  - `feat: add deterministic scoring`
  - `docs: update phase 1 plan`
  - `test: cover integrity guard`
- 提交前必须检查：
  - `git status --short`
  - 对应测试命令已运行，或明确说明无法运行的原因。
  - 重要变更已经过 `superpowers:requesting-code-review` 自审或 `gstack:review` 工程审查。
- 不得回滚用户或其他工具已经产生的无关变更。
- 一段开发分支收尾时，使用 `superpowers:finishing-a-development-branch` 决定合并、发 PR 还是丢弃，避免遗留半成品分支。

## Skill routing

当用户请求匹配下列关键词时，必须通过 `Skill` 工具调用对应 skill；不确定时优先调用而非自己手写流程。

关键路由规则：

- 产品想法 / brainstorm → `superpowers:brainstorming` 或 `gstack:office-hours`
- 立项前六问重塑 / scope 模糊 → `gstack:office-hours`
- 战略 / 范围审查 → `gstack:plan-ceo-review`（本项目默认 Hold Scope 模式）
- 架构审查 → `gstack:plan-eng-review`
- 设计系统 / 体验计划审查 → `gstack:design-consultation` 或 `gstack:plan-design-review`
- 完整四阶段审查（CEO / Design / Eng / DX） → `gstack:autoplan`
- bug / 错误调查 → `gstack:investigate` 或 `superpowers:systematic-debugging`
- QA / 回归 → `gstack:qa` 或 `gstack:qa-only`
- 代码审查 / diff 自审 → `gstack:review` 或 `superpowers:requesting-code-review`
- 视觉打磨 → `gstack:design-review`
- 提交 / 部署 / PR → `gstack:ship` 或 `gstack:land-and-deploy`
- 保存进度 → `gstack:context-save`
- 恢复上下文 → `gstack:context-restore`
- 写计划 → `superpowers:writing-plans`
- 执行计划 → `superpowers:subagent-driven-development` 或 `superpowers:executing-plans`
- TDD → `superpowers:test-driven-development`
- 完成验证 → `superpowers:verification-before-completion`
- 分支收尾 → `superpowers:finishing-a-development-branch`
- PII / 安全审计 → `gstack:cso`（本项目简历/JD 解析、Agent prompt、向量入库变更后必跑）
- typecheck / lint / 死代码仪表盘 → `gstack:health`

