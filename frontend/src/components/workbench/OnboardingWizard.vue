<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { parseJdPreview, parseResumePreview } from '@/api/preview'
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
  parseError.value = ''
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
