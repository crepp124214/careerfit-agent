# CareerFit Agent 部署指南

本指南将帮助你将项目部署到云平台，实现从GitHub自动部署。

## 架构概览

```
GitHub 仓库
    ├── frontend/ → Vercel (免费)
    ├── backend/ → Render (免费)
    └── 数据库 → Supabase (免费)
```

## 前置条件

- GitHub 账号
- Vercel 账号 (可用GitHub登录)
- Render 账号 (可用GitHub登录)
- Supabase 账号 (可用GitHub登录)

---

## 第一步：推送到GitHub

### 1.1 初始化Git仓库

```bash
cd e:\New\ project\ 2
git init
git add .
git commit -m "Initial commit: CareerFit Agent"
```

### 1.2 创建GitHub仓库

1. 访问 https://github.com/new
2. 仓库名称: `careerfit-agent`
3. 设为私有或公开
4. 不要勾选 "Add a README file"
5. 点击 "Create repository"

### 1.3 推送代码

```bash
git remote add origin https://github.com/你的用户名/careerfit-agent.git
git branch -M main
git push -u origin main
```

---

## 第二步：创建数据库 (Supabase)

### 2.1 创建项目

1. 访问 https://supabase.com
2. 点击 "New Project"
3. 选择组织，填写项目名称
4. 设置数据库密码（请保存好）
5. 选择最近的区域
6. 点击 "Create new project"

### 2.2 获取连接字符串

1. 进入项目后，点击 "Project Settings" → "Database"
2. 找到 "Connection string" → "URI"
3. 复制连接字符串，格式如下：
   ```
   postgresql://postgres.[项目ID]:[密码]@aws-0-[区域].pooler.supabase.com:6543/postgres
   ```

### 2.3 启用pgvector扩展

1. 点击 "SQL Editor"
2. 运行以下SQL：
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

---

## 第三步：部署后端 (Render)

### 3.1 创建Web Service

1. 访问 https://dashboard.render.com
2. 点击 "New" → "Web Service"
3. 连接GitHub仓库
4. 选择 `careerfit-agent` 仓库

### 3.2 配置服务

| 设置项 | 值 |
|-------|-----|
| Name | careerfit-backend |
| Region | Oregon (US West) |
| Branch | main |
| Root Directory | backend |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Instance Type | Free |

### 3.3 添加环境变量

点击 "Advanced" → "Add Environment Variable":

| 变量名 | 值 |
|-------|-----|
| CAREERFIT_ENVIRONMENT | production |
| CAREERFIT_DATABASE_URL | (Supabase连接字符串，将`postgresql://`改为`postgresql+psycopg://`) |
| CAREERFIT_LLM_ENABLED | false |
| CAREERFIT_LLM_TIMEOUT_SECONDS | 120 |

### 3.4 部署

1. 点击 "Create Web Service"
2. 等待构建完成（约5-10分钟）
3. 记录后端URL，如：`https://careerfit-backend.onrender.com`

---

## 第四步：部署前端 (Vercel)

### 4.1 导入项目

1. 访问 https://vercel.com
2. 点击 "Add New" → "Project"
3. 导入GitHub仓库 `careerfit-agent`

### 4.2 配置项目

| 设置项 | 值 |
|-------|-----|
| Framework Preset | Vue.js |
| Root Directory | frontend |
| Build Command | `npm run build` |
| Output Directory | dist |

### 4.3 添加环境变量

点击 "Environment Variables":

| 变量名 | 值 |
|-------|-----|
| VITE_API_BASE_URL | `https://careerfit-backend.onrender.com/api` |
| VITE_APP_VARIANT | fullstack |

### 4.4 部署

1. 点击 "Deploy"
2. 等待部署完成（约2-3分钟）
3. 获得前端URL，如：`https://careerfit-agent.vercel.app`

---

## 第五步：导入知识库数据

### 5.1 使用API导入

后端部署完成后，调用API导入种子数据：

```bash
curl -X POST https://careerfit-backend.onrender.com/api/knowledge/import \
  -H "Content-Type: application/json" \
  -d @backend/seeds/backend_dev.json
```

或使用Python脚本：

```python
import requests
import json

backend_url = "https://careerfit-backend.onrender.com"
seeds = ["backend_dev.json", "data_analysis.json", "frontend_fullstack.json", "llm_app_dev.json"]

for seed_file in seeds:
    with open(f"backend/seeds/{seed_file}") as f:
        data = {"documents": json.load(f)}
    response = requests.post(f"{backend_url}/api/knowledge/import", json=data)
    print(f"{seed_file}: {response.json()}")
```

---

## 第六步：配置LLM (可选)

如果需要启用大模型增强功能：

### 6.1 在Render中添加环境变量

| 变量名 | 值 |
|-------|-----|
| CAREERFIT_LLM_ENABLED | true |
| CAREERFIT_LLM_PROVIDER | openai_compatible |
| CAREERFIT_LLM_BASE_URL | (你的API地址) |
| CAREERFIT_LLM_API_KEY | (你的API密钥) |
| CAREERFIT_LLM_MODEL | (模型名称) |

### 6.2 重新部署

修改环境变量后，Render会自动重新部署。

---

## 常见问题

### Q: 后端启动失败

检查日志中的错误信息，常见原因：
- 数据库连接字符串格式错误
- 环境变量未正确设置

### Q: 前端无法连接后端

1. 检查 `VITE_API_BASE_URL` 是否正确
2. 确保后端已成功部署
3. 检查CORS配置

### Q: 知识库搜索无结果

确保已导入种子数据，参考第五步。

---

## 费用说明

| 服务 | 免费额度 | 备注 |
|-----|---------|-----|
| Vercel | 无限 | 个人项目免费 |
| Render | 750小时/月 | Free计划 |
| Supabase | 500MB数据库 | Free计划 |

总计：**完全免费**（适合个人项目）

---

## 下一步

- 配置自定义域名
- 设置CI/CD流水线
- 添加监控和日志
