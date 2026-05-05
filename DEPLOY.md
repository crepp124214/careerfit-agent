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

---

## 第一步：创建数据库 (Supabase)

### 1.1 注册并创建项目

1. 访问 https://supabase.com
2. 点击 "Start your project"
3. 使用 GitHub 账号登录
4. 授权 Supabase 访问你的 GitHub
5. 创建新组织（如果还没有）：
   - 点击 "New organization"
   - 输入组织名称（如：个人项目）
   - 点击 "Create organization"

### 1.2 创建数据库项目

1. 在组织页面点击 "New project"
2. 填写项目信息：
   - **Name**: `careerfit`
   - **Database Password**: 设置一个强密码（请保存好！）
   - **Region**: 选择 `Northeast Asia (Tokyo)` 或最近的区域
   - **Plan**: 选择 "Free"
3. 点击 "Create new project"
4. 等待约 2 分钟，项目创建完成

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

### 1.4 启用 pgvector 扩展

1. 点击左侧菜单 "SQL Editor"
2. 点击 "New query"
3. 输入以下 SQL：
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
4. 点击 "Run" 执行
5. 看到成功提示即可

---

## 第二步：部署后端 (Render)

### 2.1 注册 Render

1. 访问 https://dashboard.render.com
2. 点击 "Get Started"
3. 选择 "Sign up with GitHub"
4. 授权 Render 访问你的 GitHub

### 2.2 创建 Web Service

1. 登录后，点击 "New +" 按钮
2. 选择 "Web Service"
3. 在 "Connect a repository" 部分：
   - 如果看不到 `careerfit-agent` 仓库，点击 "Configure account"
   - 勾选 "All repositories" 或只选择 `careerfit-agent`
   - 点击 "Install" 完成授权
4. 返回 Render，刷新页面
5. 找到 `careerfit-agent` 仓库，点击 "Connect"

### 2.3 配置 Web Service

填写以下配置：

| 设置项 | 值 |
|-------|-----|
| **Name** | `careerfit-backend` |
| **Region** | `Oregon (US West)` 或 `Frankfurt (EU Central)` |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | `Free` |

### 2.4 添加环境变量

点击 "Advanced" 展开，然后点击 "Add Environment Variable"：

| 变量名 | 值 | 说明 |
|-------|-----|------|
| `CAREERFIT_ENVIRONMENT` | `production` | 生产环境标识 |
| `CAREERFIT_DATABASE_URL` | `postgresql+psycopg://...` | Supabase 连接字符串 |
| `CAREERFIT_LLM_ENABLED` | `false` | 暂不启用 LLM |
| `CAREERFIT_LLM_TIMEOUT_SECONDS` | `120` | LLM 超时时间 |

**添加环境变量的步骤：**
1. 在 "Key" 输入框输入变量名
2. 在 "Value" 输入框输入变量值
3. 点击 "Add Environment Variable"
4. 重复以上步骤添加所有变量

### 2.5 创建服务

1. 检查所有配置是否正确
2. 点击 "Create Web Service"
3. 等待构建完成（约 5-10 分钟）

### 2.6 查看部署状态

1. 在服务页面可以看到构建日志
2. 构建完成后，状态变为 "Live"
3. 记录后端 URL，如：`https://careerfit-backend.onrender.com`

### 2.7 验证后端

1. 访问 `https://你的后端地址.onrender.com/health`
2. 应该看到：`{"status": "ok", "environment": "production"}`
3. 访问 `https://你的后端地址.onrender.com/docs`
4. 应该看到 FastAPI 自动生成的 API 文档

---

## 第三步：部署前端 (Vercel)

### 3.1 注册 Vercel

1. 访问 https://vercel.com
2. 点击 "Sign Up"
3. 选择 "Continue with GitHub"
4. 授权 Vercel 访问你的 GitHub

### 3.2 导入项目

1. 登录后，点击 "Add New..." → "Project"
2. 在 "Import Git Repository" 部分：
   - 如果看不到 `careerfit-agent` 仓库，点击 "Adjust GitHub App Permissions"
   - 勾选 "All repositories" 或只选择 `careerfit-agent`
   - 点击 "Install" 完成授权
3. 返回 Vercel，刷新页面
4. 找到 `careerfit-agent` 仓库，点击 "Import"

### 3.3 配置项目

**Configure Project 页面：**

| 设置项 | 值 |
|-------|-----|
| **Project Name** | `careerfit-agent` |
| **Framework Preset** | `Vue.js` |
| **Root Directory** | 点击 "Edit"，输入 `frontend` |
| **Build Command** | `npm run build`（默认） |
| **Output Directory** | `dist`（默认） |
| **Install Command** | `npm install`（默认） |

### 3.4 添加环境变量

在 "Environment Variables" 部分：

| 变量名 | 值 |
|-------|-----|
| `VITE_API_BASE_URL` | `https://你的后端地址.onrender.com/api` |
| `VITE_APP_VARIANT` | `fullstack` |

**添加步骤：**
1. 在 "Key" 输入 `VITE_API_BASE_URL`
2. 在 "Value" 输入你的后端地址（替换 `你的后端地址`）
3. 点击 "Add"
4. 重复以上步骤添加 `VITE_APP_VARIANT`

### 3.5 部署

1. 点击 "Deploy"
2. 等待部署完成（约 2-3 分钟）
3. 看到庆祝动画表示部署成功

### 3.6 获取前端地址

1. 部署完成后，点击 "Continue to Dashboard"
2. 在项目页面可以看到部署地址，如：`https://careerfit-agent.vercel.app`
3. 点击地址访问你的应用

---

## 第四步：导入知识库数据

### 4.1 准备数据

后端部署完成后，需要导入知识库种子数据。

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

**方法二：使用 Python 脚本**

创建 `import_to_production.py`：

```python
import requests
import json
from pathlib import Path

BACKEND_URL = "https://你的后端地址.onrender.com"
SEEDS_DIR = Path("backend/seeds")

def import_seed_file(filepath: Path):
    with open(filepath, "r", encoding="utf-8") as f:
        documents = json.load(f)
    
    response = requests.post(
        f"{BACKEND_URL}/api/knowledge/import",
        json={"documents": documents}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {filepath.name}: 导入 {result['imported']} 条")
    else:
        print(f"❌ {filepath.name}: {response.text}")

def main():
    for seed_file in SEEDS_DIR.glob("*.json"):
        print(f"正在导入 {seed_file.name}...")
        import_seed_file(seed_file)
    
    # 验证导入结果
    response = requests.get(f"{BACKEND_URL}/api/knowledge/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"\n📊 知识库统计: {stats['total_documents']} 条文档")

if __name__ == "__main__":
    main()
```

运行脚本：
```bash
python import_to_production.py
```

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

---

## 第五步：配置 LLM（可选）

如果需要启用大模型增强功能：

### 5.1 在 Render 添加环境变量

进入后端服务 → Environment：

| 变量名 | 值 |
|-------|-----|
| `CAREERFIT_LLM_ENABLED` | `true` |
| `CAREERFIT_LLM_PROVIDER` | `openai_compatible` |
| `CAREERFIT_LLM_BASE_URL` | 你的 API 地址 |
| `CAREERFIT_LLM_API_KEY` | 你的 API 密钥 |
| `CAREERFIT_LLM_MODEL` | 模型名称（如 `gpt-4o-mini`） |

### 5.2 支持的模型服务

| 服务 | BASE_URL | MODEL |
|------|----------|-------|
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini`, `gpt-4o` |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| Kimi/Moonshot | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` |

### 5.3 应用更改

添加环境变量后，Render 会自动重新部署。

---

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

### Q: 前端无法连接后端

**检查步骤：**
1. 确认 `VITE_API_BASE_URL` 配置正确
2. 确认后端已成功部署（访问 `/health`）
3. 检查浏览器控制台是否有 CORS 错误

**解决方法：**
- 确保后端地址以 `/api` 结尾
- 确保使用 HTTPS

### Q: 知识库搜索无结果

**检查步骤：**
1. 确认已导入种子数据
2. 访问 `/api/knowledge/stats` 检查文档数量
3. 检查 pgvector 扩展是否启用

### Q: Render 服务休眠

免费版 Render 在 15 分钟无请求后会休眠，首次访问可能需要等待 30-60 秒唤醒。

**解决方法：**
- 升级到付费计划
- 使用外部监控服务定期访问

---

## 费用说明

| 服务 | 免费额度 | 限制 |
|-----|---------|------|
| Vercel | 无限 | 个人项目免费 |
| Render | 750 小时/月 | 休眠机制 |
| Supabase | 500MB 数据库 | 1GB 文件存储 |

**总计：完全免费**（适合个人项目）

---

## 部署检查清单

- [ ] Supabase 数据库创建完成
- [ ] pgvector 扩展已启用
- [ ] Render 后端部署成功
- [ ] 后端健康检查通过
- [ ] Vercel 前端部署成功
- [ ] 前端可以访问后端 API
- [ ] 知识库数据导入完成
- [ ] 创建测试岗位和简历
- [ ] 执行匹配分析测试

---

## 下一步

- 配置自定义域名（可选）
- 设置 GitHub Actions CI/CD（可选）
- 添加监控和日志（可选）
- 配置 LLM 服务（可选）

---

## 支持与反馈

如有问题，请在 GitHub 提交 Issue：
https://github.com/crepp124214/careerfit-agent/issues
