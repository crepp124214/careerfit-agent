---
version: 0.1-careerfit
name: CareerFit Agent
description: "面向单用户求职可信工作台的暗色设计系统。继承 Linear 的四级 surface 阶梯、唯一 lavender 强调色和密集排印风格，但把"产品 UI 截图作为主角"重写为"评分报告卡 / 证据链卡 / Agent 运行轨迹"作为主角。新增 risk 语义色族（high/medium/low），强制配套文字标签，避免单一红色风险信息表达。新增 nextBestAction-callout 组件，作为报告头部和工作台首屏的固定模块，承载 CLAUDE.md 强制约束的 Next Best Action 显眼位。Agent Trace 时间线表面化但严格脱敏，UI 层只渲染摘要，不渲染原始 JD/简历文本。底色沿用 Linear canvas #010102，单色强调沿用 lavender #5e6ad2，但二者权重重新分配：lavender 主要用于 Next Best Action 与可执行行动入口，而非营销 CTA。"

# 优先级声明
# - 本文件为 CareerFit Agent 的视觉设计系统约束。
# - 当本文件与项目根目录 CLAUDE.md 冲突时，以 CLAUDE.md 为准。
# - 本文件参考来源：C:/Users/qwer/.claude/skills/awesome-design-md/design-md/linear.app/DESIGN.md
#   （VoltAgent/awesome-design-md 仓库，Linear 设计系统提取版本）。

colors:
  # 主强调色 —— 仅用于 Next Best Action、主行动按钮、品牌、focus
  primary: "#5e6ad2"
  on-primary: "#ffffff"
  primary-hover: "#828fff"
  primary-focus: "#5e69d1"

  # 文字
  ink: "#f7f8f8"
  ink-muted: "#d0d6e0"
  ink-subtle: "#8a8f98"
  ink-tertiary: "#62666d"

  # 表面阶梯（4 级 surface ladder）
  canvas: "#010102"
  surface-1: "#0f1011"
  surface-2: "#141516"
  surface-3: "#18191a"
  surface-4: "#191a1b"

  # 1px 细分隔线
  hairline: "#23252a"
  hairline-strong: "#34343a"
  hairline-tertiary: "#3e3e44"

  # 反色（极少用，仅用于个别强行动入口的对照面）
  inverse-canvas: "#ffffff"
  inverse-surface-1: "#f5f6f6"
  inverse-ink: "#000000"

  # 语义色 —— 风险三档，必须搭配文字标签
  risk-high: "#e5484d"        # 高风险 / Integrity Guard 拦截 / 严重夸大
  risk-high-bg: "#3a1418"
  risk-medium: "#f5a524"      # 中风险 / 缺口需关注 / 简历建议待审
  risk-medium-bg: "#3a2a10"
  risk-low: "#27a644"         # 低风险 / 通过 / 证据充分
  risk-low-bg: "#0f2418"

  # 信息色 —— Agent trace 节点状态（中性，不参与风险表达）
  info-trace: "#5b8def"
  info-trace-bg: "#0f1c33"

  # 蒙版
  semantic-overlay: "#000000"

typography:
  display-xl:
    fontFamily: Inter
    fontSize: 64px
    fontWeight: 600
    lineHeight: 1.05
    letterSpacing: -2.4px
  display-lg:
    fontFamily: Inter
    fontSize: 44px
    fontWeight: 600
    lineHeight: 1.10
    letterSpacing: -1.4px
  display-md:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: -0.8px
  headline:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: 600
    lineHeight: 1.20
    letterSpacing: -0.4px
  card-title:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: 500
    lineHeight: 1.25
    letterSpacing: -0.2px
  subhead:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: 400
    lineHeight: 1.40
    letterSpacing: -0.1px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: -0.05px
  body:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: 0
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.50
    letterSpacing: 0
  caption:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.40
    letterSpacing: 0
  button:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: 500
    lineHeight: 1.20
    letterSpacing: 0
  eyebrow:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1.30
    letterSpacing: 0.4px
  mono:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.50
    letterSpacing: 0

rounded:
  xs: 4px
  sm: 6px
  md: 8px
  lg: 12px
  xl: 16px
  xxl: 24px
  pill: 9999px
  full: 9999px

spacing:
  xxs: 4px
  xs: 8px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 48px
  section: 64px

components:
  # 主行动 —— Next Best Action 触发按钮、开始分析按钮
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.button}"
    rounded: "{rounded.md}"
    padding: 8px 14px
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
    textColor: "{colors.on-primary}"
    typography: "{typography.button}"
    rounded: "{rounded.md}"
  button-primary-pressed:
    backgroundColor: "{colors.primary-focus}"
    textColor: "{colors.on-primary}"
    typography: "{typography.button}"
    rounded: "{rounded.md}"

  # 次行动 —— 跳转岗位、跳转简历版本、查看证据
  button-secondary:
    backgroundColor: "{colors.surface-1}"
    textColor: "{colors.ink}"
    typography: "{typography.button}"
    rounded: "{rounded.md}"
    padding: 8px 14px
    border: "1px solid {colors.hairline}"

  # 弱行动 —— 取消、关闭、展开/收起
  button-tertiary:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink-muted}"
    typography: "{typography.button}"
    rounded: "{rounded.md}"
    padding: 8px 14px

  # 表单
  text-input:
    backgroundColor: "{colors.surface-1}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: 10px 12px
    border: "1px solid {colors.hairline}"
  text-input-focused:
    backgroundColor: "{colors.surface-1}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: 10px 12px
    border: "1px solid {colors.primary-focus}"
  textarea:
    backgroundColor: "{colors.surface-1}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: 12px 14px
    minHeight: 200px
    border: "1px solid {colors.hairline}"

  # 工作台核心卡片
  workbench-card:
    backgroundColor: "{colors.surface-1}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.lg}"
    padding: 24px
    border: "1px solid {colors.hairline}"

  # 评分总览卡 —— 总分、维度小分一览
  scoring-overview-card:
    backgroundColor: "{colors.surface-1}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.xl}"
    padding: 32px
    border: "1px solid {colors.hairline}"

  # 评分维度卡 —— 单一维度的分数、阈值、原因
  scoring-dimension-card:
    backgroundColor: "{colors.surface-2}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.lg}"
    padding: 20px
    border: "1px solid {colors.hairline}"

  # 证据链卡 —— 一条评分证据：JD 引用 + 简历引用 + 关联评分维度
  evidence-card:
    backgroundColor: "{colors.surface-2}"
    textColor: "{colors.ink}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.lg}"
    padding: 16px 20px
    border: "1px solid {colors.hairline}"

  # 简历建议卡 —— 必须包含原始依据 / 优化表达 / JD 关联 / 简历证据 / 风险等级
  suggestion-card:
    backgroundColor: "{colors.surface-1}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.lg}"
    padding: 24px
    border: "1px solid {colors.hairline}"

  # Next Best Action 强调卡 —— 工作台首屏 / 报告头部固定位
  next-best-action-callout:
    backgroundColor: "{colors.surface-1}"
    textColor: "{colors.ink}"
    typography: "{typography.headline}"
    rounded: "{rounded.lg}"
    padding: 24px 28px
    border: "1px solid {colors.hairline}"
    leadingAccent: "4px solid {colors.primary}"

  # Agent 运行轨迹行 —— 已脱敏摘要
  agent-trace-row:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.xs}"
    padding: 16px 0
    border: "0 0 1px 0 solid {colors.hairline}"

  # 风险标签 —— 必须有文字 + 颜色双通道
  risk-pill-high:
    backgroundColor: "{colors.risk-high-bg}"
    textColor: "{colors.risk-high}"
    typography: "{typography.caption}"
    rounded: "{rounded.pill}"
    padding: 2px 10px
    requiresLabel: "高风险"
  risk-pill-medium:
    backgroundColor: "{colors.risk-medium-bg}"
    textColor: "{colors.risk-medium}"
    typography: "{typography.caption}"
    rounded: "{rounded.pill}"
    padding: 2px 10px
    requiresLabel: "需关注"
  risk-pill-low:
    backgroundColor: "{colors.risk-low-bg}"
    textColor: "{colors.risk-low}"
    typography: "{typography.caption}"
    rounded: "{rounded.pill}"
    padding: 2px 10px
    requiresLabel: "通过"

  # Integrity Guard 拦截横幅
  integrity-guard-banner:
    backgroundColor: "{colors.risk-high-bg}"
    textColor: "{colors.risk-high}"
    typography: "{typography.body}"
    rounded: "{rounded.lg}"
    padding: 16px 20px
    border: "1px solid {colors.risk-high}"

  # 状态徽章
  status-badge:
    backgroundColor: "{colors.surface-2}"
    textColor: "{colors.ink-muted}"
    typography: "{typography.caption}"
    rounded: "{rounded.pill}"
    padding: 2px 8px

  # 顶部导航
  top-nav:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.xs}"
    height: 56px
    border: "0 0 1px 0 solid {colors.hairline}"

  # 底部状态栏（替代营销 footer，工作台天然不需要营销）
  workbench-status-bar:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink-subtle}"
    typography: "{typography.caption}"
    rounded: "{rounded.xs}"
    padding: 12px 24px
    border: "1px 0 0 0 solid {colors.hairline}"
---

## 概览

CareerFit Agent 是单用户的求职可信工作台。视觉系统的目标不是“做一个好看的产品页”，而是“让一份评分报告看起来值得相信”。

底色沿用 Linear 的近黑 `{colors.canvas}` `#010102`，在其上叠 4 级 surface 阶梯（`{colors.surface-1}` 到 `{colors.surface-4}`）来承载报告头、评分卡、证据链、Agent trace 这些天然分层的信息。1 px hairline `{colors.hairline}` 替代阴影，避免在密集报告中堆叠投影造成视觉噪点。

唯一彩色强调 `{colors.primary}` `#5e6ad2`（Linear lavender）只在三种位置出现：

1. `next-best-action-callout` 的左侧色条与按钮
2. 主行动按钮（开始分析、生成新版本）
3. 输入框 focus ring

不允许出现第二种品牌强调色，更不允许把 lavender 当作背景大面积使用。

风险信息走独立的 `risk-*` 色族（high/medium/low），并强制配套 `requiresLabel` 文字标签，满足 CLAUDE.md “风险提示不能只依赖颜色，必须有文字标签”的硬约束。

排印从 Linear 的 80 px 巨大 hero 缩到 64 px 起步，因为 CareerFit 不做营销页，最大字号出现在工作台标题和报告总分。中文采用系统中文字体降级，西文采用 Inter，等宽采用 JetBrains Mono。Linear 自有字族不强制接入。

页面节奏不是 Linear 的“产品 UI 截图作为主角”，而是 **结构化报告卡作为主角**：评分总览卡、证据链卡、简历建议卡。所有卡片都拒绝大段 AI 生成纯文本堆叠，必须以结构化字段呈现。

**核心特征**：
- 暗色工作台（不做亮色主题，Phase 1 不实现）。
- 唯一 lavender `#5e6ad2`，权重让给 Next Best Action 而不是营销 CTA。
- 4 级 surface 阶梯承载报告分层，无投影。
- 风险三档色 + 强制文字标签的双通道表达。
- `next-best-action-callout` 作为工作台首屏与报告头部的固定显眼位。
- Agent trace 表面化展示，但 UI 层只渲染脱敏摘要，绝不渲染原始 JD / 简历文本。

## 颜色

> 参考来源：Linear DESIGN.md 的颜色阶梯；新增 risk 与 info-trace 色族为本项目自定义。

### 品牌与主强调
- **Lavender**（`{colors.primary}`）：Next Best Action callout 的色条与按钮、主行动按钮、focus ring。**禁止**作为大面积背景或第二类强调。
- **Lavender Hover**（`{colors.primary-hover}`）：主按钮 hover。
- **Lavender Focus**（`{colors.primary-focus}`）：输入框 focus ring，2px 描边 50% 透明度。

### 表面（4 级 surface ladder）
- **Canvas**（`{colors.canvas}`，`#010102`）：默认页面背景。
- **Surface 1**（`{colors.surface-1}`）：工作台卡片、评分总览卡、简历建议卡。
- **Surface 2**（`{colors.surface-2}`）：评分维度卡、证据链卡、被 hover 的卡片。
- **Surface 3**（`{colors.surface-3}`）：下拉、子导航。
- **Surface 4**（`{colors.surface-4}`）：嵌套面板、深层抽屉。
- **Hairline**（`{colors.hairline}`）：1px 卡片边、分隔线。
- **Hairline Strong**（`{colors.hairline-strong}`）：focus 描边、被强调分隔。

### 文字
- **Ink**（`{colors.ink}`）：标题、强调正文。
- **Ink Muted**（`{colors.ink-muted}`）：次级正文、报告元信息。
- **Ink Subtle**（`{colors.ink-subtle}`）：底部信息、占位提示、未选中标签。
- **Ink Tertiary**（`{colors.ink-tertiary}`）：脚注、禁用态。

### 风险（语义双通道）
- **Risk High**（`{colors.risk-high}`）：Integrity Guard 拦截、严重夸大、关键缺口。**必须配“高风险”文字标签。**
- **Risk Medium**（`{colors.risk-medium}`）：中等缺口、需关注、待人工确认。**必须配“需关注”文字标签。**
- **Risk Low**（`{colors.risk-low}`）：证据充分、通过、可直接采纳。**必须配“通过”文字标签。**
- 任何只有色相、没有文字的风险表达都视为违反 CLAUDE.md 前端约束。

### Agent Trace
- **Info Trace**（`{colors.info-trace}`）：节点进行中、节点重试。中性蓝，与 risk 不混色。
- 节点失败仍走 `risk-high`，因为节点失败本身是需要用户感知的风险。

## 排印

### 字族
- **Inter**：默认西文 sans，承载 display 到 caption 的全部层级。
- **系统中文**：`PingFang SC, Microsoft YaHei, Source Han Sans CN, Noto Sans CJK SC, sans-serif` 作为中文降级栈。
- **JetBrains Mono**：JD 原文片段、Agent trace 节点 ID、版本号、JSON 调试视图。

### 层级

| Token | 字号 | 字重 | 行高 | 字距 | 用途 |
|---|---|---|---|---|---|
| `{typography.display-xl}` | 64px | 600 | 1.05 | -2.4px | 工作台 / 报告页最大标题 |
| `{typography.display-lg}` | 44px | 600 | 1.10 | -1.4px | 报告总分数字 |
| `{typography.display-md}` | 32px | 600 | 1.15 | -0.8px | 章节标题 |
| `{typography.headline}` | 24px | 600 | 1.20 | -0.4px | 卡片主标题、Next Best Action 文案 |
| `{typography.card-title}` | 20px | 500 | 1.25 | -0.2px | 评分维度标题 |
| `{typography.subhead}` | 18px | 400 | 1.40 | -0.1px | 引导段、报告导言 |
| `{typography.body-lg}` | 16px | 400 | 1.55 | -0.05px | 段落正文 |
| `{typography.body}` | 14px | 400 | 1.55 | 0 | 默认正文、表格 |
| `{typography.body-sm}` | 13px | 400 | 1.50 | 0 | 证据卡正文、辅助说明 |
| `{typography.caption}` | 12px | 400 | 1.40 | 0 | 风险标签、状态徽章 |
| `{typography.button}` | 14px | 500 | 1.20 | 0 | 所有按钮 |
| `{typography.eyebrow}` | 12px | 500 | 1.30 | 0.4px | 章节眉头（正字距） |
| `{typography.mono}` | 13px | 400 | 1.50 | 0 | JD 片段、Trace ID |

### 原则
- display 用负字距（-2.4 px 至 -0.4 px）保留 Linear 的“克制精度”观感；body 维持中性 0 字距，提升中文混排可读性。
- display 与 body 同族（Inter），声音连续；只有 mono 切换到 JetBrains Mono，且仅在代码、JD 引文、ID 中出现。
- 报告页避免使用 display-xl，留给工作台首屏；report 页最大字号是 display-lg 的总分数字。
- 中文段落最小字号不低于 13 px；JD/简历原文展示区强制 16 px，并保证 1.55 行高。

## 布局

### 间距
- 基础单位 4 px。
- 工作台卡片内边距 `{spacing.lg}` 24 px；评分维度卡 `{spacing.md}` 16 px；Next Best Action callout `{spacing.lg}` 24 px 上下、`{spacing.xl}` 28 px 左右。
- 卡片之间 `{spacing.lg}` 24 px；区块之间 `{spacing.section}` 64 px（小于 Linear 的 96 px，因为工作台天然密集）。

### 容器与栅格
- 最大内容宽度 1200 px。
- 工作台首屏：左侧 280 px 导航栏（岗位/简历版本切换），右侧主区域。
- 报告页：单列布局，最大 880 px，以保证证据链文本可读。
- 评分维度卡 desktop 3-up，tablet 2-up，mobile 1-up。

### 留白哲学
- 暗色 canvas 本身就是留白，不靠白色 gap 划分章节。
- 章节用“升级到 surface-1”而不是“留出空白”来分隔。
- 报告页内部允许信息密集，但每个卡片必须以结构化字段呈现，禁止把 LLM 输出的长段落直接塞进卡片。

## 深度与层级

| 层级 | 处理 | 用途 |
|---|---|---|
| 0（平面） | 无边、无阴影 | 默认正文、Trace 行 |
| 1（surface-1 抬升） | `{colors.surface-1}` 背景 + 1px `{colors.hairline}` | 默认卡片、评分总览卡 |
| 2（surface-2 抬升） | `{colors.surface-2}` 背景 + 1px `{colors.hairline}` | 评分维度卡、证据链卡、hover 态 |
| 3（surface-3 抬升） | `{colors.surface-3}` 背景 | 下拉、子导航、抽屉头部 |
| 4（focus ring） | 2px `{colors.primary-focus}` 50% 透明 | 输入框、按钮 focus |

工作台**禁止**使用阴影替代 surface 抬升。所有层级感由表面阶梯 + hairline 表达。

## 形状

| Token | 值 | 用途 |
|---|---|---|
| `{rounded.xs}` | 4px | 状态徽章、Trace 行 |
| `{rounded.sm}` | 6px | 标签 |
| `{rounded.md}` | 8px | 所有按钮、输入框 |
| `{rounded.lg}` | 12px | 大多数卡片、Next Best Action callout |
| `{rounded.xl}` | 16px | 评分总览卡 |
| `{rounded.pill}` | 9999px | 风险标签、状态徽章、tab 切换 |
| `{rounded.full}` | 9999px | 头像 |

**禁止**把任何按钮做成 pill。pill 仅用于标签和状态。

## 组件要点

### Next Best Action callout
- 工作台首屏顶部、报告页报告头部，必有一个 `next-best-action-callout`。
- 左侧 4 px lavender 色条 `{colors.primary}` + 文案 + 1 个主行动按钮。
- 文案一行，最多 24 个汉字；超出强制截断或换为多行结构。
- 状态包括：行动可执行、行动等待依赖（被禁用按钮 + 文字解释为什么等待）、无可执行行动（用 ink-subtle 文案显示“当前没有推荐行动”）。

### 评分总览卡 + 评分维度卡
- 总览卡顶部是大号总分（`display-lg`），右侧是“最高/最低维度”概要。
- 维度卡每个一格，包含：维度名（card-title）、分数、`risk-pill-*`、阈值条、原因摘要（body-sm）。
- 维度卡必须可点击展开为该维度的证据链卡列表。

### 证据链卡
- 必须同时展示 JD 证据原文片段（mono）+ 简历证据原文片段（mono）+ 关联评分维度（status-badge）。
- 如果某一侧没有证据，明确文字标注“未在简历中找到对应证据”或“未在 JD 中找到对应要求”，**不允许**省略。
- JD/简历原文展示长度上限 200 字符，超出折叠，展开按钮在卡内底部。

### 简历建议卡
- 强制字段：原始依据 / 优化表达 / 关联 JD 要求 / 使用的简历证据 / 风险等级。
- 缺失任何一个字段，UI 层应显示占位错误状态而不是隐藏字段，便于发现后端 schema 退化。
- 风险等级以 `risk-pill-*` 呈现，置于卡片右上角。

### Integrity Guard 拦截
- 出现拦截时，在简历建议列表上方显示一条 `integrity-guard-banner`，列明被拦截的条目数与原因摘要。
- 被拦截的简历建议卡仍然渲染，但卡片整体置灰（surface-1 → surface-2，文字降级到 ink-muted），并在右上角显示 `risk-pill-high` 与“高风险”标签。

### Agent Trace
- 时间线呈现，每行一个 `agent-trace-row`。
- 每行展示：节点名（card-title 缩略版）、状态（info-trace / risk-high）、耗时、摘要（body-sm，**已脱敏**）。
- **禁止**在 UI 层渲染节点的原始输入/输出原文。如果用户点击展开，展开层只能展示：脱敏摘要、长度统计、关键字段名称、错误信息（如有）。
- 服务端可保存原始快照用于本地调试，但不得通过 API 暴露给前端。

## Do / Don't

### Do
- 把 lavender 留给 Next Best Action 与主行动按钮。
- 用 surface 阶梯而不是阴影划分层级。
- 风险信息永远色 + 文字双通道。
- 报告页用结构化字段而不是大段 LLM 文本。
- 工作台首屏直接呈现“目标岗位 + 简历版本 + Next Best Action”三件套。
- Agent trace 强制脱敏摘要。
- display 用负字距，body 用 0 字距以兼容中文。

### Don't
- 不要做亮色主题（Phase 1 明确不实现）。
- 不要把 lavender 当背景或第二种强调色用。
- 不要在工作台首屏放营销文案、宣传图、产品截图轮播。
- 不要在风险表达中只用红色或只用文字其中一种。
- 不要在 Agent trace UI 层渲染 JD/简历原文。
- 不要把 LLM 输出的长段落直接堆进卡片，必须先结构化。
- 不要给按钮做成 pill。
- 不要在评分维度卡上加阴影或亮色边框来“强调高分”，分数差异由数字与 risk-pill 表达。
- 不要为了视觉一致而隐藏证据链字段缺失，那是 schema 退化的信号。

## 响应式

| 断点 | 宽度 | 关键变化 |
|---|---|---|
| Desktop-XL | 1440px | 默认布局 |
| Desktop | 1280px | 维度卡 3-up 维持 |
| Tablet | 1024px | 维度卡 3-up → 2-up；左侧导航折叠 |
| Mobile-Lg | 768px | 单列；导航变汉堡；display-xl 由 64px 缩到 36px |
| Mobile | 480px | 工作台与所有核心页面单列布局；导航折叠为顶部 tab；display-xl 由 64px 缩到 28px；Agent trace 时间线默认收起 |

### 触摸目标
- 所有按钮在 touch 视口下最小 44 px 高。
- `risk-pill-*` 触摸版高度 ≥ 32 px。
- 输入框最小 44 px 高。

### 收起策略
- 工作台左侧导航 1024 px 以下变成顶部 tab。
- Agent trace 时间线 768 px 以下变成可折叠面板，默认收起。
- 证据链卡的 JD/简历原文 768 px 以下默认折叠到 80 字符，点击展开。

## Agent Prompt 速查

```yaml
canvas: "#010102"      # 工作台底色，全屏
primary: "#5e6ad2"     # 仅用于 Next Best Action / 主按钮 / focus
surface-1: "#0f1011"   # 默认卡片
surface-2: "#141516"   # 评分维度卡 / hover 卡
ink: "#f7f8f8"         # 主文字
risk-high: "#e5484d"   # 高风险，必须配文字"高风险"
risk-medium: "#f5a524" # 中风险，必须配文字"需关注"
risk-low: "#27a644"    # 低风险，必须配文字"通过"

button-rounded: 8px
card-rounded: 12px
report-card-rounded: 16px
font: Inter / PingFang SC / JetBrains Mono
```

可直接给 Agent 的 Prompt 模板：

> 使用 CareerFit Agent 设计系统：暗色 canvas `#010102`，唯一 lavender `#5e6ad2` 仅用于 Next Best Action 和主按钮，风险信息必须色 + 文字双通道（risk-high `#e5484d` + “高风险”标签 / risk-medium `#f5a524` + “需关注”标签 / risk-low `#27a644` + “通过”标签）。卡片用 4 级 surface 阶梯 + 1 px hairline，禁止阴影。工作台首屏顶部固定 `next-best-action-callout`。Agent trace UI 只渲染脱敏摘要，不渲染 JD/简历原文。

## 已知缺口

- 亮色主题：Phase 1 不实现；后续若做用户偏好切换，需重新派生一套 light 色阶。
- 自有字族：Linear 自有 sans 不公开，Inter 是稳定可获取的近似替代；如未来引入品牌字族，统一替换 `fontFamily`。
- 五档断点视觉走查：CLAUDE.md 要求 480 / 768 / 1024 / 1280 / 1440 全部覆盖，Phase 1 已写入断点表与收起策略；T7 UX 抛光门必须在所有断点跑过手动视觉走查并补 e2e 用例。
- DESIGN.md lint：`npx @google/design.md lint docs/DESIGN.md` 在本仓库尚未集成到 CI；变更后建议手动运行一次。
- 与 frontend-design skill 的衔接：本文件提供 token 与组件契约；具体 React/CSS 实现走 `frontend-design:frontend-design` skill 生成，本文件不规定实现技术。

## 迭代指南

1. 修改前，先确认变更点对应的 `components:` token 名称。
2. 引入新组件时，先在 frontmatter 注册 token，再在“组件要点”节补充语义说明。
3. 颜色调整必须保留 risk 与 primary 的语义独立性，不得让风险色与品牌色互相替代。
4. 修改后运行 `npx @google/design.md lint docs/DESIGN.md`。
5. 任何与 CLAUDE.md 已有约束冲突的视觉决策，必须先更新 CLAUDE.md 或在本文件“已知缺口”中记录原因。
6. 不允许新增只有英文说明的设计章节；如果引用上游 Linear 原文，必须翻译并加注。
