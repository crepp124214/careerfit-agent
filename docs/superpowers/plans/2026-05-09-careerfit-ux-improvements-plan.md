# CareerFit UX 改进实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 改善 CareerFit 前端 5 个 UX 维度：空状态引导、输入体验、报告信息密度、流程连贯性、导航精简

**Architecture:** 分 3 批实施。第 1 批新增后端解析预览 API + 前端向导和预览卡片；第 2 批重构报告页为仪表盘 + 强化 NBA 流程引导；第 3 批合并面试导航入口。每批独立可交付。

**Tech Stack:** Vue 3 + TypeScript + Pinia + ECharts（前端），FastAPI + Pydantic + SQLAlchemy（后端）

---

## 文件结构映射

### 第 1 批新增文件

| 文件 | 职责 |
|------|------|
| `backend/app/schemas/preview.py` | JD/简历解析预览的请求/响应 schema |
| `backend/app/api/routes/preview.py` | 解析预览 API 路由 |
| `backend/tests/test_preview_api.py` | 解析预览 API 测试 |
| `frontend/src/api/preview.ts` | 解析预览 API 客户端 |
| `frontend/src/components/workbench/OnboardingWizard.vue` | 分步引导向导 |
| `frontend/src/components/preview/JdPreviewCard.vue` | JD 解析预览卡片 |
| `frontend/src/components/preview/ResumePreviewCard.vue` | 简历解析预览卡片 |
| `frontend/tests/components/OnboardingWizard.test.ts` | 向导测试 |
| `frontend/tests/components/JdPreviewCard.test.ts` | JD 预览卡片测试 |
| `frontend/tests/components/ResumePreviewCard.test.ts` | 简历预览卡片测试 |

### 第 1 批修改文件

| 文件 | 变更 |
|------|------|
| `backend/app/main.py` | 注册 preview 路由 |
| `frontend/src/views/WorkspaceView.vue` | 空状态触发向导 |
| `frontend/src/router/index.ts` | 无变更（向导是组件非路由） |

### 第 2 批新增文件

| 文件 | 职责 |
|------|------|
| `frontend/src/components/report/ReportCard.vue` | 通用报告卡片容器 |
| `frontend/src/components/report/ReportDashboard.vue` | 仪表盘布局 |
| `frontend/src/components/report/NbaActionCard.vue` | NBA 行动卡片 |
| `frontend/src/components/report/GapListCard.vue` | 缺口列表卡片 |
| `frontend/src/components/report/SuggestionSummaryCard.vue` | 建议摘要卡片 |
| `frontend/src/components/report/InterviewPreviewCard.vue` | 面试题预览卡片 |
| `frontend/src/components/common/Breadcrumb.vue` | 面包屑组件 |
| `frontend/src/components/common/NbaBanner.vue` | 页面底部 NBA 横幅 |
| `frontend/tests/components/ReportDashboard.test.ts` | 仪表盘测试 |
| `frontend/tests/components/Breadcrumb.test.ts` | 面包屑测试 |

### 第 2 批修改文件

| 文件 | 变更 |
|------|------|
| `frontend/src/views/ReportView.vue` | 重构为仪表盘布局 |
| `frontend/src/components/workbench/NextBestActionCallout.vue` | 增加 target_route 和 context props |
| `frontend/src/views/LearningTasksView.vue` | 底部增加 NBA 横幅 |
| `frontend/src/views/InterviewDetailView.vue` | 底部增加 NBA 横幅 |
| `frontend/src/views/ResumesView.vue` | 创建后增加 NBA 横幅 |

### 第 3 批新增文件

| 文件 | 职责 |
|------|------|
| `frontend/src/views/InterviewView.vue` | 面试 Tab 容器视图 |

### 第 3 批修改文件

| 文件 | 变更 |
|------|------|
| `frontend/src/router/index.ts` | 新增 /interview 路由，旧路由重定向 |
| `frontend/src/components/layout/SideNav.vue` | 合并面试导航项 |

---

## 第 1 批：E 向导 + D 解析预览

### Task 1: 后端 JD 解析预览 Schema

**Files:**
- Create: `backend/app/schemas/preview.py`
- Test: `backend/tests/test_preview_api.py`

- [ ] **Step 1: 创建 preview schema**

```python
# backend/app/schemas/preview.py
from __future__ import annotations

from pydantic import BaseModel, Field


class PreviewRequest(BaseModel):
    content: str = Field(min_length=10, max_length=50000)


class JdPreviewSkill(BaseModel):
    name: str
    level: str = "mentioned"
    category: str = "technical"


class JdPreviewResponse(BaseModel):
    title: str = ""
    category: str = ""
    skills: list[JdPreviewSkill] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)
    domain_keywords: list[str] = Field(default_factory=list)


class ResumePreviewProject(BaseModel):
    name: str = ""
    role: str = ""
    highlights: list[str] = Field(default_factory=list)


class ResumePreviewEducation(BaseModel):
    school: str = ""
    major: str = ""
    degree: str = ""


class ResumePreviewResponse(BaseModel):
    name: str = ""
    skills: list[str] = Field(default_factory=list)
    projects: list[ResumePreviewProject] = Field(default_factory=list)
    education: list[ResumePreviewEducation] = Field(default_factory=list)
    experience_years: int = 0
```

- [ ] **Step 2: 提交**

```bash
git add backend/app/schemas/preview.py
git commit -m "feat: add parse preview schemas"
```

---

### Task 2: 后端 JD 解析预览 API

**Files:**
- Create: `backend/app/api/routes/preview.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_preview_api.py`

- [ ] **Step 1: 写失败测试 — JD 解析预览**

```python
# backend/tests/test_preview_api.py
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


def test_jd_parse_preview_returns_structure(client):
    resp = client.post("/api/jobs/parse-preview", json={
        "content": "我们需要一名Python后端开发工程师，熟练掌握FastAPI和PostgreSQL，有Docker经验优先。本科及以上学历，3年以上开发经验。"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "title" in data
    assert "skills" in data
    assert isinstance(data["skills"], list)
    assert "category" in data


def test_jd_parse_preview_rejects_short_content(client):
    resp = client.post("/api/jobs/parse-preview", json={"content": "short"})
    assert resp.status_code == 422


def test_resume_parse_preview_returns_structure(client):
    resp = client.post("/api/resumes/parse-preview", json={
        "content": "张三，本科毕业于北京大学计算机科学专业。3年后端开发经验，熟练使用Python、FastAPI、PostgreSQL、Docker。参与过电商平台后端架构设计，负责订单系统和支付模块开发。"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "skills" in data
    assert isinstance(data["skills"], list)


def test_resume_parse_preview_rejects_short_content(client):
    resp = client.post("/api/resumes/parse-preview", json={"content": "short"})
    assert resp.status_code == 422
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd backend && python -m pytest tests/test_preview_api.py -v`
Expected: 4 FAILED（路由不存在）

- [ ] **Step 3: 实现解析预览路由**

```python
# backend/app/api/routes/preview.py
import logging

from fastapi import APIRouter

from app.schemas.preview import (
    JdPreviewResponse,
    JdPreviewSkill,
    PreviewRequest,
    ResumePreviewEducation,
    ResumePreviewProject,
    ResumePreviewResponse,
)
from app.services.job_service import parse_job_profile
from app.services.resume_service import parse_resume_profile

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

router = APIRouter(prefix="/api", tags=["preview"])


@router.post("/jobs/parse-preview", response_model=JdPreviewResponse)
def jd_parse_preview(req: PreviewRequest) -> JdPreviewResponse:
    profile = parse_job_profile(req.content)
    skills = [
        JdPreviewSkill(
            name=d["name"],
            level=d.get("required_level", "mentioned"),
            category=d.get("category", "technical"),
        )
        for d in profile.get("skill_dimensions", [])
    ]
    return JdPreviewResponse(
        title=_guess_jd_title(req.content),
        category=profile.get("job_family", ""),
        skills=skills,
        requirements=profile.get("basic_requirements", []),
        domain_keywords=profile.get("domain_keywords", []),
    )


@router.post("/resumes/parse-preview", response_model=ResumePreviewResponse)
def resume_parse_preview(req: PreviewRequest) -> ResumePreviewResponse:
    profile = parse_resume_profile(req.content)
    skills = profile.get("skills", [])
    projects = [
        ResumePreviewProject(
            name=p.get("name", ""),
            role=p.get("role", ""),
            highlights=p.get("highlights", []),
        )
        for p in profile.get("projects", [])
    ]
    education = [
        ResumePreviewEducation(
            school=e.get("school", ""),
            major=e.get("major", ""),
            degree=e.get("degree", ""),
        )
        for e in profile.get("education", [])
    ]
    return ResumePreviewResponse(
        name=profile.get("candidate_name", ""),
        skills=skills,
        projects=projects,
        education=education,
        experience_years=profile.get("experience_years", 0),
    )


def _guess_jd_title(content: str) -> str:
    for line in content.split("\n"):
        line = line.strip()
        if len(line) > 4 and len(line) < 60:
            return line
    return ""
```

- [ ] **Step 4: 注册路由到 main.py**

在 `backend/app/main.py` 中添加 preview 路由注册。找到其他路由注册的位置（如 `from app.api.routes import jobs`），添加：

```python
from app.api.routes.preview import router as preview_router
app.include_router(preview_router)
```

- [ ] **Step 5: 运行测试确认通过**

Run: `cd backend && python -m pytest tests/test_preview_api.py -v`
Expected: 4 passed

- [ ] **Step 6: 提交**

```bash
git add backend/app/api/routes/preview.py backend/app/main.py backend/tests/test_preview_api.py
git commit -m "feat: add JD and resume parse preview API"
```

---

### Task 3: 前端解析预览 API 客户端

**Files:**
- Create: `frontend/src/api/preview.ts`

- [ ] **Step 1: 创建 preview API 客户端**

```typescript
// frontend/src/api/preview.ts
import { apiClient } from './client'

export interface JdPreviewSkill {
  name: string
  level: string
  category: string
}

export interface JdPreviewResponse {
  title: string
  category: string
  skills: JdPreviewSkill[]
  requirements: string[]
  domain_keywords: string[]
}

export interface ResumePreviewProject {
  name: string
  role: string
  highlights: string[]
}

export interface ResumePreviewEducation {
  school: string
  major: string
  degree: string
}

export interface ResumePreviewResponse {
  name: string
  skills: string[]
  projects: ResumePreviewProject[]
  education: ResumePreviewEducation[]
  experience_years: number
}

export async function parseJdPreview(content: string) {
  return apiClient.post<JdPreviewResponse>('/jobs/parse-preview', { content })
}

export async function parseResumePreview(content: string) {
  return apiClient.post<ResumePreviewResponse>('/resumes/parse-preview', { content })
}
```

- [ ] **Step 2: 运行 typecheck**

Run: `cd frontend && npm run typecheck`
Expected: 无错误

- [ ] **Step 3: 提交**

```bash
git add frontend/src/api/preview.ts
git commit -m "feat: add parse preview API client"
```

---

### Task 4: JD 解析预览卡片组件

**Files:**
- Create: `frontend/src/components/preview/JdPreviewCard.vue`
- Test: `frontend/tests/components/JdPreviewCard.test.ts`

- [ ] **Step 1: 写失败测试**

```typescript
// frontend/tests/components/JdPreviewCard.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import JdPreviewCard from '@/components/preview/JdPreviewCard.vue'
import type { JdPreviewResponse } from '@/api/preview'

const mockData: JdPreviewResponse = {
  title: '后端开发工程师',
  category: 'software_engineering',
  skills: [
    { name: 'Python', level: 'project_practice', category: 'programming' },
    { name: 'SQL', level: 'mentioned', category: 'database' },
  ],
  requirements: ['3年经验', '本科及以上'],
  domain_keywords: ['后端开发'],
}

describe('JdPreviewCard', () => {
  it('renders title and skills', () => {
    const wrapper = mount(JdPreviewCard, {
      props: { data: mockData },
    })
    expect(wrapper.text()).toContain('后端开发工程师')
    expect(wrapper.text()).toContain('Python')
    expect(wrapper.text()).toContain('SQL')
  })

  it('renders requirements', () => {
    const wrapper = mount(JdPreviewCard, {
      props: { data: mockData },
    })
    expect(wrapper.text()).toContain('3年经验')
  })

  it('shows empty state when data has no skills', () => {
    const emptyData = { ...mockData, skills: [] }
    const wrapper = mount(JdPreviewCard, {
      props: { data: emptyData },
    })
    expect(wrapper.text()).toContain('未提取到技能')
  })
})
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd frontend && npm test -- --run tests/components/JdPreviewCard.test.ts`
Expected: FAIL（组件不存在）

- [ ] **Step 3: 实现 JdPreviewCard**

```vue
<!-- frontend/src/components/preview/JdPreviewCard.vue -->
<script setup lang="ts">
import type { JdPreviewResponse } from '@/api/preview'

defineProps<{
  data: JdPreviewResponse
}>()
</script>

<template>
  <section class="jd-preview" aria-label="岗位解析预览">
    <header class="jd-preview__header">
      <h3 class="jd-preview__title">{{ data.title || '岗位信息' }}</h3>
      <span v-if="data.category" class="jd-preview__category">{{ data.category }}</span>
    </header>

    <div v-if="data.skills.length > 0" class="jd-preview__section">
      <p class="jd-preview__label">提取的技能维度</p>
      <ul class="jd-preview__skills">
        <li v-for="skill in data.skills" :key="skill.name" class="jd-preview__skill">
          <span class="jd-preview__skill-name">{{ skill.name }}</span>
          <span class="jd-preview__skill-level">{{ skill.level }}</span>
        </li>
      </ul>
    </div>
    <p v-else class="jd-preview__empty">未提取到技能</p>

    <div v-if="data.requirements.length > 0" class="jd-preview__section">
      <p class="jd-preview__label">基础要求</p>
      <ul class="jd-preview__requirements">
        <li v-for="req in data.requirements" :key="req">{{ req }}</li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.jd-preview {
  padding: var(--space-md);
  background-color: var(--color-surface-2);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
}

.jd-preview__header {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-sm);
}

.jd-preview__title {
  margin: 0;
  font-size: var(--font-body-lg-size);
  font-weight: 600;
  color: var(--color-ink);
}

.jd-preview__category {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
  background-color: var(--color-surface-3);
  padding: 2px 8px;
  border-radius: var(--rounded-pill);
}

.jd-preview__section {
  margin-top: var(--space-sm);
}

.jd-preview__label {
  margin: 0 0 var(--space-xs);
  font-size: var(--font-eyebrow-size);
  font-weight: var(--font-eyebrow-weight);
  letter-spacing: var(--font-eyebrow-letter);
  text-transform: uppercase;
  color: var(--color-ink-subtle);
}

.jd-preview__skills {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
}

.jd-preview__skill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background-color: var(--color-surface-1);
  border-radius: var(--rounded-md);
  font-size: var(--font-body-sm-size);
}

.jd-preview__skill-name {
  color: var(--color-ink);
  font-weight: 500;
}

.jd-preview__skill-level {
  color: var(--color-ink-subtle);
  font-size: var(--font-caption-size);
}

.jd-preview__requirements {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
}

.jd-preview__requirements li {
  padding: 2px 8px;
  background-color: var(--color-surface-3);
  border-radius: var(--rounded-pill);
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-muted);
}

.jd-preview__empty {
  margin: var(--space-sm) 0 0;
  color: var(--color-ink-subtle);
  font-size: var(--font-body-sm-size);
}
</style>
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd frontend && npm test -- --run tests/components/JdPreviewCard.test.ts`
Expected: 3 passed

- [ ] **Step 5: 提交**

```bash
git add frontend/src/components/preview/JdPreviewCard.vue frontend/tests/components/JdPreviewCard.test.ts
git commit -m "feat: add JdPreviewCard component"
```

---

### Task 5: 简历解析预览卡片组件

**Files:**
- Create: `frontend/src/components/preview/ResumePreviewCard.vue`
- Test: `frontend/tests/components/ResumePreviewCard.test.ts`

- [ ] **Step 1: 写失败测试**

```typescript
// frontend/tests/components/ResumePreviewCard.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ResumePreviewCard from '@/components/preview/ResumePreviewCard.vue'
import type { ResumePreviewResponse } from '@/api/preview'

const mockData: ResumePreviewResponse = {
  name: '张三',
  skills: ['Python', 'SQL', 'Docker'],
  projects: [{ name: '电商平台', role: '后端开发', highlights: ['设计订单系统'] }],
  education: [{ school: '北京大学', major: '计算机科学', degree: '本科' }],
  experience_years: 3,
}

describe('ResumePreviewCard', () => {
  it('renders name and skills', () => {
    const wrapper = mount(ResumePreviewCard, {
      props: { data: mockData },
    })
    expect(wrapper.text()).toContain('张三')
    expect(wrapper.text()).toContain('Python')
  })

  it('renders projects', () => {
    const wrapper = mount(ResumePreviewCard, {
      props: { data: mockData },
    })
    expect(wrapper.text()).toContain('电商平台')
  })

  it('renders education', () => {
    const wrapper = mount(ResumePreviewCard, {
      props: { data: mockData },
    })
    expect(wrapper.text()).toContain('北京大学')
  })

  it('shows empty state when no skills', () => {
    const emptyData = { ...mockData, skills: [] }
    const wrapper = mount(ResumePreviewCard, {
      props: { data: emptyData },
    })
    expect(wrapper.text()).toContain('未提取到技能')
  })
})
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd frontend && npm test -- --run tests/components/ResumePreviewCard.test.ts`
Expected: FAIL（组件不存在）

- [ ] **Step 3: 实现 ResumePreviewCard**

```vue
<!-- frontend/src/components/preview/ResumePreviewCard.vue -->
<script setup lang="ts">
import type { ResumePreviewResponse } from '@/api/preview'

defineProps<{
  data: ResumePreviewResponse
}>()
</script>

<template>
  <section class="resume-preview" aria-label="简历解析预览">
    <header class="resume-preview__header">
      <h3 class="resume-preview__name">{{ data.name || '简历信息' }}</h3>
      <span v-if="data.experience_years > 0" class="resume-preview__years">{{ data.experience_years }}年经验</span>
    </header>

    <div v-if="data.skills.length > 0" class="resume-preview__section">
      <p class="resume-preview__label">技能</p>
      <ul class="resume-preview__tags">
        <li v-for="skill in data.skills" :key="skill" class="resume-preview__tag">{{ skill }}</li>
      </ul>
    </div>
    <p v-else class="resume-preview__empty">未提取到技能</p>

    <div v-if="data.projects.length > 0" class="resume-preview__section">
      <p class="resume-preview__label">项目经历</p>
      <ul class="resume-preview__projects">
        <li v-for="proj in data.projects" :key="proj.name" class="resume-preview__project">
          <span class="resume-preview__project-name">{{ proj.name }}</span>
          <span v-if="proj.role" class="resume-preview__project-role">{{ proj.role }}</span>
        </li>
      </ul>
    </div>

    <div v-if="data.education.length > 0" class="resume-preview__section">
      <p class="resume-preview__label">教育背景</p>
      <ul class="resume-preview__education">
        <li v-for="edu in data.education" :key="edu.school">
          {{ edu.school }} · {{ edu.major }} · {{ edu.degree }}
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.resume-preview {
  padding: var(--space-md);
  background-color: var(--color-surface-2);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
}

.resume-preview__header {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-sm);
}

.resume-preview__name {
  margin: 0;
  font-size: var(--font-body-lg-size);
  font-weight: 600;
  color: var(--color-ink);
}

.resume-preview__years {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
  background-color: var(--color-surface-3);
  padding: 2px 8px;
  border-radius: var(--rounded-pill);
}

.resume-preview__section {
  margin-top: var(--space-sm);
}

.resume-preview__label {
  margin: 0 0 var(--space-xs);
  font-size: var(--font-eyebrow-size);
  font-weight: var(--font-eyebrow-weight);
  letter-spacing: var(--font-eyebrow-letter);
  text-transform: uppercase;
  color: var(--color-ink-subtle);
}

.resume-preview__tags {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
}

.resume-preview__tag {
  padding: 4px 10px;
  background-color: var(--color-surface-1);
  border-radius: var(--rounded-md);
  font-size: var(--font-body-sm-size);
  color: var(--color-ink);
  font-weight: 500;
}

.resume-preview__projects {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.resume-preview__project {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-size: var(--font-body-sm-size);
}

.resume-preview__project-name {
  font-weight: 500;
  color: var(--color-ink);
}

.resume-preview__project-role {
  color: var(--color-ink-subtle);
}

.resume-preview__education {
  list-style: none;
  margin: 0;
  padding: 0;
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-muted);
}

.resume-preview__empty {
  margin: var(--space-sm) 0 0;
  color: var(--color-ink-subtle);
  font-size: var(--font-body-sm-size);
}
</style>
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd frontend && npm test -- --run tests/components/ResumePreviewCard.test.ts`
Expected: 4 passed

- [ ] **Step 5: 提交**

```bash
git add frontend/src/components/preview/ResumePreviewCard.vue frontend/tests/components/ResumePreviewCard.test.ts
git commit -m "feat: add ResumePreviewCard component"
```

---

### Task 6: 分步引导向导组件

**Files:**
- Create: `frontend/src/components/workbench/OnboardingWizard.vue`
- Test: `frontend/tests/components/OnboardingWizard.test.ts`
- Modify: `frontend/src/views/WorkspaceView.vue`

- [ ] **Step 1: 写失败测试**

```typescript
// frontend/tests/components/OnboardingWizard.test.ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import OnboardingWizard from '@/components/workbench/OnboardingWizard.vue'

function mountWithRouter() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/reports/:taskId', name: 'report', component: { template: '<div/>' } }],
  })
  return mount(OnboardingWizard, {
    global: { plugins: [router] },
  })
}

describe('OnboardingWizard', () => {
  it('renders step 1 by default', () => {
    const wrapper = mountWithRouter()
    expect(wrapper.text()).toContain('粘贴岗位描述')
  })

  it('has skip button', () => {
    const wrapper = mountWithRouter()
    expect(wrapper.find('[data-testid="wizard-skip"]').exists()).toBe(true)
  })

  it('emits dismiss when skip clicked', async () => {
    const wrapper = mountWithRouter()
    await wrapper.find('[data-testid="wizard-skip"]').trigger('click')
    expect(wrapper.emitted('dismiss')).toBeTruthy()
  })

  it('shows progress bar', () => {
    const wrapper = mountWithRouter()
    expect(wrapper.find('[data-testid="wizard-progress"]').exists()).toBe(true)
  })
})
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd frontend && npm test -- --run tests/components/OnboardingWizard.test.ts`
Expected: FAIL（组件不存在）

- [ ] **Step 3: 实现 OnboardingWizard**

```vue
<!-- frontend/src/components/workbench/OnboardingWizard.vue -->
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { parseJdPreview } from '@/api/preview'
import { parseResumePreview } from '@/api/preview'
import { createJob } from '@/api/jobs'
import { createResume } from '@/api/resumes'
import JdPreviewCard from '@/components/preview/JdPreviewCard.vue'
import ResumePreviewCard from '@/components/preview/ResumePreviewCard.vue'
import type { JdPreviewResponse } from '@/api/preview'
import type { ResumePreviewResponse } from '@/api/preview'

const emit = defineEmits<{
  (e: 'dismiss'): void
}>()

const router = useRouter()
const step = ref(1)
const jdText = ref('')
const resumeText = ref('')
const jdPreview = ref<JdPreviewResponse | null>(null)
const resumePreview = ref<ResumePreviewResponse | null>(null)
const parsing = ref(false)
const parseError = ref('')
const submitting = ref(false)

const STEPS = [
  { id: 1, title: '粘贴岗位描述' },
  { id: 2, title: '粘贴简历' },
  { id: 3, title: '开始分析' },
]

const progressPercent = computed(() => ((step.value - 1) / 3) * 100)

let debounceTimer: ReturnType<typeof setTimeout> | null = null

function onJdInput() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(async () => {
    if (jdText.value.length < 20) return
    parsing.value = true
    parseError.value = ''
    const res = await parseJdPreview(jdText.value)
    if (res.ok) {
      jdPreview.value = res.data
    } else {
      parseError.value = '解析未成功，请直接提交原文'
      jdPreview.value = null
    }
    parsing.value = false
  }, 800)
}

function onResumeInput() {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(async () => {
    if (resumeText.value.length < 20) return
    parsing.value = true
    parseError.value = ''
    const res = await parseResumePreview(resumeText.value)
    if (res.ok) {
      resumePreview.value = res.data
    } else {
      parseError.value = '解析未成功，请直接提交原文'
      resumePreview.value = null
    }
    parsing.value = false
  }, 800)
}

function nextStep() {
  if (step.value < 3) step.value++
}

function prevStep() {
  if (step.value > 1) step.value--
}

async function submitAndAnalyze() {
  submitting.value = true
  try {
    const jobRes = await createJob({
      title: jdPreview.value?.title || '目标岗位',
      raw_text: jdText.value,
    })
    if (!jobRes.ok) { parseError.value = '创建岗位失败'; submitting.value = false; return }

    const resumeRes = await createResume({
      candidate_name: resumePreview.value?.name || '候选人',
      version_label: 'v1',
      raw_text: resumeText.value,
    })
    if (!resumeRes.ok) { parseError.value = '创建简历失败'; submitting.value = false; return }

    router.push({ name: 'analysis-run' })
  } catch {
    parseError.value = '提交失败，请重试'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="wizard-overlay" role="dialog" aria-modal="true" aria-label="新手引导">
    <div class="wizard">
      <header class="wizard__header">
        <h2 class="wizard__title">开始你的求职成长之旅</h2>
        <button
          type="button"
          class="wizard__skip"
          data-testid="wizard-skip"
          aria-label="跳过引导"
          @click="emit('dismiss')"
        >
          跳过
        </button>
      </header>

      <div class="wizard__progress" data-testid="wizard-progress">
        <div class="wizard__progress-bar">
          <div class="wizard__progress-fill" :style="{ width: `${progressPercent}%` }" />
        </div>
        <div class="wizard__steps">
          <span
            v-for="s in STEPS"
            :key="s.id"
            class="wizard__step-indicator"
            :class="{
              'wizard__step-indicator--active': step === s.id,
              'wizard__step-indicator--done': step > s.id,
            }"
          >
            {{ s.id }}
          </span>
        </div>
      </div>

      <div class="wizard__body">
        <div v-if="step === 1" class="wizard__step">
          <h3 class="wizard__step-title">粘贴岗位描述</h3>
          <p class="wizard__step-desc">将你想申请的岗位 JD 粘贴到下方，系统会自动解析技能要求</p>
          <textarea
            v-model="jdText"
            class="wizard__textarea"
            placeholder="粘贴岗位描述..."
            rows="6"
            @input="onJdInput"
          />
          <div v-if="parsing" class="wizard__loading">解析中...</div>
          <JdPreviewCard v-if="jdPreview" :data="jdPreview" />
          <p v-if="parseError && step === 1" class="wizard__error">{{ parseError }}</p>
        </div>

        <div v-if="step === 2" class="wizard__step">
          <h3 class="wizard__step-title">粘贴简历</h3>
          <p class="wizard__step-desc">将你的简历内容粘贴到下方，系统会自动提取技能和经历</p>
          <textarea
            v-model="resumeText"
            class="wizard__textarea"
            placeholder="粘贴简历内容..."
            rows="6"
            @input="onResumeInput"
          />
          <div v-if="parsing" class="wizard__loading">解析中...</div>
          <ResumePreviewCard v-if="resumePreview" :data="resumePreview" />
          <p v-if="parseError && step === 2" class="wizard__error">{{ parseError }}</p>
        </div>

        <div v-if="step === 3" class="wizard__step">
          <h3 class="wizard__step-title">开始分析</h3>
          <p class="wizard__step-desc">系统将创建岗位和简历，并自动执行匹配分析</p>
          <p v-if="parseError" class="wizard__error">{{ parseError }}</p>
        </div>
      </div>

      <footer class="wizard__footer">
        <button
          v-if="step > 1"
          type="button"
          class="wizard__btn wizard__btn--secondary"
          @click="prevStep"
        >
          上一步
        </button>
        <button
          v-if="step < 3"
          type="button"
          class="wizard__btn wizard__btn--primary"
          :disabled="step === 1 ? jdText.length < 20 : resumeText.length < 20"
          @click="nextStep"
        >
          下一步
        </button>
        <button
          v-if="step === 3"
          type="button"
          class="wizard__btn wizard__btn--primary"
          :disabled="submitting"
          @click="submitAndAnalyze"
        >
          {{ submitting ? '提交中...' : '开始分析' }}
        </button>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.wizard-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.5);
  padding: var(--space-md);
}

.wizard {
  width: 100%;
  max-width: 560px;
  max-height: 90vh;
  overflow-y: auto;
  background-color: var(--color-surface-1);
  border-radius: var(--rounded-xl);
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
}

.wizard__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-lg);
  border-bottom: 1px solid var(--color-hairline);
}

.wizard__title {
  margin: 0;
  font-size: var(--font-headline-size);
  font-weight: var(--font-headline-weight);
  color: var(--color-ink);
}

.wizard__skip {
  background: none;
  border: none;
  color: var(--color-ink-subtle);
  font-size: var(--font-body-sm-size);
  cursor: pointer;
  padding: var(--space-xs);
}

.wizard__skip:hover {
  color: var(--color-ink);
}

.wizard__progress {
  padding: var(--space-md) var(--space-lg);
}

.wizard__progress-bar {
  width: 100%;
  height: 4px;
  background-color: var(--color-surface-3);
  border-radius: var(--rounded-pill);
  overflow: hidden;
}

.wizard__progress-fill {
  height: 100%;
  background-color: var(--color-primary);
  transition: width 0.3s var(--motion-easing-standard);
}

.wizard__steps {
  display: flex;
  justify-content: space-between;
  margin-top: var(--space-xs);
}

.wizard__step-indicator {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: var(--font-caption-size);
  font-weight: 600;
  background-color: var(--color-surface-3);
  color: var(--color-ink-subtle);
}

.wizard__step-indicator--active {
  background-color: var(--color-primary);
  color: var(--color-on-primary);
}

.wizard__step-indicator--done {
  background-color: var(--color-risk-low);
  color: #fff;
}

.wizard__body {
  flex: 1;
  padding: var(--space-lg);
}

.wizard__step-title {
  margin: 0 0 var(--space-xs);
  font-size: var(--font-body-lg-size);
  font-weight: 600;
  color: var(--color-ink);
}

.wizard__step-desc {
  margin: 0 0 var(--space-md);
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-muted);
}

.wizard__textarea {
  width: 100%;
  padding: var(--space-sm);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-md);
  font-family: var(--font-family-sans);
  font-size: var(--font-body-sm-size);
  line-height: var(--font-body-line);
  resize: vertical;
  background-color: var(--color-surface-1);
  color: var(--color-ink);
}

.wizard__textarea:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: -2px;
}

.wizard__loading {
  margin-top: var(--space-sm);
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-subtle);
}

.wizard__error {
  margin-top: var(--space-sm);
  font-size: var(--font-body-sm-size);
  color: var(--color-risk-high);
}

.wizard__footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-lg);
  border-top: 1px solid var(--color-hairline);
}

.wizard__btn {
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--rounded-md);
  font-size: var(--font-button-size);
  font-weight: var(--font-button-weight);
  cursor: pointer;
  border: none;
  transition: background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.wizard__btn--primary {
  background-color: var(--color-primary);
  color: var(--color-on-primary);
}

.wizard__btn--primary:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
}

.wizard__btn--primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.wizard__btn--secondary {
  background-color: var(--color-surface-2);
  color: var(--color-ink);
  border: 1px solid var(--color-hairline);
}

.wizard__btn--secondary:hover {
  background-color: var(--color-surface-3);
}

@media (max-width: 480px) {
  .wizard-overlay {
    padding: 0;
  }

  .wizard {
    max-width: 100%;
    max-height: 100vh;
    border-radius: 0;
  }
}
</style>
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd frontend && npm test -- --run tests/components/OnboardingWizard.test.ts`
Expected: 4 passed

- [ ] **Step 5: 修改 WorkspaceView 触发向导**

在 `frontend/src/views/WorkspaceView.vue` 中：
- 导入 `OnboardingWizard` 替代 `OnboardingGuide`
- 添加 `showWizard` ref，当无岗位且无简历时为 true
- 点击跳过后设置 `localStorage.setItem('wizard_dismissed', 'true')` 并关闭向导
- 用 `OnboardingWizard` 替换 `OnboardingGuide` 的渲染位置

- [ ] **Step 6: 运行 typecheck**

Run: `cd frontend && npm run typecheck`
Expected: 无错误

- [ ] **Step 7: 提交**

```bash
git add frontend/src/components/workbench/OnboardingWizard.vue frontend/tests/components/OnboardingWizard.test.ts frontend/src/views/WorkspaceView.vue
git commit -m "feat: add OnboardingWizard with parse preview"
```

---

## 第 2 批：B 仪表盘 + C NBA 流程

### Task 7: 通用报告卡片容器

**Files:**
- Create: `frontend/src/components/report/ReportCard.vue`

- [ ] **Step 1: 创建 ReportCard 容器**

```vue
<!-- frontend/src/components/report/ReportCard.vue -->
<script setup lang="ts">
defineProps<{
  title: string
  icon?: string
}>()

const emit = defineEmits<{
  (e: 'cta-click'): void
}>()
</script>

<template>
  <article class="report-card" role="region" :aria-label="title">
    <header class="report-card__header">
      <h3 class="report-card__title">{{ title }}</h3>
    </header>
    <div class="report-card__body">
      <slot />
    </div>
    <footer v-if="$slots.cta" class="report-card__footer">
      <slot name="cta" />
    </footer>
  </article>
</template>

<style scoped>
.report-card {
  display: flex;
  flex-direction: column;
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.report-card__header {
  padding: var(--space-sm) var(--space-md);
  border-bottom: 1px solid var(--color-hairline);
}

.report-card__title {
  margin: 0;
  font-size: var(--font-body-sm-size);
  font-weight: 600;
  color: var(--color-ink-subtle);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.report-card__body {
  flex: 1;
  padding: var(--space-md);
}

.report-card__footer {
  padding: var(--space-sm) var(--space-md);
  border-top: 1px solid var(--color-hairline);
}
</style>
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/components/report/ReportCard.vue
git commit -m "feat: add ReportCard container component"
```

---

### Task 8: 面包屑组件

**Files:**
- Create: `frontend/src/components/common/Breadcrumb.vue`
- Test: `frontend/tests/components/Breadcrumb.test.ts`

- [ ] **Step 1: 写失败测试**

```typescript
// frontend/tests/components/Breadcrumb.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Breadcrumb from '@/components/common/Breadcrumb.vue'

describe('Breadcrumb', () => {
  it('renders items with separator', () => {
    const wrapper = mount(Breadcrumb, {
      props: {
        items: [
          { label: '工作台', to: '/' },
          { label: '报告', to: '/reports/1' },
          { label: '面试训练' },
        ],
      },
    })
    expect(wrapper.text()).toContain('工作台')
    expect(wrapper.text()).toContain('报告')
    expect(wrapper.text()).toContain('面试训练')
  })

  it('renders last item as plain text', () => {
    const wrapper = mount(Breadcrumb, {
      props: {
        items: [
          { label: '工作台', to: '/' },
          { label: '当前页' },
        ],
      },
    })
    const links = wrapper.findAll('a')
    expect(links.length).toBe(1)
  })
})
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd frontend && npm test -- --run tests/components/Breadcrumb.test.ts`
Expected: FAIL

- [ ] **Step 3: 实现 Breadcrumb**

```vue
<!-- frontend/src/components/common/Breadcrumb.vue -->
<script setup lang="ts">
import { RouterLink } from 'vue-router'

interface BreadcrumbItem {
  label: string
  to?: string
}

defineProps<{
  items: BreadcrumbItem[]
}>()
</script>

<template>
  <nav class="breadcrumb" aria-label="面包屑导航">
    <ol class="breadcrumb__list">
      <li v-for="(item, i) in items" :key="i" class="breadcrumb__item">
        <span v-if="i > 0" class="breadcrumb__sep" aria-hidden="true">/</span>
        <RouterLink v-if="item.to" :to="item.to" class="breadcrumb__link">
          {{ item.label }}
        </RouterLink>
        <span v-else class="breadcrumb__current" aria-current="page">{{ item.label }}</span>
      </li>
    </ol>
  </nav>
</template>

<style scoped>
.breadcrumb__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-size: var(--font-body-sm-size);
}

.breadcrumb__item {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.breadcrumb__sep {
  color: var(--color-ink-tertiary);
}

.breadcrumb__link {
  color: var(--color-ink-subtle);
  text-decoration: none;
}

.breadcrumb__link:hover {
  color: var(--color-primary);
}

.breadcrumb__current {
  color: var(--color-ink);
  font-weight: 500;
}
</style>
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd frontend && npm test -- --run tests/components/Breadcrumb.test.ts`
Expected: 2 passed

- [ ] **Step 5: 提交**

```bash
git add frontend/src/components/common/Breadcrumb.vue frontend/tests/components/Breadcrumb.test.ts
git commit -m "feat: add Breadcrumb component"
```

---

### Task 9: NBA 横幅组件

**Files:**
- Create: `frontend/src/components/common/NbaBanner.vue`

- [ ] **Step 1: 创建 NbaBanner**

```vue
<!-- frontend/src/components/common/NbaBanner.vue -->
<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { Sparkles } from 'lucide-vue-next'

defineProps<{
  label: string
  description?: string
  ctaTo?: string
  ctaLabel?: string
}>()

const emit = defineEmits<{
  (e: 'cta-click'): void
}>()
</script>

<template>
  <aside class="nba-banner" role="complementary" aria-label="下一步建议">
    <Sparkles :size="16" class="nba-banner__icon" aria-hidden="true" />
    <div class="nba-banner__body">
      <p class="nba-banner__label">{{ label }}</p>
      <p v-if="description" class="nba-banner__desc">{{ description }}</p>
    </div>
    <RouterLink
      v-if="ctaTo"
      :to="ctaTo"
      class="nba-banner__cta"
    >
      {{ ctaLabel || '前往' }}
    </RouterLink>
    <button
      v-else
      type="button"
      class="nba-banner__cta"
      @click="emit('cta-click')"
    >
      {{ ctaLabel || '继续' }}
    </button>
  </aside>
</template>

<style scoped>
.nba-banner {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  margin-top: var(--space-lg);
  background-color: rgba(107, 117, 224, 0.08);
  border: 1px solid rgba(107, 117, 224, 0.2);
  border-radius: var(--rounded-md);
}

.nba-banner__icon {
  flex-shrink: 0;
  color: var(--color-primary);
}

.nba-banner__body {
  flex: 1;
}

.nba-banner__label {
  margin: 0;
  font-size: var(--font-body-sm-size);
  font-weight: 500;
  color: var(--color-ink);
}

.nba-banner__desc {
  margin: 2px 0 0;
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

.nba-banner__cta {
  flex-shrink: 0;
  padding: 6px 12px;
  background-color: var(--color-primary);
  color: var(--color-on-primary);
  border: none;
  border-radius: var(--rounded-md);
  font-size: var(--font-button-size);
  font-weight: var(--font-button-weight);
  text-decoration: none;
  cursor: pointer;
  transition: background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.nba-banner__cta:hover {
  background-color: var(--color-primary-hover);
}
</style>
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/components/common/NbaBanner.vue
git commit -m "feat: add NbaBanner component"
```

---

### Task 10: 报告页仪表盘重构

**Files:**
- Create: `frontend/src/components/report/ReportDashboard.vue`
- Modify: `frontend/src/views/ReportView.vue`

- [ ] **Step 1: 创建 ReportDashboard**

```vue
<!-- frontend/src/components/report/ReportDashboard.vue -->
<script setup lang="ts">
import type { Report } from '@/api/reports'
import type { AgentRun } from '@/api/agentRuns'
import ReportCard from './ReportCard.vue'
import ScoringOverviewCard from './ScoringOverviewCard.vue'
import SkillsRadarChart from './SkillsRadarChart.vue'
import NextBestActionCallout from '@/components/workbench/NextBestActionCallout.vue'
import CapabilityGapCard from './CapabilityGapCard.vue'
import SuggestionCard from './SuggestionCard.vue'
import InterviewQuestionCard from './InterviewQuestionCard.vue'
import EvidenceChainTable from './EvidenceChainTable.vue'
import AgentTraceTimeline from './AgentTraceTimeline.vue'
import Breadcrumb from '@/components/common/Breadcrumb.vue'

const props = defineProps<{
  report: Report
  agentRun: AgentRun | null
}>()

const emit = defineEmits<{
  (e: 'start-interview'): void
  (e: 'start-learning'): void
  (e: 'optimize-resume'): void
}>()
</script>

<template>
  <div class="dashboard">
    <Breadcrumb :items="[{ label: '工作台', to: '/' }, { label: '报告' }]" />

    <div class="dashboard__grid">
      <ReportCard title="总分">
        <ScoringOverviewCard :score="report.totalScore" :dimensions="report.scoreItems" />
      </ReportCard>

      <ReportCard title="技能雷达">
        <SkillsRadarChart :dimensions="report.scoreItems" />
      </ReportCard>

      <ReportCard title="下一步建议">
        <NextBestActionCallout
          :state="report.nextBestAction ? 'ready' : 'empty'"
          :headline="report.nextBestAction?.headline || ''"
          :action-label="report.nextBestAction?.actionLabel || ''"
          :cta-to="report.nextBestAction?.targetRoute || ''"
          @action="emit('start-interview')"
        />
      </ReportCard>

      <ReportCard title="能力缺口">
        <CapabilityGapCard :gaps="report.gaps" />
      </ReportCard>

      <ReportCard title="简历建议">
        <SuggestionCard :suggestions="report.resumeSuggestions" />
      </ReportCard>

      <ReportCard title="面试题">
        <InterviewQuestionCard :questions="report.interviewQuestions" />
        <template #cta>
          <button type="button" class="dashboard__card-cta" @click="emit('start-interview')">
            开始面试训练
          </button>
        </template>
      </ReportCard>
    </div>

    <details class="dashboard__details">
      <summary class="dashboard__details-summary">证据链详情</summary>
      <EvidenceChainTable :items="report.evidenceChain" />
    </details>

    <details v-if="agentRun" class="dashboard__details">
      <summary class="dashboard__details-summary">Agent 执行轨迹</summary>
      <AgentTraceTimeline :nodes="agentRun.nodes" />
    </details>
  </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.dashboard__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-md);
}

@media (max-width: 1024px) {
  .dashboard__grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .dashboard__grid {
    grid-template-columns: 1fr;
  }
}

.dashboard__card-cta {
  width: 100%;
  padding: var(--space-sm);
  background-color: var(--color-primary);
  color: var(--color-on-primary);
  border: none;
  border-radius: var(--rounded-md);
  font-size: var(--font-button-size);
  font-weight: var(--font-button-weight);
  cursor: pointer;
  transition: background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.dashboard__card-cta:hover {
  background-color: var(--color-primary-hover);
}

.dashboard__details {
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-md);
  overflow: hidden;
}

.dashboard__details-summary {
  padding: var(--space-sm) var(--space-md);
  background-color: var(--color-surface-2);
  cursor: pointer;
  font-size: var(--font-body-sm-size);
  font-weight: 500;
  color: var(--color-ink-muted);
  list-style: none;
}

.dashboard__details-summary::before {
  content: '▶ ';
  font-size: 10px;
}

.dashboard__details[open] .dashboard__details-summary::before {
  content: '▼ ';
}
</style>
```

- [ ] **Step 2: 重构 ReportView 使用 ReportDashboard**

在 `frontend/src/views/ReportView.vue` 中：
- 导入 `ReportDashboard` 替代原有纵向堆叠布局
- 传递 `report` 和 `agentRun` props
- 处理 `start-interview`、`start-learning`、`optimize-resume` 事件
- 添加导出按钮和返回工作台链接

- [ ] **Step 3: 运行 typecheck**

Run: `cd frontend && npm run typecheck`
Expected: 无错误

- [ ] **Step 4: 提交**

```bash
git add frontend/src/components/report/ReportDashboard.vue frontend/src/views/ReportView.vue
git commit -m "feat: refactor report page to dashboard layout"
```

---

### Task 11: 各页面 NBA 横幅集成

**Files:**
- Modify: `frontend/src/views/LearningTasksView.vue`
- Modify: `frontend/src/views/InterviewDetailView.vue`
- Modify: `frontend/src/views/ResumesView.vue`

- [ ] **Step 1: 在 LearningTasksView 底部添加 NBA 横幅**

在 `frontend/src/views/LearningTasksView.vue` 模板底部添加：

```vue
<NbaBanner
  label="学习任务完成，建议创建新简历版本"
  description="基于学习成果更新简历，再进行一次匹配分析"
  cta-to="/resumes"
  cta-label="创建新简历"
/>
```

- [ ] **Step 2: 在 InterviewDetailView 底部添加 NBA 横幅**

在 `frontend/src/views/InterviewDetailView.vue` 模板底部添加：

```vue
<NbaBanner
  label="面试训练完成，查看学习任务"
  description="针对薄弱环节进行专项学习"
  cta-to="/learning"
  cta-label="查看学习任务"
/>
```

- [ ] **Step 3: 在 ResumesView 创建成功后添加 NBA 横幅**

在 `frontend/src/views/ResumesView.vue` 中，简历创建成功后显示条件性 NBA 横幅：

```vue
<NbaBanner
  v-if="showNbaBanner"
  label="新简历已创建，建议重新分析"
  cta-to="/analyses/new"
  cta-label="开始分析"
/>
```

- [ ] **Step 4: 运行 typecheck**

Run: `cd frontend && npm run typecheck`
Expected: 无错误

- [ ] **Step 5: 提交**

```bash
git add frontend/src/views/LearningTasksView.vue frontend/src/views/InterviewDetailView.vue frontend/src/views/ResumesView.vue
git commit -m "feat: add NBA banners to learning, interview, and resume pages"
```

---

## 第 3 批：A 导航精简

### Task 12: 面试 Tab 容器视图

**Files:**
- Create: `frontend/src/views/InterviewView.vue`

- [ ] **Step 1: 创建 InterviewView**

```vue
<!-- frontend/src/views/InterviewView.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import LearningTasksView from './LearningTasksView.vue'
import InterviewListView from './InterviewListView.vue'
import InterviewBankView from './InterviewBankView.vue'

const route = useRoute()
const router = useRouter()

const TABS = [
  { key: 'learning', label: '学习任务' },
  { key: 'training', label: '模拟面试' },
  { key: 'bank', label: '题目生成' },
] as const

type TabKey = typeof TABS[number]['key']

const activeTab = computed<TabKey>(() => {
  const tab = route.query.tab as string
  if (tab === 'learning' || tab === 'training' || tab === 'bank') return tab
  return 'learning'
})

function switchTab(key: TabKey) {
  router.replace({ query: { ...route.query, tab: key } })
}
</script>

<template>
  <div class="interview-view">
    <header class="interview-view__tabs" role="tablist">
      <button
        v-for="tab in TABS"
        :key="tab.key"
        role="tab"
        :aria-selected="activeTab === tab.key"
        :class="[
          'interview-view__tab',
          { 'interview-view__tab--active': activeTab === tab.key },
        ]"
        @click="switchTab(tab.key)"
      >
        {{ tab.label }}
      </button>
    </header>

    <div class="interview-view__content" role="tabpanel">
      <LearningTasksView v-if="activeTab === 'learning'" />
      <InterviewListView v-if="activeTab === 'training'" />
      <InterviewBankView v-if="activeTab === 'bank'" />
    </div>
  </div>
</template>

<style scoped>
.interview-view__tabs {
  display: flex;
  gap: 0;
  border-bottom: 2px solid var(--color-hairline);
  margin-bottom: var(--space-lg);
}

.interview-view__tab {
  padding: var(--space-sm) var(--space-lg);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  font-size: var(--font-body-size);
  font-weight: 500;
  color: var(--color-ink-muted);
  cursor: pointer;
  transition: all var(--motion-duration-fast) var(--motion-easing-standard);
}

.interview-view__tab:hover {
  color: var(--color-ink);
  background-color: var(--color-surface-2);
}

.interview-view__tab--active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}
</style>
```

- [x] **Step 2: 提交**

```bash
git add frontend/src/views/InterviewView.vue
git commit -m "feat: add InterviewView with tab container"
```

---

### Task 13: 路由和导航更新

**Files:**
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/components/layout/SideNav.vue`

- [x] **Step 1: 更新路由**

在 `frontend/src/router/index.ts` 中：
- 导入 `InterviewView`
- 新增路由 `{ path: '/interview', name: 'interview', component: InterviewView }`
- 将旧路由 `/learning`、`/interview`（原 interview-list）、`/interview-bank` 改为重定向：

```typescript
{ path: '/learning', redirect: '/interview?tab=learning' },
{ path: '/interview-prep', redirect: '/interview?tab=learning' },
{ path: '/interview-bank', redirect: '/interview?tab=bank' },
```

- 保留 `/interview/:id` 路由不变（面试详情页）

- [ ] **Step 2: 更新 SideNav 导航项**

在 `frontend/src/components/layout/SideNav.vue` 中，将 `ITEMS` 数组从 9 项改为 7 项：

```typescript
const ITEMS: NavItem[] = [
  { label: '工作台', route: '/', name: 'workspace', cap: null, group: 'core' },
  { label: '岗位', route: '/jobs', name: 'jobs', cap: 'jobs', group: 'core' },
  { label: '简历', route: '/resumes', name: 'resumes', cap: 'resumes', group: 'core' },
  { label: '历史', route: '/history', name: 'history', cap: 'reports', group: 'insights' },
  { label: '对比', route: '/diff', name: 'version-diff', cap: 'reports', group: 'insights' },
  { label: '面试', route: '/interview', name: 'interview', cap: 'interview', group: 'insights' },
  { label: '设置', route: '/settings', name: 'settings', cap: null, group: 'system' },
]
```

- [x] **Step 3: 运行 typecheck 和测试**

Run: `cd frontend && npm run typecheck`
Expected: 无错误

Run: `cd frontend && npm test -- --run`
Expected: 通过（可能需要修复因路由变更导致的测试失败）

- [ ] **Step 4: 提交**

```bash
git add frontend/src/router/index.ts frontend/src/components/layout/SideNav.vue
git commit -m "feat: merge interview nav entries and add redirects"
```

---

## 验收检查

### 第 1 批

- [ ] `cd backend && python -m pytest tests/test_preview_api.py -v` 全部通过
- [ ] `cd frontend && npm run typecheck` 无错误
- [ ] `cd frontend && npm test -- --run tests/components/OnboardingWizard.test.ts tests/components/JdPreviewCard.test.ts tests/components/ResumePreviewCard.test.ts` 全部通过

### 第 2 批

- [ ] `cd frontend && npm run typecheck` 无错误
- [ ] 报告页展示 2-3 列卡片网格
- [ ] 每个页面有面包屑导航

### 第 3 批

- [x] `cd frontend && npm run typecheck` 无错误
- [x] 侧边栏 7 项
- [x] 旧路由重定向正确
