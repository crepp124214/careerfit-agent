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

- `superpowers` 用于生成和执行结构化工作流：
  - `brainstorming`：产品/功能构思和设计确认。
  - `writing-plans`：把已确认设计拆成可执行实施计划。
  - `subagent-driven-development` 或 `executing-plans`：按计划实施。
  - `verification-before-completion`：完成前验证。
- `gstack` 用于增强审查和质量门：
  - `autoplan`：自动跑产品、设计、工程审查。
  - `plan-ceo-review`：产品和范围审查。
  - `plan-design-review`：体验和 UI 计划审查。
  - `plan-eng-review`：工程架构、测试、性能和风险审查。

### 顺序

推荐默认顺序：

```text
superpowers:brainstorming
  -> gstack:autoplan
  -> superpowers:writing-plans
  -> superpowers:subagent-driven-development 或 superpowers:executing-plans
  -> superpowers:verification-before-completion
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

## 实现约束

- 先完成可信端到端闭环，再扩展页面和功能。
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

## Git 与交付

- 每个独立任务完成并验证后再提交。
- 提交信息使用英文 Conventional Commits，例如：
  - `feat: add deterministic scoring`
  - `docs: update phase 1 plan`
  - `test: cover integrity guard`
- 提交前必须检查：
  - `git status --short`
  - 对应测试命令已运行，或明确说明无法运行的原因。
- 不得回滚用户或其他工具已经产生的无关变更。
