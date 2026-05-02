# CareerFit Agent 测试计划

日期：2026-05-02

## 受影响页面和路由

- 工作台
- 目标岗位库
- 简历版本库
- 匹配分析页
- 分析报告页
- 证据解释页
- 面试训练页
- 学习路径页
- 成长趋势页
- Agent 运行轨迹页

## 后端 API 覆盖

| API | 必测场景 |
|---|---|
| `POST /api/jobs` | 有效 JD、空 JD、格式不完整 JD、解析失败 |
| `GET /api/jobs` | 空列表、有数据列表 |
| `GET /api/jobs/{id}` | 存在、不存在 |
| `POST /api/resumes` | 有效文本简历、空简历、低置信度解析 |
| `GET /api/resumes/compare` | 新增段落、删除段落、修改段落 |
| `POST /api/analysis` | 有效岗位 + 简历、岗位不存在、简历不存在 |
| `GET /api/analysis/{task_id}` | pending、running、success、failed |
| `GET /api/reports/{task_id}` | 完整报告、弱证据报告、不存在 |
| `GET /api/agent-runs/{task_id}` | 成功节点、失败节点、脱敏摘要 |
| `PATCH /api/learning/tasks/{id}` | `not_started -> doing`、`doing -> done`、非法状态流转 |
| `GET /api/knowledge/search` | 命中预期文档、无命中、非法查询 |

## 核心单元测试

- 评分公式把所有维度限制在 0-100。
- 真实性风险扣分不能让最终分数变成负数。
- 能力层级映射返回预期数值。
- 证据链校验会拒绝没有 JD 证据的评分项。
- 证据链校验会拒绝没有简历证据的评分项。
- Integrity Guard 会阻止无证据指标。
- Integrity Guard 会阻止无证据领导力描述。
- Integrity Guard 允许安全改写。
- 简历版本比较能识别新增、删除和修改的 bullet。

## LangGraph 与 Agent 测试

- JD Parser Agent 返回符合 schema 的输出。
- Resume Parser Agent 返回符合 schema 的输出。
- RAG Retriever Agent 返回按类型分组的文档。
- Match Scoring Agent 不使用 LLM 生成最终数字分数。
- Gap Analysis Agent 输出 `missing_skill`、`weak_evidence`、`expression_gap`。
- Integrity Guard Agent 在 Resume Optimizer 最终输出前运行。
- Report Composer Agent 为每个评分项提供证据引用。
- 工作流为每个节点记录 `agent_runs`。
- 节点重试后仍失败时，工作流把任务标记为 failed。

## RAG 评估

种子文档至少覆盖：

- 大模型应用开发工程师。
- 后端开发工程师。
- 前端/全栈开发工程师。

必须检查：

- 查询 `LangGraph Agent 编排` 能召回 LangGraph 技能标准。
- 查询 `pgvector 索引` 能召回向量数据库标准。
- 查询 `Vue3 项目经验` 能召回前端/全栈标准。
- 查询没有匹配技能时，返回空结果或低置信度结果，而不是编造来源。

## LLM 评估

至少使用：

- 5 份样例 JD。
- 5 份样例简历。
- 5 条不安全简历优化样例。

评估标准：

- Parser 能抽取必备技能，并达到可接受召回率。
- Parser 保留证据片段。
- Integrity Guard 阻止编造事实。
- Report Composer 不生成无证据结论。
- 面试题在可行时引用真实简历项目。

## 前端测试

- 工作台空状态。
- 工作台展示最新报告和 Next Best Action。
- 创建岗位的加载和错误状态。
- 创建简历的加载和错误状态。
- 分析时间线运行中状态。
- 分析时间线失败节点状态。
- 报告成功状态。
- 报告弱证据状态。
- 证据详情展开。
- 学习任务状态更新。
- Agent trace 脱敏。
- 移动端报告堆叠布局。
- 主要操作支持键盘导航。

## Docker 冒烟测试

运行：

```text
docker compose up --build
```

验证：

- PostgreSQL 启动，并启用 pgvector 扩展。
- 后端健康检查通过。
- 前端能打开。
- 后端能连接数据库。
- 初始迁移执行成功。
- 种子知识库导入成功。

## 关键路径

1. 创建目标岗位。
2. 创建简历版本。
3. 执行分析。
4. 查看报告。
5. 确认每个评分项都有证据。
6. 查看真实性风险。
7. 标记学习任务完成。
8. 创建下一版简历。
9. 再次分析。
10. 查看分数趋势。
