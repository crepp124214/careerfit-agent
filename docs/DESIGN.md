# CareerFit Agent 设计文档

## 产品定位

CareerFit Agent 是一个面向计算机专业应届生的个人求职成长工作台。通过目标岗位分析、简历匹配评分、证据链报告、能力缺口识别、学习任务闭环，帮助求职者诚实优化简历并形成持续成长闭环。

---

## 目标用户

正在申请以下岗位的计算机专业学生和应届毕业生：
- 软件开发
- 后端/前端/全栈
- AI 应用开发
- 大模型应用开发

---

## 业务闭环

```
保存目标岗位 → 上传简历版本 → 执行匹配分析 → 查看评分和证据链
     ↓
识别能力缺口 → 生成简历建议 → 生成面试题和学习路径 → 完成学习任务
     ↓
创建新简历版本 → 再次匹配分析 → 对比分数和缺口趋势
```

---

## 功能模块

### 已完成功能

| 模块 | 功能 | 状态 |
|------|------|------|
| 目标岗位库 | 创建、管理岗位JD | ✅ |
| 简历版本库 | 创建、管理简历版本，支持版本对比 | ✅ |
| 匹配分析 | 执行JD-简历匹配分析 | ✅ |
| 可解释报告 | 总分、分项评分、证据链、缺口分析 | ✅ |
| Integrity Guard | 检测无证据指标和夸大表达 | ✅ |
| 学习任务闭环 | 从报告生成学习任务，状态跟踪 | ✅ |
| 历史趋势 | 历史分数趋势、缺口数量变化 | ✅ |
| 版本对比 | 简历版本行级diff | ✅ |
| 知识库模式 | RAG技能知识库检索增强 | ✅ |
| 大模型代理 | 支持OpenAI-compatible API | ✅ |
| 面试训练 | 面试题生成、练习会话 | ✅ |
| Agent轨迹 | 实时进度展示、执行详情 | ✅ |

---

## 技术架构

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.5 | 框架 |
| TypeScript | 5.x | 类型安全 |
| Vite | 6.x | 构建工具 |
| Pinia | 3.x | 状态管理 |
| Vue Router | 4.x | 路由 |

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| FastAPI | 0.111+ | Web框架 |
| Pydantic | 2.7+ | 数据验证 |
| SQLAlchemy | 2.0+ | ORM |
| PostgreSQL | 16 | 主数据库 |
| SQLite | 3 | 开发数据库 |
| pgvector | 0.2+ | 向量存储 |

### AI

| 技术 | 用途 |
|------|------|
| LangGraph | Agent工作流 |
| Sentence Transformers | 文本嵌入 |
| OpenAI-compatible API | 大模型代理 |

---

## Agent 工作流

### 执行顺序

```
JD Parser → Resume Parser → RAG Retriever → Match Scorer
     ↓
Gap Analyzer → Resume Optimizer → Interview Coach
     ↓
Learning Planner → Next Best Action
```

### Agent 职责

| Agent | 执行模式 | 职责 |
|-------|---------|------|
| JD Parser | 确定性 | 解析岗位描述，提取结构化信息 |
| Resume Parser | 确定性 | 解析简历，提取技能、项目、经历 |
| RAG Retriever | 确定性 | 从知识库检索相关技能标准 |
| Match Scorer | 确定性 | 计算匹配分数（规则引擎） |
| Gap Analyzer | 确定性 | 识别能力缺口 |
| Resume Optimizer | LLM | 生成简历优化建议 |
| Interview Coach | LLM | 生成面试题 |
| Learning Planner | LLM | 生成学习计划 |
| Next Best Action | LLM | 推荐下一步行动 |

### LLM节点特性

- 支持并发执行（可配置）
- 自动回退到规则引擎
- 超时重试机制
- 结果缓存

---

## 数据模型

### 核心实体

| 实体 | 说明 |
|------|------|
| JobDescription | 目标岗位 |
| ResumeVersion | 简历版本 |
| AnalysisTask | 分析任务 |
| AnalysisReport | 匹配报告 |
| AgentRun | Agent运行轨迹 |
| LearningTask | 学习任务 |
| KnowledgeDocument | 知识库文档 |
| InterviewSession | 面试会话 |
| InterviewQuestion | 面试问题 |

### 实体关系

```
JobDescription ──┐
                 ├── AnalysisTask ── AnalysisReport
ResumeVersion ───┘        │
                          ├── AgentRun (多个)
                          ├── LearningTask (多个)
                          └── InterviewSession ── InterviewQuestion (多个)
```

---

## API 设计

### 岗位管理

```
POST   /api/jobs           创建岗位
GET    /api/jobs           获取岗位列表
GET    /api/jobs/{id}      获取岗位详情
DELETE /api/jobs/{id}      删除岗位
```

### 简历管理

```
POST   /api/resumes           创建简历
GET    /api/resumes           获取简历列表
GET    /api/resumes/{id}      获取简历详情
DELETE /api/resumes/{id}      删除简历
GET    /api/resumes/compare   版本对比
```

### 分析任务

```
POST   /api/analysis            创建分析任务
GET    /api/analysis/{id}       获取任务状态
GET    /api/reports/{task_id}   获取报告
GET    /api/reports/history     历史趋势
GET    /api/agent-runs/{task_id} Agent轨迹
```

### 学习任务

```
GET    /api/learning/tasks            获取任务列表
POST   /api/learning/tasks/generate   生成任务
PATCH  /api/learning/tasks/{id}       更新状态
```

### 知识库

```
POST   /api/knowledge/import   导入文档
POST   /api/knowledge/search   搜索文档
GET    /api/knowledge/stats    获取统计
```

### 面试训练

```
POST   /api/interview/sessions           创建会话
GET    /api/interview/sessions/{id}      获取会话
PATCH  /api/interview/questions/{id}     更新问题状态
```

### 系统状态

```
GET    /health              健康检查
GET    /api/capabilities    能力状态
GET    /api/llm/metrics     LLM指标
GET    /api/llm/cache       缓存统计
```

---

## 安全设计

### API Key 安全

- API Key 仅存储在后端环境变量
- 前端无法读取、保存或展示 Key
- 日志中自动脱敏处理

### 数据脱敏

- 简历原文和 JD 原文在 API 响应中为 `[redacted]`
- Agent trace 不保存敏感信息
- 证据数据标记为 `[redacted evidence]`

### 本地存储

- 用户偏好使用 `careerfit:pref:*` 命名空间
- PII 数据白名单控制
- 不存储敏感文本

---

## 性能优化

### LLM 性能

- **并发执行**: 4个LLM节点可并发执行
- **结果缓存**: 基于内容哈希的LRU缓存
- **超时控制**: 默认120秒，可配置
- **自动回退**: LLM失败时回退到规则引擎

### 数据库

- SQLite 用于开发环境
- PostgreSQL + pgvector 用于生产环境
- 自动创建表结构

---

## 部署方案

### 本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev

# 导入知识库
cd backend
python import_seeds.py
```

### 云平台部署

详见 [DEPLOY.md](../DEPLOY.md)

---

## 项目边界

### 范围内

- 目标岗位库和简历版本库
- JD-简历匹配分析
- 可解释评分和证据链
- 能力缺口分析
- Integrity Guard
- 简历优化建议
- 面试题和学习路径
- 学习任务跟踪
- 历史趋势和版本对比
- 知识库 RAG
- 大模型代理
- 面试训练

### 范围外

- 登录、注册、多租户
- HR 候选人筛选
- 导师/管理员看板
- 支付、通知、日历
- 自动改写简历
- 编造虚假内容

---

## 版本历史

| Phase | 功能 | 状态 |
|-------|------|------|
| Phase 1 | 可信主路径、完整前端 | ✅ 完成 |
| Phase 2A | 学习任务闭环 | ✅ 完成 |
| Phase 2B | 历史趋势、版本对比 | ✅ 完成 |
| Phase 2C | 多模型后端代理 | ✅ 完成 |
| Phase 2D | 知识库模式（RAG） | ✅ 完成 |
| Phase 2E | 面试训练 | ✅ 完成 |
| Phase 2F | 报告导出 | 📝 规划中 |
| Phase 2G | Agent可信度增强 | 📝 规划中 |
