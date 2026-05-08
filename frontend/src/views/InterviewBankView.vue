<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppButton from '@/components/common/AppButton.vue'
import { requestJson } from '@/api/client'

const route = useRoute()

const form = reactive({
  sourceType: 'manual' as 'manual' | 'report_reference',
  targetJob: '',
  skills: [] as string[],
  jdContext: '',
  resumeContext: '',
  questionTypes: ['technical', 'behavioral', 'scenario', 'project_deep_dive'],
  difficulty: 'mixed' as 'easy' | 'medium' | 'hard' | 'mixed',
  count: 10,
  sourceReportId: '' as string,
})

// UI 状态
const loading = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('')
const questions = ref<any[]>([])
const selectedIds = ref<number[]>([])
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const newSkill = ref('')

let progressTimer: ReturnType<typeof setInterval> | null = null

function startProgressTimer(estimatedSeconds: number) {
  loadingProgress.value = 0
  loadingMessage.value = '正在连接 AI 服务...'
  const step = 100 / (estimatedSeconds * 4)
  let phase = 0

  progressTimer = setInterval(() => {
    if (loadingProgress.value < 90) {
      loadingProgress.value = Math.min(90, loadingProgress.value + step)
    }
    phase++
    if (phase === 4) loadingMessage.value = 'AI 正在分析岗位要求...'
    if (phase === 12) loadingMessage.value = 'AI 正在生成面试题...'
    if (phase === 20) loadingMessage.value = 'AI 正在优化题目质量...'
    if (phase >= 28) loadingMessage.value = '即将完成，请稍候...'
  }, 250)
}

function stopProgressTimer() {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
  loadingProgress.value = 100
}

onMounted(async () => {
  if (route.query.source === 'analysis_report' && route.query.report_id) {
    form.sourceType = 'report_reference'
    form.sourceReportId = route.query.report_id as string
    successMessage.value = '✅ 已关联分析报告，将自动提取上下文'
  }
})

// 切换题型
function toggleQuestionType(type: string) {
  const idx = form.questionTypes.indexOf(type as any)
  if (idx > -1) {
    form.questionTypes.splice(idx, 1)
  } else {
    form.questionTypes.push(type as any)
  }
}

// 切换题目选中
function toggleSelect(id: number) {
  const idx = selectedIds.value.indexOf(id)
  if (idx > -1) {
    selectedIds.value.splice(idx, 1)
  } else {
    selectedIds.value.push(id)
  }
}

// 生成面试题
async function generateQuestions() {
  loading.value = true
  error.value = null
  successMessage.value = null
  startProgressTimer(40)

  try {
    const payload: any = {
      skills: form.skills,
      target_job: form.targetJob,
      question_types: form.questionTypes,
      difficulty: form.difficulty,
      count: form.count,
    }

    if (form.sourceType === 'report_reference' && form.sourceReportId) {
      payload.source_report_id = parseInt(form.sourceReportId)
    } else {
      payload.jd_context = form.jdContext
      payload.resume_context = form.resumeContext
    }

    loadingMessage.value = '正在调用 AI 生成面试题...'

    const res = await requestJson<any>('/interview/questions/generate', {
      method: 'POST',
      body: JSON.stringify(payload),
    })

    if (!res.ok) {
      throw new Error(res.detail || res.message || `请求失败`)
    }

    const data = res.data
    stopProgressTimer()

    if (data.success && data.data?.questions) {
      questions.value = data.data.questions
      const mode = data.data.metadata?.mode || 'unknown'
      successMessage.value = `成功生成 ${data.data.questions.length} 道面试题 (模式: ${mode})`
    } else {
      throw new Error('返回格式异常')
    }

  } catch (e: any) {
    stopProgressTimer()
    error.value = e.message || '生成失败，请重试'
  } finally {
    loading.value = false
  }
}

// 生成准备计划
async function generatePrepPlan() {
  if (selectedIds.value.length === 0) {
    error.value = '请先选择至少一道题目'
    return
  }
  
  loading.value = true
  error.value = null
  
  try {
    const selectedQuestions = questions.value.filter(q => selectedIds.value.includes(q.id))
    
    const res = await requestJson<any>('/interview/prep-plan/generate', {
      method: 'POST',
      body: JSON.stringify({
        selected_questions: selectedQuestions,
        prep_depth: 'standard',
      }),
    })
    
    if (!res.ok) {
      throw new Error(res.detail || res.message || `请求失败`)
    }
    
    const data = res.data
    
    if (data.success && data.data?.prep_plans) {
      successMessage.value = `✅ 为 ${selectedIds.value.length} 道题生成了准备计划`
    } else {
      throw new Error('返回格式异常')
    }
    
  } catch (e: any) {
    error.value = e.message || '生成准备计划失败'
  } finally {
    loading.value = false
  }
}

// 添加技能
function addSkill(skill: string) {
  if (skill && !form.skills.includes(skill)) {
    form.skills.push(skill)
  }
}

// 移除技能
function removeSkill(skill: string) {
  const idx = form.skills.indexOf(skill)
  if (idx > -1) {
    form.skills.splice(idx, 1)
  }
}
</script>

<template>
  <div class="interview-bank">
    <!-- 页面标题 -->
    <header class="interview-bank__header">
      <h1 class="interview-bank__title">🎯 面试题库</h1>
      <p class="interview-bank__subtitle">
        自定义生成针对性面试题，支持基于 JD 和简历的双数据源策略
      </p>
      
      <!-- 成功/错误提示 -->
      <div v-if="successMessage" class="alert alert--success">
        {{ successMessage }}
      </div>
      <div v-if="error" class="alert alert--error">
        {{ error }}
        <button @click="error = null" class="alert__close">×</button>
      </div>

      <!-- 进度条 -->
      <div v-if="loading" class="progress-container">
        <div class="progress-bar">
          <div
            class="progress-bar__fill"
            :style="{ width: loadingProgress + '%' }"
          ></div>
        </div>
        <p class="progress-message">{{ loadingMessage }}</p>
        <p class="progress-hint">预计需要 30-60 秒，请耐心等待</p>
      </div>
    </header>

    <!-- 配置区域 -->
    <section class="interview-bank__config">
      <h2 class="config-section__title">📥 输入配置</h2>
      
      <!-- 来源选择 -->
      <div class="form-group">
        <label class="form-label">数据来源</label>
        <div class="radio-group">
          <label class="radio-option">
            <input 
              type="radio" 
              v-model="form.sourceType" 
              value="manual"
              class="radio-input"
            >
            <span class="radio-label">手动输入</span>
          </label>
          
          <label class="radio-option radio-option--primary">
            <input 
              type="radio" 
              v-model="form.sourceType" 
              value="report_reference"
              class="radio-input"
            >
            <span class="radio-label">
              从分析报告引用
              <span class="badge-tag badge-tag--success">推荐</span>
            </span>
          </label>
        </div>
      </div>

      <!-- 目标岗位 -->
      <div class="form-group">
        <label class="form-label">目标岗位</label>
        <input 
          v-model="form.targetJob"
          type="text" 
          class="form-input"
          placeholder="例如：数据分析师、后端开发工程师"
        />
      </div>

      <!-- 技能选择 -->
      <div class="form-group">
        <label class="form-label">
          目标技能 
          <span class="form-hint">（已选 {{ form.skills.length }} 项）</span>
        </label>
        
        <div class="skill-tags">
          <span 
            v-for="skill in form.skills" 
            :key="skill" 
            class="tag tag--removable"
            @click="removeSkill(skill)"
          >
            {{ skill }} ×
          </span>
        </div>
        
        <div class="skill-input-wrapper">
          <input 
            v-model="newSkill"
            type="text" 
            class="form-input form-input--inline"
            placeholder="输入技能后回车添加..."
            @keyup.enter="addSkill(newSkill); newSkill = ''"
          />
        </div>
      </div>

      <!-- JD 内容 -->
      <div class="form-group">
        <label class="form-label">
          📋 JD 岗位描述
          <span class="form-hint">用于生成技术/行为/场景题</span>
        </label>
        <textarea 
          v-model="form.jdContext"
          class="form-textarea"
          rows="4"
          placeholder="粘贴岗位要求（JD）内容...&#10;例如：&#10;岗位职责：&#10;1. 负责数据分析&#10;2. 搭建 A/B 实验框架&#10;3. 数据可视化报表"
        ></textarea>
      </div>

      <!-- 简历内容 -->
      <div class="form-group">
        <label class="form-label">
          📝 简历 / 项目经历
          <span class="form-hint">用于生成项目深挖题 ⭐</span>
        </label>
        <textarea 
          v-model="form.resumeContext"
          class="form-textarea"
          rows="4"
          placeholder="粘贴简历或项目经历...&#10;例如：&#10;项目经历：&#10;XX公司 | 数据分析师 | 2023-2024&#10;- 使用 Python + Pandas 处理 50GB 用户行为数据&#10;- 搭建自动化 ETL 流程"
        ></textarea>
      </div>

      <!-- 题型选择 -->
      <div class="form-group">
        <label class="form-label">题型筛选（可多选）</label>
        <div class="checkbox-group">
          <label 
            v-for="type in ['technical', 'behavioral', 'scenario', 'project_deep_dive']" 
            :key="type"
            class="checkbox-option"
          >
            <input 
              type="checkbox"
              :checked="form.questionTypes.includes(type)"
              @change="toggleQuestionType(type)"
              class="checkbox-input"
            >
            <span class="checkbox-label">
              {{ type === 'technical' ? '🔧 技术题' : '' }}
              {{ type === 'behavioral' ? '👥 行为题' : '' }}
              {{ type === 'scenario' ? '💼 场景题' : '' }}
              {{ type === 'project_deep_dive' ? '📄 项目深挖题 ⭐' : '' }}
            </span>
          </label>
        </div>
      </div>

      <!-- 难度和数量 -->
      <div class="form-row">
        <div class="form-group form-group--flex-1">
          <label class="form-label">难度</label>
          <select v-model="form.difficulty" class="form-select">
            <option value="easy">简单</option>
            <option value="medium">中等</option>
            <option value="hard">困难</option>
            <option value="mixed">混合</option>
          </select>
        </div>
        
        <div class="form-group form-group--flex-1">
          <label class="form-label">数量</label>
          <input 
            v-model.number="form.count"
            type="number" 
            min="3" 
            max="20"
            class="form-input"
          />
        </div>
      </div>

      <!-- 生成按钮 -->
      <div class="form-actions">
        <AppButton
          variant="primary"
          size="lg"
          :loading="loading"
          :disabled="form.skills.length === 0"
          @click="generateQuestions"
        >
          🚀 {{ loading ? '生成中...' : '生成面试题' }}
        </AppButton>
      </div>
    </section>

    <!-- 结果区域 -->
    <section v-if="questions.length > 0" class="interview-bank__results">
      <h2 class="results-section__title">
        生成的面试题 ({{ questions.length }} 道)
        <span class="results-section__actions">
          全选 | 取消全选
        </span>
      </h2>

      <!-- 题目列表 -->
      <div class="question-list">
        <article 
          v-for="q in questions" 
          :key="q.id"
          class="question-card"
          :class="[`question-card--${q.type}`, `question-card--${q.source || 'unknown'}`]"
        >
          <header class="question-card__header">
            <span class="question-number">Q{{ q.id }}</span>
            
            <!-- 类型标签 -->
            <span class="badge badge--type">{{ q.category || q.type }}</span>
            
            <!-- 难度标签 -->
            <span :class="['badge', 'badge--difficulty', `badge--${q.difficulty}`]">
              {{ q.difficulty }}
            </span>
            
            <!-- 来源标记 -->
            <span v-if="q.source" class="source-tag" :title="'数据源: ' + q.source">
              {{ q.source === 'jd_based' ? '📋 JD' : q.source === 'resume_based' ? '📄 简历' : '?' }}
            </span>
            
            <!-- 选择框 -->
            <label class="checkbox-wrapper">
              <input 
                type="checkbox"
                :checked="selectedIds.includes(q.id)"
                @change="toggleSelect(q.id)"
                class="checkbox-input"
              >
              <span class="checkbox-label">选择此题</span>
            </label>
          </header>

          <div class="question-card__body">
            <p class="question-text">{{ q.question }}</p>
            
            <!-- 考察点提示 -->
            <div v-if="q.what_it_tests?.length" class="question-meta">
              <h4 class="meta-title">💡 考察点：</h4>
              <ul class="meta-list">
                <li v-for="(point, idx) in q.what_it_tests" :key="idx">{{ point }}</li>
              </ul>
            </div>
          </div>
        </article>
      </div>

      <!-- 批量操作栏 -->
      <div v-if="selectedIds.length > 0" class="action-bar action-bar--visible">
        <span class="action-bar__info">
          已选择 <strong>{{ selectedIds.length }}</strong> 道题
        </span>
        
        <AppButton
          variant="primary"
          :loading="loading"
          @click="generatePrepPlan"
        >
          📖 为选中题目生成准备计划
        </AppButton>
      </div>
    </section>

    <!-- 空状态 -->
    <section v-else class="interview-bank__empty">
      <div class="empty-state">
        <div class="empty-state__icon">📝</div>
        <h3 class="empty-state__title">尚未生成面试题</h3>
        <p class="empty-state__description">
          配置上方参数后点击"生成面试题"<br>
          支持<strong>基于 JD 的技术/行为/场景题</strong>和<strong>基于简历的项目深挖题</strong>
        </p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.interview-bank {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-lg);
}

/* Header */
.interview-bank__header {
  margin-bottom: var(--space-xl);
}

.interview-bank__title {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-ink);
  margin: 0 0 var(--space-sm) 0;
}

.interview-bank__subtitle {
  font-size: 14px;
  color: var(--color-dim);
  margin: 0;
}

/* Alert */
.alert {
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--rounded-md);
  margin-bottom: var(--space-md);
}

/* Progress */
.progress-container {
  margin: var(--space-lg) 0;
  padding: var(--space-lg);
  background: var(--color-surface, #f8fafc);
  border-radius: var(--rounded-lg, 12px);
  border: 1px solid var(--color-border, #e2e8f0);
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--color-border, #e2e8f0);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: var(--space-sm);
}

.progress-bar__fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-message {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-ink, #1e293b);
  margin: 0 0 4px 0;
}

.progress-hint {
  font-size: 12px;
  color: var(--color-dim, #94a3b8);
  margin: 0;
}

.alert {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.alert--success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.alert--error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.alert__close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 0 8px;
  color: inherit;
}

/* Config Section */
.interview-bank__config {
  background: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  padding: var(--space-lg);
  margin-bottom: var(--space-xl);
}

.config-section__title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 var(--space-lg) 0;
  color: var(--color-ink);
}

/* Form */
.form-group {
  margin-bottom: var(--space-md);
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-ink);
  margin-bottom: var(--space-xs);
}

.form-hint {
  font-weight: 400;
  color: var(--color-dim);
  font-size: 13px;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-md);
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
  line-height: 1.5;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-md);
}

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}

.form-actions {
  margin-top: var(--space-lg);
  padding-top: var(--space-md);
  border-top: 1px solid var(--color-hairline);
}

/* Radio & Checkbox */
.radio-group,
.checkbox-group {
  display: flex;
  gap: var(--space-md);
  flex-wrap: wrap;
}

.radio-option,
.checkbox-option {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  cursor: pointer;
  padding: var(--space-sm) var(--space-md);
  border: 2px solid var(--color-hairline);
  border-radius: var(--rounded-md);
  transition: all 0.2s;
}

.radio-option:hover,
.checkbox-option:hover,
.radio-option:has(:checked),
.checkbox-option:has(:checked) {
  border-color: var(--color-primary);
  background-color: var(--color-surface-2);
}

.radio-option--primary {
  border-color: var(--color-primary);
  background-color: rgba(var(--color-primary-rgb), 0.05);
}

.radio-input,
.checkbox-input {
  width: 18px;
  height: 18px;
  accent-color: var(--color-primary);
  cursor: pointer;
}

.radio-label,
.checkbox-label {
  font-size: 14px;
  font-weight: 500;
  user-select: none;
}

/* Tags */
.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
  margin-bottom: var(--space-sm);
}

.tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  background-color: var(--color-surface-2);
  border: 1px solid var(--color-hairline);
  border-radius: 20px;
  font-size: 13px;
  cursor: default;
}

.tag--removable {
  cursor: pointer;
  color: var(--color-danger);
}

.tag--removable:hover {
  background-color: var(--color-danger-surface);
  border-color: var(--color-danger);
}

/* Badge */
.badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge--type {
  background-color: #e3f2fd;
  color: #1565c0;
}

.badge--difficulty {
  background-color: #fff3e0;
  color: #e65100;
}

.badge--easy {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.badge--hard {
  background-color: #fce4ec;
  color: #c62828;
}

.source-tag {
  font-size: 12px;
  opacity: 0.8;
}

/* Question Card */
.question-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.question-card {
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  overflow: hidden;
  transition: box-shadow 0.2s, transform 0.2s;
}

.question-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.question-card--selected {
  border-color: var(--color-primary);
  background-color: rgba(var(--color-primary-rgb), 0.02);
}

.question-card__header {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md);
  background-color: var(--color-surface-1);
  border-bottom: 1px solid var(--color-hairline);
  flex-wrap: wrap;
}

.question-number {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-primary);
}

.question-card__body {
  padding: var(--space-md);
}

.question-text {
  font-size: 15px;
  line-height: 1.6;
  color: var(--color-ink);
  margin: 0 0 var(--space-md) 0;
}

.question-meta {
  margin-top: var(--space-md);
  padding: var(--space-sm);
  background-color: var(--color-surface-1);
  border-radius: var(--rounded-md);
}

.meta-title {
  font-size: 13px;
  font-weight: 600;
  margin: 0 0 var(--space-xs) 0;
  color: var(--color-dim);
}

.meta-list {
  margin: 0;
  padding-left: var(--space-lg);
}

.meta-list li {
  font-size: 13px;
  line-height: 1.5;
  color: var(--color-dim);
  margin-bottom: var(--space-xs);
}

.checkbox-wrapper {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  cursor: pointer;
}

/* Action Bar */
.action-bar {
  position: sticky;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  max-width: 90%;
  padding: var(--space-md) var(--space-lg);
  background-color: white;
  border: 2px solid var(--color-primary);
  border-radius: var(--rounded-full);
  box-shadow: var(--shadow-lg);
  display: flex;
  align-items: center;
  justify-content: space-between;
  animation: slideUp 0.3s ease-out;
}

.action-bar--visible {
  display: flex;
}

.action-bar__info {
  font-size: 14px;
  color: var(--color-dim);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

/* Empty State */
.interview-bank__empty {
  text-align: center;
  padding: var(--space-xxl) var(--space-md);
}

.empty-state__icon {
  font-size: 64px;
  margin-bottom: var(--space-md);
}

.empty-state__title {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-ink);
  margin: 0 0 var(--space-sm) 0;
}

.empty-state__description {
  font-size: 14px;
  color: var(--color-dim);
  line-height: 1.6;
  margin: 0;
}

.empty-state__description strong {
  color: var(--color-primary);
}
</style>
