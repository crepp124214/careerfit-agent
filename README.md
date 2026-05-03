# CareerFit Agent

计算机应届生个人求职成长工作台。通过目标岗位分析、简历匹配评分、证据链报告和能力缺口识别，帮助求职者诚实优化简历、制定学习计划。

## 项目边界

- **不做**登录、注册、多租户账号系统
- **不做** HR 候选人筛选与排序流程
- **不做**导师、就业老师或管理员看板
- **不做**支付、通知、日历或企业协作功能

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3.5 + TypeScript + Vite + Pinia + Vue Router + VueUse |
| 后端 | FastAPI + Pydantic + SQLAlchemy + PostgreSQL + pgvector |
| 测试 | Vitest（前端）、pytest（后端） |
| 容器 | Docker Compose（multi-stage builds） |

## 大模型后端代理

默认不启用大模型。启用后，API Key 只放在后端环境变量里，前端不会读取、保存或展示 Key。LLM 只用于简历建议、面试题、学习计划和 Next Best Action，最终数字评分仍由后端确定性规则计算。

通用配置：

```env
CAREERFIT_LLM_ENABLED=true
CAREERFIT_LLM_PROVIDER=openai_compatible
CAREERFIT_LLM_BASE_URL=https://api.example.com/v1
CAREERFIT_LLM_API_KEY=你的_key
CAREERFIT_LLM_MODEL=你的模型名
CAREERFIT_LLM_API_STYLE=chat_completions
```

常见 OpenAI-compatible 示例：

```env
# OpenAI Chat Completions
CAREERFIT_LLM_BASE_URL=https://api.openai.com/v1
CAREERFIT_LLM_MODEL=gpt-5.2
CAREERFIT_LLM_API_STYLE=chat_completions

# OpenAI Responses API
CAREERFIT_LLM_BASE_URL=https://api.openai.com/v1
CAREERFIT_LLM_MODEL=gpt-5.2
CAREERFIT_LLM_API_STYLE=responses

# DeepSeek
CAREERFIT_LLM_BASE_URL=https://api.deepseek.com/v1
CAREERFIT_LLM_MODEL=deepseek-chat
CAREERFIT_LLM_API_STYLE=chat_completions

# Kimi / Moonshot
CAREERFIT_LLM_BASE_URL=https://api.moonshot.cn/v1
CAREERFIT_LLM_MODEL=moonshot-v1-8k
CAREERFIT_LLM_API_STYLE=chat_completions
```

其他国内模型服务如果提供 OpenAI-compatible `/chat/completions`，通常只需要替换 `CAREERFIT_LLM_BASE_URL` 和 `CAREERFIT_LLM_MODEL`。不要把真实 `.env`、API Key 或模型 Key 提交到仓库。

## 运行方式

### 方式一：仅前端（无需后端）

用于查看完整网站结构。所有后端能力以"功能未上线"提示告知用户。

```bash
docker compose -f docker-compose.frontend-only.yml up --build
```

前端地址：http://localhost:5173

### 方式二：全栈（推荐）

可信主路径端到端可用，包括岗位创建、简历匹配分析、确定性评分、证据链报告、Integrity Guard 和 Agent 运行轨迹。

```bash
docker compose up --build
```

| 服务 | 地址 |
|---|---|
| 前端 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

## Phase 1 验收门

### 前端 Phase 1.A

- 13 条路由全部可达（工作台、报告、岗位管理、简历管理、Agent trace、历史趋势、版本对比、学习任务、设置等）
- 每个页面支持空 / 加载 / 错误 / 部分数据四态
- 后端缺口用 `BackendNotReadyNotice` 告知，禁止 mock 数据
- 风险信息色 + 文字双通道
- `Next Best Action` 在工作台首屏与报告头部显眼位
- 完整响应式（1440 / 1280 / 1024 / 768 / 480）
- 完整无障碍（键盘可达、ARIA、WCAG AA）
- 关键交互有动效过渡，尊重 `prefers-reduced-motion`
- 本地偏好通过 `localStorage` 持久化（`careerfit:pref:*` 命名空间，PII 白名单）

### 后端 Phase 1.B

- 可信主路径：创建岗位 → 创建简历 → 执行分析 → 确定性评分 → 证据链报告 → Integrity Guard → Agent 运行轨迹 → Next Best Action
- 评分确定性：维度 clamp 0–100，LLM 不直接决定分数
- Integrity Guard 阻止无证据指标与夸大职责
- Agent Trace 脱敏：原始 JD/简历文本在 API 响应中为 `[redacted]`
- `/api/capabilities` 返回当前已上线能力

## 项目结构

```text
├── frontend/          # Vue 3 前端
│   ├── src/
│   │   ├── api/       # API 客户端
│   │   ├── components/
│   │   ├── composables/
│   │   ├── stores/    # Pinia stores
│   │   └── views/     # 页面视图
│   ├── tests/
│   └── Dockerfile
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── api/routes/
│   │   ├── models/
│   │   ├── services/
│   │   └── main.py
│   ├── tests/
│   └── Dockerfile
├── docker-compose.yml              # 全栈
├── docker-compose.frontend-only.yml # 仅前端
└── docs/                           # 设计与计划文档
```

## 开发

```bash
# 前端开发
cd frontend
npm install
npm run dev

# 后端开发
cd backend
pip install -e .
uvicorn app.main:app --reload

# 前端测试
cd frontend && npm test

# 后端测试
cd backend && pytest -q

# 类型检查
cd frontend && npm run typecheck
```
