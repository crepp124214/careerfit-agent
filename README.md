# CareerFit Agent

<div align="center">

**计算机应届生个人求职成长工作台**

[![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?logo=vue.js)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## 📖 目录

- [项目概述](#项目概述)
- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [API 参考](#api-参考)
- [项目结构](#项目结构)
- [开发指南](#开发指南)
- [部署指南](#部署指南)
- [贡献指南](#贡献指南)
- [许可证](#许可证)
- [支持与联系](#支持与联系)

---

## 项目概述

CareerFit Agent 是一个面向计算机专业应届生的个人求职成长工作台。通过目标岗位分析、简历匹配评分、证据链报告、能力缺口识别、学习任务闭环，帮助求职者诚实优化简历并形成持续成长闭环。

### 核心价值

- **可解释评分** - 评分由确定性规则计算，每个分数都能追溯到具体证据
- **诚实优化** - Integrity Guard 检测无证据指标和夸大表达，防止简历造假
- **持续成长** - 学习任务闭环帮助补齐能力缺口，形成正向循环
- **知识增强** - RAG 技能知识库提供行业标准参考

### 目标用户

- 计算机专业应届毕业生
- 正在求职的软件开发工程师
- 后端/前端/全栈开发求职者
- AI/大模型应用开发求职者

---

## 功能特性

### ✅ 已完成功能

| 功能 | 描述 |
|------|------|
| 🎯 **目标岗位库** | 创建、管理岗位 JD，自动解析结构化信息 |
| 📄 **简历版本库** | 维护多个简历版本，支持版本对比 |
| 📊 **匹配分析** | 执行 JD-简历匹配分析，生成可解释报告 |
| 🔍 **证据链报告** | 每个评分项可追溯到 JD 要求、简历证据、知识库标准 |
| 🛡️ **Integrity Guard** | 检测无证据指标和夸大表达，阻止简历造假 |
| 📚 **学习任务闭环** | 从报告生成学习任务，状态跟踪 |
| 📈 **历史趋势** | 历史分数趋势图、缺口数量变化 |
| 🔄 **版本对比** | 两个简历版本的行级 diff |
| 🧠 **知识库模式** | 基于 RAG 的技能知识库检索增强 |
| 🤖 **大模型代理** | 支持 OpenAI-compatible API，多模型支持 |
| 💬 **面试训练** | 面试题生成、练习会话 |
| 📝 **Agent 轨迹** | 实时进度展示、执行详情 |
| ⚡ **LangGraph 集成** | 基于 LangGraph 的 Agent 工作流编排 |
| 📦 **分析缓存** | 加速重复分析任务 |

### 🎯 业务闭环

```
保存目标岗位 → 上传简历版本 → 执行匹配分析 → 查看评分和证据链
     ↓
识别能力缺口 → 生成简历建议 → 生成面试题和学习路径 → 完成学习任务
     ↓
创建新简历版本 → 再次匹配分析 → 对比分数和缺口趋势
```

---

## 技术栈

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| [Vue](https://vuejs.org/) | 3.5 | 渐进式 JavaScript 框架 |
| [TypeScript](https://www.typescriptlang.org/) | 5.x | 类型安全 |
| [Vite](https://vitejs.dev/) | 6.x | 下一代前端构建工具 |
| [Pinia](https://pinia.vuejs.org/) | 3.x | Vue 状态管理 |
| [Vue Router](https://router.vuejs.org/) | 4.x | Vue.js 官方路由 |
| [Reka UI](https://reka-ui.com/) | 2.x | 无样式 UI 组件库 |
| [ECharts](https://echarts.apache.org/) | 5.x | 数据可视化图表库 |

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| [FastAPI](https://fastapi.tiangolo.com/) | 0.111+ | 现代 Python Web 框架 |
| [Pydantic](https://docs.pydantic.dev/) | 2.7+ | 数据验证和设置管理 |
| [SQLAlchemy](https://www.sqlalchemy.org/) | 2.0+ | Python SQL 工具包和 ORM |
| [PostgreSQL](https://www.postgresql.org/) | 16 | 对象关系数据库 |
| [pgvector](https://github.com/pgvector/pgvector) | 0.2+ | PostgreSQL 向量扩展 |

### AI

| 技术 | 用途 |
|------|------|
| [LangGraph](https://langchain-ai.github.io/langgraph/) | Agent 工作流编排 |
| [Sentence Transformers](https://www.sbert.net/) | 文本嵌入生成 |
| OpenAI-compatible API | 大模型代理 |

---

## 快速开始

### 前提条件

- **Node.js** 18+ 和 npm
- **Python** 3.12+
- **Git**

### 安装步骤

#### 1. 克隆仓库

```bash
git clone https://github.com/你的用户名/careerfit-agent.git
cd careerfit-agent
```

#### 2. 安装后端依赖

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 3. 安装前端依赖

```bash
cd ../frontend
npm install
```

#### 4. 配置环境变量

```bash
cd ..
cp .env.example .env
```

编辑 `.env` 文件，配置必要的环境变量。

#### 5. 启动服务

**启动后端：**

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**启动前端（新终端）：**

```bash
cd frontend
npm run dev
```

#### 6. 导入知识库数据

```bash
cd backend
python import_seeds.py
```

### 访问应用

| 服务 | 地址 |
|------|------|
| 前端应用 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |
| ReDoc 文档 | http://localhost:8000/redoc |

---

## 配置说明

### 环境变量

创建 `.env` 文件并配置以下变量：

```env
# 基础配置
CAREERFIT_ENVIRONMENT=development

# 数据库连接
# 本地开发 (SQLite):
CAREERFIT_DATABASE_URL=sqlite+pysqlite:///./careerfit_dev.db
# 生产环境 (PostgreSQL):
# CAREERFIT_DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname

# 大模型配置 (可选)
CAREERFIT_LLM_ENABLED=false
CAREERFIT_LLM_PROVIDER=openai_compatible
CAREERFIT_LLM_BASE_URL=https://api.openai.com/v1
CAREERFIT_LLM_API_KEY=your-api-key
CAREERFIT_LLM_MODEL=gpt-4o-mini
CAREERFIT_LLM_TIMEOUT_SECONDS=120

# 前端配置
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_VARIANT=fullstack
```

### 支持的大模型服务

| 服务 | BASE_URL | MODEL |
|------|----------|-------|
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini`, `gpt-4o` |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| Kimi/Moonshot | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` |
| 其他 | OpenAI-compatible API | 根据服务商文档 |

---

## API 参考

### 岗位管理

```http
POST   /api/jobs           # 创建岗位
GET    /api/jobs           # 获取岗位列表
GET    /api/jobs/{id}      # 获取岗位详情
DELETE /api/jobs/{id}      # 删除岗位
```

### 简历管理

```http
POST   /api/resumes           # 创建简历
GET    /api/resumes           # 获取简历列表
GET    /api/resumes/{id}      # 获取简历详情
DELETE /api/resumes/{id}      # 删除简历
GET    /api/resumes/compare   # 版本对比
```

### 分析任务

```http
POST   /api/analysis            # 创建分析任务
GET    /api/analysis/{id}       # 获取任务状态
GET    /api/reports/{task_id}   # 获取报告
GET    /api/reports/history     # 历史趋势
GET    /api/agent-runs/{task_id} # Agent 轨迹
```

### 学习任务

```http
GET    /api/learning/tasks            # 获取任务列表
POST   /api/learning/tasks/generate   # 生成任务
PATCH  /api/learning/tasks/{id}       # 更新状态
```

### 知识库

```http
POST   /api/knowledge/import   # 导入文档
POST   /api/knowledge/search   # 搜索文档
GET    /api/knowledge/stats    # 获取统计
```

### 面试训练

```http
POST   /api/interview/prepare      # 生成面试题
GET    /api/interview/history     # 面试历史
GET    /api/interview/{id}        # 面试详情
```

### 系统状态

```http
GET    /health              # 健康检查
GET    /api/capabilities    # 能力状态
GET    /api/llm/metrics     # LLM 指标
GET    /api/system/stats    # 系统统计
```

完整 API 文档请访问：http://localhost:8000/docs

---

## 项目结构

```
careerfit-agent/
├── frontend/                    # Vue 3 前端
│   ├── src/
│   │   ├── api/                 # API 客户端
│   │   ├── components/          # Vue 组件
│   │   ├── composables/         # Vue 组合式函数
│   │   ├── stores/              # Pinia 状态管理
│   │   ├── views/               # 页面视图
│   │   └── main.ts              # 入口文件
│   ├── tests/                   # 前端测试
│   └── package.json             # Node 依赖
│
├── backend/                     # FastAPI 后端
│   ├── app/
│   │   ├── agents/              # Agent 工作流
│   │   │   ├── graph.py         # 工作流图定义
│   │   │   ├── nodes.py         # Agent 节点实现
│   │   │   └── state.py         # 状态定义
│   │   ├── api/routes/          # API 路由
│   │   ├── db/                  # 数据库模型
│   │   ├── llm/                 # 大模型代理
│   │   │   ├── cache.py         # 结果缓存
│   │   │   ├── client.py        # LLM 客户端
│   │   │   ├── concurrent.py    # 并发执行
│   │   │   ├── metrics.py       # 性能指标
│   │   │   ├── prompts.py       # Prompt 模板
│   │   │   └── service.py       # LLM 服务
│   │   ├── rag/                 # RAG 检索
│   │   ├── schemas/             # Pydantic 模型
│   │   ├── services/            # 业务服务
│   │   └── main.py              # 应用入口
│   ├── seeds/                   # 知识库种子数据
│   ├── tests/                   # 后端测试
│   ├── requirements.txt         # Python 依赖
│   └── import_seeds.py          # 数据导入脚本
│
├── docs/                        # 文档
│   ├── DESIGN.md                # 设计文档
│   └── INDEX.md                 # 文档索引
│
├── .env.example                 # 环境变量示例
├── README.md                    # 项目说明
└── docker-compose.yml           # Docker 配置
```

---

## 开发指南

### 开发命令

```bash
# 前端开发
cd frontend
npm run dev          # 启动开发服务器
npm run build        # 构建生产版本
npm run test         # 运行测试
npm run typecheck    # 类型检查

# 后端开发
cd backend
uvicorn app.main:app --reload  # 启动开发服务器
pytest -q                       # 运行测试
```

### 代码规范

- **前端**: ESLint + TypeScript 严格模式
- **后端**: Pydantic 数据验证，类型注解

### 分支管理

- `main` - 主分支，稳定版本
- `develop` - 开发分支
- `feature/*` - 功能分支
- `bugfix/*` - 修复分支

---

## 部署指南

### Docker 部署（推荐）

使用 Docker Compose 一键部署前后端和数据库：

```bash
# 复制环境变量配置
cp .env.docker .env

# 编辑 .env 文件，填入必要的配置（尤其是 LLM API Key）

# 启动所有服务
docker compose up --build -d

# 查看容器状态
docker compose ps

# 查看日志
docker compose logs -f backend
```

访问应用：
- 前端应用：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### Docker 环境变量

创建 `.env` 文件（参考 `.env.docker`）：

```env
# 基础配置
CAREERFIT_ENVIRONMENT=production
CAREERFIT_DATABASE_URL=postgresql+psycopg://careerfit:careerfit@postgres:5432/careerfit

# PostgreSQL 数据库
POSTGRES_DB=careerfit
POSTGRES_USER=careerfit
POSTGRES_PASSWORD=careerfit

# 大模型配置（必须填入真实 API Key）
CAREERFIT_LLM_ENABLED=true
CAREERFIT_LLM_PROVIDER=openai_compatible
CAREERFIT_LLM_BASE_URL=https://api.minimaxi.com/v1
CAREERFIT_LLM_API_KEY=YOUR_API_KEY_HERE
CAREERFIT_LLM_MODEL=MiniMax-M2.5
CAREERFIT_LLM_API_STYLE=chat_completions
CAREERFIT_LLM_TIMEOUT_SECONDS=120
```

### 手动部署

---

## 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范

- 遵循现有代码风格
- 添加必要的测试
- 更新相关文档

### 提交信息规范

使用约定式提交：

```
feat: 添加新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建/工具相关
```

---

## 许可证

本项目采用 [MIT 许可证](LICENSE)。

---

## 支持与联系

### 问题反馈

如果您遇到问题或有功能建议，请：

1. 查看 [Issues](https://github.com/你的用户名/careerfit-agent/issues) 是否已有相关问题
2. 如果没有，创建新的 Issue，详细描述问题或建议

### 文档

- [设计文档](./docs/DESIGN.md)
- [API 文档](http://localhost:8000/docs)（启动后端后访问）

### 致谢

感谢以下开源项目：

- [Vue.js](https://vuejs.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [Sentence Transformers](https://www.sbert.net/)

---

<div align="center">

**如果这个项目对您有帮助，请给一个 ⭐️ Star！**

</div>
