# CareerFit Agent 部署指南

本指南将帮助你将项目部署到云平台，实现从 GitHub 自动部署。

## 架构概览

```
GitHub 仓库
    ├── frontend/ → Vercel (免费)
    ├── backend/ → Render (免费)
    └── 数据库 → Supabase (免费)
```

## 前置条件

- GitHub 账号
- Vercel 账号 (可用 GitHub 登录)
- Render 账号 (可用 GitHub 登录)
- Supabase 账号 (可用 GitHub 登录)

***

## 第一步：创建数据库 (Supabase)

### 1.1 注册并创建项目

1. 访问 <https://supabase.com>
2. 点击 "Start your project"
3. 使用 GitHub 账号登录
4. 授权 Supabase 访问你的 GitHub
5. 创建新组织（如果还没有）：
   - 点击 "New organization"
   - 输入组织名称（如：个人项目）
   - 点击 "Create organization"

**💡 提示**：

- 一个组织可以包含多个项目
- 组织名称建议使用英文，避免特殊字符
- GitHub 授权后，Supabase 可以访问你的公开仓库信息

### 1.2 创建数据库项目

1. 在组织页面点击 "New project"
2. 填写项目信息：
   - **Name**: `careerfit`
   - **Database Password**: 设置一个强密码（请保存好！）
   - **Region**: 选择 `Northeast Asia (Tokyo)` 或最近的区域
   - **Plan**: 选择 "Free"
3. 点击 "Create new project"
4. 等待约 2 分钟，项目创建完成

**💡 密码建议**：

- 至少 16 个字符
- 包含大小写字母、数字和特殊字符
- 使用密码管理器保存（如 1Password、Bitwarden）
- 不要使用常见单词或生日等易猜信息

**💡 区域选择建议**：

- 中国大陆用户：选择 `Northeast Asia (Tokyo)` 或 `Southeast Asia (Singapore)`
- 美国用户：选择 `West US (North California)` 或 `East US (North Virginia)`
- 欧洲用户：选择 `West EU (Ireland)` 或 `West EU (Frankfurt)`
- 区域一旦选定无法更改，请谨慎选择

**⏱️ 创建时间**：

- 通常需要 2-5 分钟
- 如果超过 10 分钟仍未完成，刷新页面或联系 Supabase 支持

### 1.3 获取数据库连接字符串

1. 项目创建完成后，点击左侧菜单 "Project Settings"（齿轮图标）
2. 点击 "Database"
3. 找到 "Connection string" 部分
4. 选择 "URI" 标签
5. 复制连接字符串，格式如下：
   ```
   postgresql://postgres.[项目ID]:[密码]@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres
   ```
   **重要**：将 `postgresql://` 改为 `postgresql+psycopg://`，最终格式：
   ```
   postgresql+psycopg://postgres.[项目ID]:[密码]@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres
   ```

**💡 连接字符串说明**：

- `postgres.[项目ID]`：你的数据库用户名
- `[密码]`：你在步骤 1.2 设置的密码
- `pooler.supabase.com:6543`：连接池地址，适合 Serverless 环境
- `postgres`：数据库名称

**⚠️ 安全提示**：

- 连接字符串包含密码，请妥善保管
- 不要提交到 Git 仓库
- 不要在公开场合分享
- 如果泄露，立即在 Supabase 重置密码

### 1.4 启用 pgvector 扩展

1. 点击左侧菜单 "SQL Editor"
2. 点击 "New query"
3. 输入以下 SQL：
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
4. 点击 "Run" 执行
5. 看到成功提示即可

**💡 验证扩展**：
执行以下 SQL 验证扩展是否启用：

```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

应该看到类似结果：

```
extname | extversion
--------+------------
vector  | 0.5.0
```

**⚠️ 常见错误**：

- `permission denied`: 需要使用 postgres 用户执行
- `extension not available`: Supabase 免费版默认支持，如遇到请联系支持

### 1.5 配置数据库安全（可选但推荐）

**启用行级安全（RLS）**：

虽然本项目是单用户应用，但建议了解 RLS 概念：

```sql
-- 示例：为 future 使用启用 RLS
ALTER TABLE job_positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_tasks ENABLE ROW LEVEL SECURITY;
```

**设置连接限制**：

在 Supabase Dashboard → Settings → Database：

- Connection Pooling: 启用
- Pool Size: 15（免费版默认）
- 最大连接数: 60

### 1.6 备份配置

**自动备份**：

- 免费版：每天自动备份，保留 7 天
- 付费版：可配置备份频率和保留时间

**手动备份**：

```bash
# 使用 pg_dump 备份
pg_dump "postgresql+psycopg://连接字符串" > backup_$(date +%Y%m%d).sql
```

**恢复备份**：

```bash
psql "postgresql+psycopg://连接字符串" < backup_20240101.sql
```

***

## 第二步：部署后端 (Render)

### 2.1 注册 Render

1. 访问 <https://dashboard.render.com>
2. 点击 "Get Started"
3. 选择 "Sign up with GitHub"
4. 授权 Render 访问你的 GitHub

**💡 提示**：

- 使用 GitHub 登录可以简化仓库连接流程
- Render 免费版无需绑定信用卡
- 一个 GitHub 账号可以创建多个 Render 项目

### 2.2 创建 Web Service

1. 登录后，点击 "New +" 按钮
2. 选择 "Web Service"
3. 在 "Connect a repository" 部分：
   - 如果看不到 `careerfit-agent` 仓库，点击 "Configure account"
   - 勾选 "All repositories" 或只选择 `careerfit-agent`
   - 点击 "Install" 完成授权
4. 返回 Render，刷新页面
5. 找到 `careerfit-agent` 仓库，点击 "Connect"

**💡 GitHub 授权说明**：

- "All repositories": Render 可以访问你所有的公开和私有仓库
- "Only select repositories": 只能访问你选择的仓库（推荐）
- 授权后可以在 GitHub Settings → Applications 中管理

**⚠️ 常见问题**：

- 如果看不到仓库，检查 GitHub 仓库是否为公开
- 如果是私有仓库，需要在 GitHub 授权时选择该仓库
- 授权后需要等待 1-2 分钟同步

### 2.3 配置 Web Service

填写以下配置：

| 设置项                | 值                                                  |
| ------------------ | -------------------------------------------------- |
| **Name**           | `careerfit-backend`                                |
| **Region**         | `Oregon (US West)` 或 `Frankfurt (EU Central)`      |
| **Branch**         | `main`                                             |
| **Root Directory** | `backend`                                          |
| **Runtime**        | `Python 3`                                         |
| **Build Command**  | `pip install -r requirements.txt`                  |
| **Start Command**  | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type**  | `Free`                                             |

**💡 配置说明**：

**Name**：

- 服务名称，用于生成 URL
- 格式：`https://[name].onrender.com`
- 只能包含小写字母、数字和连字符
- 一旦创建无法更改

**Region**：

- 选择离你用户最近的区域
- Oregon: 适合北美和亚太用户
- Frankfurt: 适合欧洲用户
- Singapore: 适合东南亚用户（付费）

**Root Directory**：

- 必须设置为 `backend`
- Render 会在这个目录下执行构建命令
- 如果设置错误，会导致找不到 requirements.txt

**Build Command**：

- 安装 Python 依赖
- 免费版构建时间限制 15 分钟
- 如果超时，考虑优化依赖或升级付费版

**Start Command**：

- `$PORT` 是 Render 自动分配的端口
- 不要硬编码端口号
- `--host 0.0.0.0` 允许外部访问

**Instance Type**：

- Free: 512MB RAM, 0.1 CPU
- Starter ($7/月): 512MB RAM, 0.5 CPU
- Standard ($25/月): 2GB RAM, 1 CPU

### 2.4 添加环境变量

点击 "Advanced" 展开，然后点击 "Add Environment Variable"：

| 变量名                             | 值                          | 说明             |
| ------------------------------- | -------------------------- | -------------- |
| `CAREERFIT_ENVIRONMENT`         | `production`               | 生产环境标识         |
| `CAREERFIT_DATABASE_URL`        | `postgresql+psycopg://...` | Supabase 连接字符串 |
| `CAREERFIT_LLM_ENABLED`         | `false`                    | 暂不启用 LLM       |
| `CAREERFIT_LLM_TIMEOUT_SECONDS` | `120`                      | LLM 超时时间       |

**添加环境变量的步骤：**

1. 在 "Key" 输入框输入变量名
2. 在 "Value" 输入框输入变量值
3. 点击 "Add Environment Variable"
4. 重复以上步骤添加所有变量

**💡 环境变量最佳实践**：

- 敏感信息（如密码、API Key）使用环境变量
- 不要在代码中硬编码敏感信息
- 环境变量可以在部署后随时修改
- 修改环境变量会触发重新部署

**⚠️ 重要提示**：

- `CAREERFIT_DATABASE_URL` 必须使用 `postgresql+psycopg://` 前缀
- 密码中的特殊字符需要 URL 编码：
  - `@` → `%40`
  - `#` → `%23`
  - `:` → `%3A`
  - `/` → `%2F`

**示例**：
如果密码是 `MyP@ss#123`，编码后为 `MyP%40ss%23123`

### 2.5 创建服务

1. 检查所有配置是否正确
2. 点击 "Create Web Service"
3. 等待构建完成（约 5-10 分钟）

**⏱️ 构建阶段**：

1. **Cloning repository** (30秒 - 1分钟)
   - 从 GitHub 拉取代码
   - 检出指定分支
2. **Installing dependencies** (3-5分钟)
   - 下载并安装 Python 包
   - 这是最耗时的阶段
3. **Building application** (1-2分钟)
   - 执行构建命令
   - 编译静态文件（如果有）
4. **Deploying** (1-2分钟)
   - 启动应用
   - 健康检查

**💡 查看构建日志**：

- 点击服务页面中的 "Logs" 标签
- 实时查看构建输出
- 如果失败，日志会显示错误信息

### 2.6 查看部署状态

1. 在服务页面可以看到构建日志
2. 构建完成后，状态变为 "Live"
3. 记录后端 URL，如：`https://careerfit-backend.onrender.com`

**状态说明**：

- `Building`: 正在构建
- `Deploying`: 正在部署
- `Live`: 运行中
- `Failed`: 部署失败
- `Suspended`: 已休眠（免费版）

### 2.7 验证后端

1. 访问 `https://你的后端地址.onrender.com/health`
2. 应该看到：`{"status": "ok", "environment": "production"}`
3. 访问 `https://你的后端地址.onrender.com/docs`
4. 应该看到 FastAPI 自动生成的 API 文档

**💡 验证步骤**：

**健康检查**：

```bash
curl https://你的后端地址.onrender.com/health
```

预期响应：

```json
{
  "status": "ok",
  "environment": "production"
}
```

**API 文档**：

- 浏览器访问 `/docs` 查看 Swagger UI
- 浏览器访问 `/redoc` 查看 ReDoc
- 可以直接在文档中测试 API

**数据库连接测试**：

```bash
curl https://你的后端地址.onrender.com/api/knowledge/stats
```

预期响应：

```json
{
  "total_documents": 0,
  "by_type": {}
}
```

**⚠️ 常见错误排查**：

**错误 1: 502 Bad Gateway**

- 原因：应用启动失败
- 排查：查看 Render 日志
- 解决：检查环境变量、依赖版本

**错误 2: Application failed to respond**

- 原因：健康检查失败
- 排查：确认 `/health` 端点可访问
- 解决：检查启动命令、端口配置

**错误 3: Build failed**

- 原因：依赖安装失败
- 排查：查看构建日志
- 解决：检查 requirements.txt、Python 版本

### 2.8 配置自动部署

Render 默认启用自动部署：

- 每次 push 到 main 分支，自动触发部署
- 可以在 Settings → Build & Deploy 中配置
- 可以指定其他分支或禁用自动部署

**💡 部署策略**：

- `Auto-deploy`: 推荐用于开发环境
- `Manual deploy`: 推荐用于生产环境
- `Preview deploys`: 为每个 PR 创建预览环境

### 2.9 配置健康检查

Render 自动配置健康检查：

- 路径：`/health`
- 超时：30 秒
- 间隔：30 秒

**自定义健康检查**（可选）：

在 Render Dashboard → Settings → Health Check：

- Path: `/health`
- Timeout: 60 秒
- Interval: 30 秒

### 2.10 监控和日志

**查看实时日志**：

1. 进入服务页面
2. 点击 "Logs" 标签
3. 选择 "All" 或 "Recent"

**日志类型**：

- `Build Log`: 构建过程日志
- `Deploy Log`: 部署过程日志
- `Runtime Log`: 应用运行日志

**监控指标**：

- CPU 使用率
- 内存使用率
- 请求数量
- 响应时间

**💡 日志最佳实践**：

- 使用结构化日志（JSON）
- 记录关键操作和错误
- 避免记录敏感信息
- 定期清理旧日志

***

## 第三步：部署前端 (Vercel)

### 3.1 注册 Vercel

1. 访问 <https://vercel.com>
2. 点击 "Sign Up"
3. 选择 "Continue with GitHub"
4. 授权 Vercel 访问你的 GitHub

**💡 提示**：

- 使用 GitHub 登录可以简化仓库连接流程
- Vercel 免费版对个人项目无限制
- 一个 GitHub 账号可以创建多个 Vercel 项目

### 3.2 导入项目

1. 登录后，点击 "Add New\..." → "Project"
2. 在 "Import Git Repository" 部分：
   - 如果看不到 `careerfit-agent` 仓库，点击 "Adjust GitHub App Permissions"
   - 勾选 "All repositories" 或只选择 `careerfit-agent`
   - 点击 "Install" 完成授权
3. 返回 Vercel，刷新页面
4. 找到 `careerfit-agent` 仓库，点击 "Import"

**💡 GitHub 授权说明**：

- "All repositories": Vercel 可以访问你所有的公开和私有仓库
- "Only select repositories": 只能访问你选择的仓库（推荐）
- 授权后可以在 GitHub Settings → Applications 中管理

**⚠️ 常见问题**：

- 如果看不到仓库，检查 GitHub 仓库是否为公开
- 如果是私有仓库，需要在 GitHub 授权时选择该仓库
- 授权后需要等待 1-2 分钟同步

### 3.3 配置项目

**Configure Project 页面：**

| 设置项                  | 值                       |
| -------------------- | ----------------------- |
| **Project Name**     | `careerfit-agent`       |
| **Framework Preset** | `Vue.js`                |
| **Root Directory**   | 点击 "Edit"，输入 `frontend` |
| **Build Command**    | `npm run build`（默认）     |
| **Output Directory** | `dist`（默认）              |
| **Install Command**  | `npm install`（默认）       |

**💡 配置说明**：

**Project Name**：

- 项目名称，用于生成 URL
- 格式：`https://[name].vercel.app`
- 可以包含小写字母、数字和连字符
- 可以在部署后修改

**Framework Preset**：

- Vercel 会自动检测框架
- 如果检测错误，手动选择 `Vue.js`
- Vue.js 项目会自动配置构建设置

**Root Directory**：

- **必须**点击 "Edit" 并输入 `frontend`
- 如果不设置，Vercel 会在根目录查找 package.json
- 设置错误会导致构建失败

**Build Command**：

- 默认 `npm run build`
- Vue 项目通常不需要修改
- 如果有自定义构建脚本，可以修改

**Output Directory**：

- 默认 `dist`
- Vue 项目构建输出目录
- 通常不需要修改

**Install Command**：

- 默认 `npm install`
- 如果使用 pnpm 或 yarn，可以修改
- 例如：`pnpm install` 或 `yarn install`

### 3.4 添加环境变量

在 "Environment Variables" 部分：

| 变量名                 | 值                                 |
| ------------------- | --------------------------------- |
| `VITE_API_BASE_URL` | `https://你的后端地址.onrender.com/api` |
| `VITE_APP_VARIANT`  | `fullstack`                       |

**添加步骤：**

1. 在 "Key" 输入 `VITE_API_BASE_URL`
2. 在 "Value" 输入你的后端地址（替换 `你的后端地址`）
3. 点击 "Add"
4. 重复以上步骤添加 `VITE_APP_VARIANT`

**💡 环境变量说明**：

**VITE\_API\_BASE\_URL**：

- 后端 API 地址
- 必须以 `/api` 结尾
- 必须使用 HTTPS
- 示例：`https://careerfit-backend.onrender.com/api`

**VITE\_APP\_VARIANT**：

- 应用变体标识
- `fullstack`: 完整前后端应用
- `frontend-only`: 仅前端（开发模式）

**⚠️ 重要提示**：

- Vite 环境变量必须以 `VITE_` 开头才能在前端访问
- 环境变量在构建时注入，修改后需要重新部署
- 不要在前端环境变量中存储敏感信息

**环境变量作用域**：

- Production: 生产环境
- Preview: 预览环境（PR）
- Development: 开发环境（本地）

### 3.5 部署

1. 点击 "Deploy"
2. 等待部署完成（约 2-3 分钟）
3. 看到庆祝动画表示部署成功

**⏱️ 部署阶段**：

1. **Queued** (几秒)
   - 部署任务进入队列
   - 等待构建资源
2. **Building** (1-2分钟)
   - 安装依赖
   - 执行构建命令
   - 生成静态文件
3. **Deploying** (30秒 - 1分钟)
   - 上传构建产物
   - 配置 CDN
   - 更新 DNS
4. **Ready** (完成)
   - 部署成功
   - 可以访问

**💡 查看构建日志**：

- 点击部署详情页面
- 查看 "Building" 阶段日志
- 如果失败，日志会显示错误信息

### 3.6 获取前端地址

1. 部署完成后，点击 "Continue to Dashboard"
2. 在项目页面可以看到部署地址，如：`https://careerfit-agent.vercel.app`
3. 点击地址访问你的应用

**💡 Vercel 域名说明**：

- 默认域名：`[project-name].vercel.app`
- 可以配置自定义域名
- 支持 HTTPS（自动配置 SSL 证书）

### 3.7 验证前端

**基本验证**：

1. 访问前端地址
2. 应该看到工作台页面
3. 检查控制台是否有错误

**API 连接验证**：

1. 打开浏览器开发者工具（F12）
2. 切换到 "Network" 标签
3. 刷新页面
4. 检查是否有 API 请求失败

**预期行为**：

- 如果后端未启动：API 请求失败，前端显示错误提示
- 如果后端已启动：API 请求成功，前端正常显示数据

**⚠️ 常见错误排查**：

**错误 1: 白屏或 404**

- 原因：Root Directory 设置错误
- 排查：检查 Vercel 项目设置
- 解决：重新配置 Root Directory 为 `frontend`

**错误 2: API 请求失败**

- 原因：环境变量配置错误
- 排查：检查 `VITE_API_BASE_URL` 是否正确
- 解决：更新环境变量并重新部署

**错误 3: CORS 错误**

- 原因：后端未配置 CORS
- 排查：检查浏览器控制台错误信息
- 解决：确认后端已配置允许前端域名

### 3.8 配置自动部署

Vercel 默认启用自动部署：

- 每次 push 到 main 分支，自动触发部署
- 可以在 Settings → Git 中配置
- 可以指定其他分支或禁用自动部署

**💡 部署策略**：

- `Production Branch`: 生产分支（默认 main）
- `Preview Branches`: 预览分支（其他分支）
- `Ignored Build Step`: 忽略某些文件的变更

### 3.9 配置预览部署

Vercel 为每个 PR 自动创建预览环境：

- URL 格式：`https://[project]-[hash].vercel.app`
- 可以在 PR 中直接查看预览
- 合并后预览环境自动删除

**💡 预览部署优势**：

- 快速验证变更
- 团队协作更方便
- 不影响生产环境

### 3.10 配置自定义域名（可选）

**添加域名**：

1. 进入项目 Settings → Domains
2. 输入你的域名（如 `careerfit.yourdomain.com`）
3. 点击 "Add"

**配置 DNS**：

1. 在域名服务商添加 CNAME 记录
2. 名称：`careerfit`（或你选择的子域名）
3. 值：`cname.vercel-dns.com`
4. 等待 DNS 生效（通常几分钟到几小时）

**SSL 证书**：

- Vercel 自动配置 Let's Encrypt 证书
- 通常几分钟内生效
- 支持自动续期

### 3.11 监控和分析

**Vercel Analytics**：

- 访问量统计
- 页面加载性能
- 地理分布
- 设备类型

**启用 Analytics**：

1. 进入项目 Settings → Analytics
2. 点击 "Enable Analytics"
3. 免费版有使用限制

**Speed Insights**：

- Core Web Vitals 指标
- 性能评分
- 优化建议

**日志查看**：

1. 进入项目页面
2. 点击 "Deployments" 标签
3. 选择具体部署
4. 点击 "Functions" 或 "Runtime Logs"

***

## 第四步：导入知识库数据

### 4.1 准备数据

后端部署完成后，需要导入知识库种子数据。

**💡 知识库说明**：

- 知识库用于增强匹配分析
- 包含技能标准、面试题库、学习资源等
- 可以自定义导入内容

**数据来源**：

- 项目自带种子数据：`backend/seeds/*.json`
- 自定义数据：按相同格式准备

### 4.2 使用 API 导入

**方法一：使用 curl 命令**

```bash
# 设置后端地址
BACKEND_URL="https://你的后端地址.onrender.com"

# 导入后端开发技能
curl -X POST "$BACKEND_URL/api/knowledge/import" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {"doc_type": "skill", "title": "Python", "content": "Python 是一种高级编程语言..."},
      {"doc_type": "skill", "title": "FastAPI", "content": "FastAPI 是现代 Python Web 框架..."}
    ]
  }'

# 导入数据分析技能
curl -X POST "$BACKEND_URL/api/knowledge/import" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {"doc_type": "skill", "title": "SQL", "content": "SQL 是结构化查询语言..."},
      {"doc_type": "skill", "title": "Pandas", "content": "Pandas 是 Python 数据分析库..."}
    ]
  }'
```

**💡 curl 命令说明**：

- `-X POST`: 使用 POST 方法
- `-H "Content-Type: application/json"`: 设置请求头
- `-d '...'`: 发送 JSON 数据
- Windows 用户可以使用 PowerShell 的 `Invoke-WebRequest`

**Windows PowerShell 替代命令**：

```powershell
$headers = @{"Content-Type"="application/json"}
$body = @{
    documents = @(
        @{doc_type="skill"; title="Python"; content="Python 是一种高级编程语言..."},
        @{doc_type="skill"; title="FastAPI"; content="FastAPI 是现代 Python Web 框架..."}
    )
} | ConvertTo-Json -Depth 10

Invoke-WebRequest -Uri "https://你的后端地址.onrender.com/api/knowledge/import" `
  -Method POST -Headers $headers -Body $body
```

**方法二：使用 Python 脚本**

创建 `import_to_production.py`：

```python
import requests
import json
from pathlib import Path

BACKEND_URL = "https://你的后端地址.onrender.com"
SEEDS_DIR = Path("backend/seeds")

def import_seed_file(filepath: Path):
    """导入单个种子文件"""
    with open(filepath, "r", encoding="utf-8") as f:
        documents = json.load(f)
    
    print(f"正在导入 {filepath.name}...")
    print(f"  文档数量: {len(documents)}")
    
    response = requests.post(
        f"{BACKEND_URL}/api/knowledge/import",
        json={"documents": documents},
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"  ✅ 成功导入: {result['imported']} 条")
        if result.get('skipped', 0) > 0:
            print(f"  ⚠️  跳过: {result['skipped']} 条（已存在）")
        return result['imported']
    else:
        print(f"  ❌ 失败: {response.status_code}")
        print(f"  错误信息: {response.text}")
        return 0

def main():
    """批量导入所有种子文件"""
    print(f"后端地址: {BACKEND_URL}")
    print(f"种子目录: {SEEDS_DIR}")
    print("-" * 50)
    
    if not SEEDS_DIR.exists():
        print(f"❌ 种子目录不存在: {SEEDS_DIR}")
        print("请确保在项目根目录运行此脚本")
        return
    
    total_imported = 0
    seed_files = list(SEEDS_DIR.glob("*.json"))
    
    if not seed_files:
        print("❌ 未找到种子文件")
        return
    
    print(f"找到 {len(seed_files)} 个种子文件\n")
    
    for seed_file in seed_files:
        imported = import_seed_file(seed_file)
        total_imported += imported
        print()
    
    print("-" * 50)
    print(f"总计导入: {total_imported} 条文档")
    
    # 验证导入结果
    print("\n验证导入结果...")
    response = requests.get(f"{BACKEND_URL}/api/knowledge/stats", timeout=30)
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ 知识库统计:")
        print(f"  总文档数: {stats['total_documents']}")
        for doc_type, count in stats.get('by_type', {}).items():
            print(f"  {doc_type}: {count} 条")
    else:
        print(f"❌ 验证失败: {response.status_code}")

if __name__ == "__main__":
    main()
```

运行脚本：

```bash
python import_to_production.py
```

**💡 脚本说明**：

- 自动扫描 `backend/seeds` 目录下的所有 JSON 文件
- 显示导入进度和结果
- 自动验证导入后的知识库状态
- 支持超时设置，避免长时间等待

**⚠️ 注意事项**：

- 确保在项目根目录运行脚本
- 确保后端服务已启动
- 如果导入失败，检查网络连接和后端日志

### 4.3 验证导入

访问：`https://你的后端地址.onrender.com/api/knowledge/stats`

应该看到类似：

```json
{
  "total_documents": 30,
  "by_type": {
    "skill": 30
  }
}
```

**💡 验证步骤**：

1. **检查文档数量**：
   - 总数应该大于 0
   - 按类型分类统计
2. **测试搜索功能**：
   ```bash
   curl -X POST "https://你的后端地址.onrender.com/api/knowledge/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "Python", "limit": 5}'
   ```
3. **检查向量索引**：
   - 如果搜索返回结果，说明向量索引正常
   - 如果无结果，检查 pgvector 扩展是否启用

### 4.4 自定义知识库

**数据格式**：

```json
[
  {
    "doc_type": "skill",
    "title": "技能名称",
    "content": "技能描述和标准...",
    "metadata": {
      "category": "分类",
      "level": "初级/中级/高级",
      "tags": ["标签1", "标签2"]
    }
  }
]
```

**文档类型**：

- `skill`: 技能标准
- `interview_question`: 面试题
- `learning_resource`: 学习资源
- `industry_standard`: 行业标准

**导入自定义数据**：

```python
import requests

BACKEND_URL = "https://你的后端地址.onrender.com"

documents = [
    {
        "doc_type": "skill",
        "title": "自定义技能",
        "content": "自定义内容...",
        "metadata": {"custom": "value"}
    }
]

response = requests.post(
    f"{BACKEND_URL}/api/knowledge/import",
    json={"documents": documents}
)

print(response.json())
```

### 4.5 知识库维护

**更新文档**：

- 相同 `title` 的文档会被更新
- 使用 API 重新导入即可

**删除文档**：

- 目前需要通过数据库直接操作
- 未来版本会提供 API

**备份知识库**：

```bash
# 导出知识库
curl "https://你的后端地址.onrender.com/api/knowledge/export" > knowledge_backup.json
```

**💡 最佳实践**：

- 定期备份知识库
- 导入前先在测试环境验证
- 保持文档内容更新
- 添加有用的 metadata 便于筛选

BACKEND\_URL = "<https://你的后端地址.onrender.com>"
SEEDS\_DIR = Path("backend/seeds")

def import\_seed\_file(filepath: Path):
with open(filepath, "r", encoding="utf-8") as f:
documents = json.load(f)

```
response = requests.post(
    f"{BACKEND_URL}/api/knowledge/import",
    json={"documents": documents}
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ {filepath.name}: 导入 {result['imported']} 条")
else:
    print(f"❌ {filepath.name}: {response.text}")
```

def main():
for seed\_file in SEEDS\_DIR.glob("\*.json"):
print(f"正在导入 {seed\_file.name}...")
import\_seed\_file(seed\_file)

```
# 验证导入结果
response = requests.get(f"{BACKEND_URL}/api/knowledge/stats")
if response.status_code == 200:
    stats = response.json()
    print(f"\n📊 知识库统计: {stats['total_documents']} 条文档")
```

if __name__ == "__main__":
main()

````

运行脚本：

```bash
python import_to_production.py
````

### 4.3 验证导入

访问：`https://你的后端地址.onrender.com/api/knowledge/stats`

应该看到类似：

```json
{
  "total_documents": 30,
  "by_type": {
    "skill": 30
  }
}
```

***

## 第五步：配置 LLM（可选）

如果需要启用大模型增强功能：

### 5.1 在 Render 添加环境变量

进入后端服务 → Environment：

| 变量名                      | 值                     |
| ------------------------ | --------------------- |
| `CAREERFIT_LLM_ENABLED`  | `true`                |
| `CAREERFIT_LLM_PROVIDER` | `openai_compatible`   |
| `CAREERFIT_LLM_BASE_URL` | 你的 API 地址             |
| `CAREERFIT_LLM_API_KEY`  | 你的 API 密钥             |
| `CAREERFIT_LLM_MODEL`    | 模型名称（如 `gpt-4o-mini`） |

**💡 环境变量说明**：

**CAREERFIT\_LLM\_ENABLED**：

- `true`: 启用 LLM 增强
- `false`: 禁用 LLM（默认）

**CAREERFIT\_LLM\_PROVIDER**：

- `openai_compatible`: OpenAI 兼容 API
- 未来支持更多提供商

**CAREERFIT\_LLM\_BASE\_URL**：

- API 服务地址
- 必须包含 `/v1` 后缀
- 示例：`https://api.openai.com/v1`

**CAREERFIT\_LLM\_API\_KEY**：

- API 密钥
- 从模型服务商获取
- **不要**提交到 Git 仓库

**CAREERFIT\_LLM\_MODEL**：

- 模型名称
- 不同服务商支持的模型不同
- 推荐使用性价比高的模型

### 5.2 支持的模型服务

| 服务            | BASE\_URL                     | MODEL            | 价格（每 1K tokens）    |
| ------------- | ----------------------------- | ---------------- | ------------------ |
| OpenAI        | `https://api.openai.com/v1`   | `gpt-4o-mini`    | $0.00015 / $0.0006 |
| OpenAI        | `https://api.openai.com/v1`   | `gpt-4o`         | $0.005 / $0.015    |
| DeepSeek      | `https://api.deepseek.com/v1` | `deepseek-chat`  | ¥0.001 / ¥0.002    |
| Kimi/Moonshot | `https://api.moonshot.cn/v1`  | `moonshot-v1-8k` | ¥0.012 / ¥0.012    |

**💡 模型选择建议**：

**性价比推荐**：

- OpenAI: `gpt-4o-mini`（便宜且效果好）
- DeepSeek: `deepseek-chat`（国内访问快）
- Kimi: `moonshot-v1-8k`（中文理解好）

**性能推荐**：

- OpenAI: `gpt-4o`（最强性能）
- Claude: `claude-3-5-sonnet`（需要适配）

**⚠️ 注意事项**：

- 不同模型价格差异大
- 建议先用便宜模型测试
- 监控 API 使用量和费用
- 设置预算限制避免超支

### 5.3 应用更改

添加环境变量后，Render 会自动重新部署。

**💡 部署流程**：

1. 修改环境变量
2. Render 自动触发重新部署
3. 等待 2-3 分钟
4. 验证 LLM 功能

### 5.4 验证 LLM 配置

**方法一：通过 API 测试**

```bash
# 创建测试岗位
curl -X POST "https://你的后端地址.onrender.com/api/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试岗位",
    "description": "Python 开发工程师..."
  }'

# 创建测试简历
curl -X POST "https://你的后端地址.onrender.com/api/resumes" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试简历",
    "content": "3年 Python 开发经验..."
  }'

# 执行分析（会调用 LLM）
curl -X POST "https://你的后端地址.onrender.com/api/analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 1,
    "resume_id": 1
  }'
```

**方法二：通过前端测试**

1. 访问前端地址
2. 创建岗位和简历
3. 执行匹配分析
4. 检查报告是否包含 LLM 增强内容

**💡 验证要点**：

- 分析报告包含简历建议
- 分析报告包含面试题
- 分析报告包含学习计划
- 分析报告包含 Next Best Action

### 5.5 LLM 调用监控

**查看 LLM 统计**：

```bash
curl "https://你的后端地址.onrender.com/api/llm/stats"
```

预期响应：

```json
{
  "total_calls": 10,
  "successful_calls": 9,
  "failed_calls": 1,
  "timeout_calls": 0,
  "cache_hits": 5,
  "cache_misses": 5,
  "average_duration": 2.5,
  "total_prompt_length": 5000,
  "total_response_length": 3000
}
```

**💡 监控指标**：

- `total_calls`: 总调用次数
- `successful_calls`: 成功次数
- `failed_calls`: 失败次数
- `timeout_calls`: 超时次数
- `cache_hits`: 缓存命中次数
- `average_duration`: 平均耗时

**优化建议**：

- 如果失败率高：检查 API Key、网络连接
- 如果超时多：考虑增加超时时间或换更快的模型
- 如果缓存命中低：检查缓存配置

### 5.6 成本控制

**设置预算**：

- OpenAI: 在 Billing → Usage limits 设置
- DeepSeek: 在账户设置中设置
- Kimi: 在控制台中设置

**监控费用**：

- 定期查看 API 使用量
- 设置费用告警
- 分析调用日志

**优化成本**：

- 使用缓存减少重复调用
- 选择性价比高的模型
- 优化 prompt 减少 token 消耗
- 批量处理请求

### 5.7 故障排查

**LLM 调用失败**：

1. **检查 API Key**：
   - 确认 Key 正确
   - 确认 Key 未过期
   - 确认有足够余额
2. **检查网络连接**：
   - 确认可以访问 API 地址
   - 检查是否有防火墙限制
   - 尝试本地测试
3. **检查模型名称**：
   - 确认模型名称正确
   - 确认账户有权限使用该模型
4. **查看日志**：
   - 在 Render 查看运行日志
   - 搜索 "LLM" 相关错误
   - 检查超时和重试记录

**常见错误**：

| 错误信息                        | 原因         | 解决方法          |
| --------------------------- | ---------- | ------------- |
| `401 Unauthorized`          | API Key 错误 | 检查 Key 是否正确   |
| `429 Too Many Requests`     | 请求过快       | 降低请求频率或升级套餐   |
| `500 Internal Server Error` | 服务端错误      | 稍后重试或联系服务商    |
| `timeout`                   | 超时         | 增加超时时间或换更快的模型 |

***

## 第六步：更新和维护

### 6.1 更新部署

**自动更新**：

- Render 和 Vercel 默认启用自动部署
- 每次 push 到 main 分支，自动触发部署
- 可以在设置中配置部署分支

**手动触发部署**：

**Render**：

1. 进入服务页面
2. 点击 "Manual Deploy" → "Deploy latest commit"
3. 等待部署完成

**Vercel**：

1. 进入项目页面
2. 点击 "Deployments" 标签
3. 点击最新部署旁的 "..." → "Redeploy"

**💡 更新流程**：

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 本地测试
cd backend && pytest -q
cd ../frontend && npm test

# 3. 提交更改
git add .
git commit -m "feat: update feature"
git push origin main

# 4. 等待自动部署
# Render 和 Vercel 会自动部署
```

### 6.2 回滚部署

**Render 回滚**：

1. 进入服务页面
2. 点击 "Events" 标签
3. 找到之前成功的部署
4. 点击 "Rollback to this deploy"

**Vercel 回滚**：

1. 进入项目页面
2. 点击 "Deployments" 标签
3. 找到之前成功的部署
4. 点击 "..." → "Promote to Production"

**💡 回滚建议**：

- 回滚前先确认问题原因
- 回滚后及时修复问题
- 记录回滚原因和时间

### 6.3 查看日志

**Render 日志**：

1. 进入服务页面
2. 点击 "Logs" 标签
3. 选择日志类型（Build / Deploy / Runtime）
4. 使用搜索功能过滤日志

**Vercel 日志**：

1. 进入项目页面
2. 点击 "Deployments" 标签
3. 选择具体部署
4. 点击 "Functions" 或 "Runtime Logs"

**💡 日志分析**：

- 搜索 "ERROR" 或 "Exception" 查找错误
- 搜索 "WARNING" 查找警告
- 关注时间戳定位问题
- 使用日志分析工具（如 Datadog）

### 6.4 监控和告警

**Render 监控**：

- CPU 使用率
- 内存使用率
- 请求数量
- 响应时间

**Vercel Analytics**：

- 访问量统计
- 页面加载性能
- 地理分布
- 设备类型

**设置告警**：

- Render: Settings → Notifications
- Vercel: Settings → Notifications
- 配置邮件或 Slack 通知

**💡 监控建议**：

- 设置 CPU/内存告警阈值
- 监控 API 响应时间
- 跟踪错误率
- 定期查看性能报告

### 6.5 数据库维护

**备份策略**：

- Supabase 自动备份（免费版每天备份，保留 7 天）
- 定期手动备份重要数据
- 测试备份恢复流程

**性能优化**：

- 监控数据库查询性能
- 添加必要的索引
- 清理旧数据
- 优化慢查询

**安全维护**：

- 定期更新数据库密码
- 检查访问权限
- 监控异常访问
- 及时应用安全补丁

### 6.6 安全最佳实践

**环境变量管理**：

- 不要提交敏感信息到 Git
- 定期轮换 API Key 和密码
- 使用不同的环境变量区分环境
- 限制环境变量访问权限

**HTTPS 配置**：

- 确保所有服务使用 HTTPS
- 检查 SSL 证书有效期
- 配置 HSTS 头

**访问控制**：

- 限制数据库访问 IP（如果可能）
- 配置 CORS 白名单
- 启用速率限制
- 监控异常访问

**定期安全检查**：

- 检查依赖漏洞（`npm audit`, `pip audit`）
- 更新过时的依赖
- 审查代码安全
- 进行渗透测试（如果需要）

***

## 常见问题

### Q: 后端启动失败

**检查步骤：**

1. 查看 Render 的构建日志
2. 检查环境变量是否正确
3. 确认数据库连接字符串格式正确（`postgresql+psycopg://`）

**常见错误：**

- `Connection refused`: 数据库地址错误
- `FATAL: password authentication failed`: 密码错误
- `database "postgres" does not exist`: 数据库未创建

**详细排查**：

**错误 1: ModuleNotFoundError**

```
ModuleNotFoundError: No module named 'xxx'
```

- 原因：依赖未安装或版本不兼容
- 解决：检查 requirements.txt，确保所有依赖都列出

**错误 2: Port already in use**

```
Error: Port 10000 is already in use
```

- 原因：端口被占用
- 解决：Render 会自动分配端口，检查启动命令是否使用了硬编码端口

**错误 3: Database connection failed**

```
psycopg.OperationalError: connection failed
```

- 原因：数据库连接字符串错误或网络问题
- 解决：
  1. 检查连接字符串格式
  2. 确认数据库已启动
  3. 检查网络连接
  4. 验证密码是否正确

### Q: 前端无法连接后端

**检查步骤：**

1. 确认 `VITE_API_BASE_URL` 配置正确
2. 确认后端已成功部署（访问 `/health`）
3. 检查浏览器控制台是否有 CORS 错误

**解决方法：**

- 确保后端地址以 `/api` 结尾
- 确保使用 HTTPS

**详细排查**：

**错误 1: CORS 错误**

```
Access to XMLHttpRequest at '...' from origin '...' has been blocked by CORS policy
```

- 原因：后端未配置允许前端域名
- 解决：检查后端 CORS 配置，确保包含前端域名

**错误 2: Network Error**

```
Error: Network Error
```

- 原因：后端未启动或地址错误
- 解决：
  1. 确认后端已部署成功
  2. 检查后端地址是否正确
  3. 尝试直接访问后端地址

**错误 3: 404 Not Found**

```
GET https://xxx/api/xxx 404 (Not Found)
```

- 原因：API 路径错误
- 解决：检查 API 路径是否正确

### Q: 知识库搜索无结果

**检查步骤：**

1. 确认已导入种子数据
2. 访问 `/api/knowledge/stats` 检查文档数量
3. 检查 pgvector 扩展是否启用

**详细排查**：

**问题 1: 文档数量为 0**

- 原因：未导入数据或导入失败
- 解决：重新运行导入脚本，检查日志

**问题 2: pgvector 扩展未启用**

- 原因：Supabase 项目未启用扩展
- 解决：在 SQL Editor 中执行 `CREATE EXTENSION IF NOT EXISTS vector;`

**问题 3: 向量索引问题**

- 原因：向量索引损坏或未创建
- 解决：检查数据库日志，重建索引

### Q: Render 服务休眠

免费版 Render 在 15 分钟无请求后会休眠，首次访问可能需要等待 30-60 秒唤醒。

**解决方法：**

- 升级到付费计划
- 使用外部监控服务定期访问

**推荐监控服务**：

- UptimeRobot（免费）
- Pingdom（免费）
- Better Uptime（免费）

**配置示例（UptimeRobot）**：

1. 注册 UptimeRobot 账号
2. 添加新监控
3. 监控类型：HTTP(s)
4. URL：`https://你的后端地址.onrender.com/health`
5. 监控间隔：5 分钟
6. 保存设置

### Q: LLM 调用超时

**原因**：

- 模型响应慢
- 网络延迟
- Prompt 过长

**解决方法**：

1. 增加超时时间（`CAREERFIT_LLM_TIMEOUT_SECONDS`）
2. 换更快的模型
3. 优化 Prompt 减少 token 数量
4. 启用缓存减少重复调用

### Q: 部署后功能异常

**排查步骤**：

1. 检查环境变量是否正确
2. 查看运行日志
3. 对比本地和生产环境差异
4. 检查数据库迁移是否执行

**常见原因**：

- 环境变量缺失或错误
- 数据库表结构未更新
- 依赖版本不一致
- 配置文件未提交

***

## 费用说明

### 免费额度详情

| 服务       | 免费额度      | 限制                 | 适合场景          |
| -------- | --------- | ------------------ | ------------- |
| Vercel   | 无限带宽      | 个人项目免费             | 个人博客、作品集、小型应用 |
| Render   | 750 小时/月  | 15分钟无请求后休眠         | 开发测试、小型应用     |
| Supabase | 500MB 数据库 | 1GB 文件存储, 2GB 带宽/月 | 小型应用、原型开发     |

**总计：完全免费**（适合个人项目）

### 付费升级建议

**何时考虑付费**：

**Render 升级场景**：

- 需要避免休眠（Starter $7/月）
- 需要更多内存和 CPU（Standard $25/月）
- 需要自动扩容（Pro $85/月）

**Supabase 升级场景**：

- 数据库超过 500MB（Pro $25/月）
- 需要更多带宽（Pro 包含 250GB）
- 需要每日备份保留更久（Pro 保留 30 天）

**Vercel 升级场景**：

- 需要团队协作（Pro $20/用户/月）
- 需要更长的构建时间（Pro 45分钟）
- 需要高级分析功能

### 成本估算

**小型应用（免费）**：

- 用户数：< 100
- 日活：< 10
- 数据量：< 100MB
- 月成本：$0

**中型应用（$30-50/月）**：

- 用户数：100-1000
- 日活：10-100
- 数据量：100MB-1GB
- 月成本：
  - Render Starter: $7
  - Supabase Pro: $25
  - 总计：$32/月

**大型应用（$100+/月）**：

- 用户数：> 1000
- 日活：> 100
- 数据量：> 1GB
- 月成本：
  - Render Standard: $25
  - Supabase Pro: $25
  - LLM API: $50+
  - 总计：$100+/月

### 节省成本技巧

1. **优化资源使用**：
   - 使用缓存减少数据库查询
   - 优化图片和静态资源
   - 启用 CDN 加速
2. **选择合适的套餐**：
   - 从免费版开始，按需升级
   - 监控使用量，避免浪费
   - 利用学生/开源项目优惠
3. **优化 LLM 成本**：
   - 选择性价比高的模型
   - 使用缓存减少重复调用
   - 优化 Prompt 减少 token 消耗

***

## 部署检查清单

### 部署前检查

- [ ] GitHub 仓库已创建
- [ ] 代码已推送到 main 分支
- [ ] README.md 已更新
- [ ] 环境变量列表已准备

### 数据库部署检查

- [ ] Supabase 账号已注册
- [ ] 项目已创建
- [ ] 数据库密码已保存
- [ ] 连接字符串已复制
- [ ] pgvector 扩展已启用
- [ ] 连接测试成功

### 后端部署检查

- [ ] Render 账号已注册
- [ ] GitHub 仓库已连接
- [ ] Root Directory 设置为 `backend`
- [ ] 环境变量已配置
- [ ] 构建成功
- [ ] 服务状态为 "Live"
- [ ] `/health` 端点可访问
- [ ] `/docs` API 文档可访问

### 前端部署检查

- [ ] Vercel 账号已注册
- [ ] GitHub 仓库已连接
- [ ] Root Directory 设置为 `frontend`
- [ ] 环境变量已配置
- [ ] 构建成功
- [ ] 前端页面可访问
- [ ] API 连接正常

### 功能验证检查

- [ ] 知识库数据已导入
- [ ] 知识库统计正常
- [ ] 可以创建岗位
- [ ] 可以创建简历
- [ ] 可以执行匹配分析
- [ ] 分析报告正常显示
- [ ] （可选）LLM 功能正常

### 安全检查

- [ ] 环境变量未提交到 Git
- [ ] API Key 已妥善保管
- [ ] 数据库密码强度足够
- [ ] HTTPS 已启用
- [ ] CORS 配置正确

### 监控和维护检查

- [ ] 日志可正常查看
- [ ] 监控已配置（可选）
- [ ] 告警已设置（可选）
- [ ] 备份策略已制定

***

## 下一步

### 推荐配置

**1. 配置自定义域名**：

- 提升品牌形象
- 更容易记忆
- 完全控制

**2. 设置 CI/CD**：

- 自动化测试
- 自动化部署
- 代码质量保证

**3. 添加监控和日志**：

- 实时监控服务状态
- 快速定位问题
- 性能优化

**4. 配置 LLM 服务**：

- 增强分析报告
- 提供个性化建议
- 提升用户体验

### 高级功能

**性能优化**：

- 启用 CDN
- 配置缓存策略
- 优化数据库查询
- 图片压缩和懒加载

**安全加固**：

- 配置 WAF（Web Application Firewall）
- 启用 DDoS 防护
- 定期安全审计
- 设置速率限制

**扩展功能**：

- 添加用户认证（如果需要）
- 集成第三方服务
- 添加更多 AI 功能
- 开发移动应用

### 学习资源

**官方文档**：

- [Vercel 文档](https://vercel.com/docs)
- [Render 文档](https://render.com/docs)
- [Supabase 文档](https://supabase.com/docs)

**社区支持**：

- [Vercel Discord](https://vercel.com/discord)
- [Render Community](https://render.com/community)
- [Supabase Discord](https://supabase.com/discord)

**教程和示例**：

- [Next.js 部署教程](https://nextjs.org/docs/deployment)
- [FastAPI 部署指南](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL 最佳实践](https://www.postgresql.org/docs/current/best-practices.html)

***

## 支持与反馈

### 获取帮助

**项目相关**：

- GitHub Issues: <https://github.com/crepp124214/careerfit-agent/issues>
- 查看项目文档: `README.md`, `docs/`

**平台相关**：

- Vercel 支持: <https://vercel.com/support>
- Render 支持: <https://render.com/support>
- Supabase 支持: <https://supabase.com/support>

### 贡献指南

欢迎贡献代码、报告问题或提出建议：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 更新日志

查看项目的最新更新和变更：

- GitHub Releases: <https://github.com/crepp124214/careerfit-agent/releases>
- CHANGELOG.md: 项目根目录

***

## 附录

### 环境变量完整列表

**后端环境变量**：

| 变量名                             | 必需 | 默认值                 | 说明                 |
| ------------------------------- | -- | ------------------- | ------------------ |
| `CAREERFIT_ENVIRONMENT`         | 否  | `development`       | 环境标识               |
| `CAREERFIT_DATABASE_URL`        | 是  | -                   | 数据库连接字符串           |
| `CAREERFIT_LLM_ENABLED`         | 否  | `false`             | 是否启用 LLM           |
| `CAREERFIT_LLM_PROVIDER`        | 否  | `openai_compatible` | LLM 提供商            |
| `CAREERFIT_LLM_BASE_URL`        | 条件 | -                   | API 地址（启用 LLM 时必需） |
| `CAREERFIT_LLM_API_KEY`         | 条件 | -                   | API 密钥（启用 LLM 时必需） |
| `CAREERFIT_LLM_MODEL`           | 条件 | -                   | 模型名称（启用 LLM 时必需）   |
| `CAREERFIT_LLM_TIMEOUT_SECONDS` | 否  | `120`               | LLM 超时时间           |

**前端环境变量**：

| 变量名                 | 必需 | 默认值         | 说明        |
| ------------------- | -- | ----------- | --------- |
| `VITE_API_BASE_URL` | 是  | -           | 后端 API 地址 |
| `VITE_APP_VARIANT`  | 否  | `fullstack` | 应用变体      |

### 常用命令速查

**本地开发**：

```bash
# 后端
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

**部署相关**：

```bash
# 查看部署状态
vercel ls

# 查看日志
vercel logs

# 手动部署
vercel --prod
```

**数据库操作**：

```bash
# 导入数据
python import_to_production.py

# 查看统计
curl https://你的后端地址.onrender.com/api/knowledge/stats
```

### 故障排查流程图

```
问题发生
    ↓
查看日志 → 找到错误信息
    ↓
检查环境变量 → 确认配置正确
    ↓
检查网络连接 → 确认服务可访问
    ↓
检查数据库 → 确认连接正常
    ↓
重启服务 → 尝试解决
    ↓
如果仍失败 → 查看 FAQ 或提交 Issue
```

***

**祝你部署顺利！** 🎉

如有任何问题，欢迎在 GitHub 提交 Issue 或查阅文档。>
