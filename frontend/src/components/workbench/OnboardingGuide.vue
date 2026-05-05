<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useJobsStore } from '@/stores/jobs'
import { useResumesStore } from '@/stores/resumes'

const router = useRouter()
const jobs = useJobsStore()
const resumes = useResumesStore()

const hasJobs = computed(() => jobs.list.length > 0)
const hasResumes = computed(() => resumes.list.length > 0)

const currentStep = computed(() => {
  if (!hasJobs.value) return 1
  if (!hasResumes.value) return 2
  return 3
})

const steps = [
  { id: 1, title: '创建目标岗位', description: '粘贴你想申请的岗位 JD，系统会自动解析技能要求', action: '创建岗位', route: '/jobs' },
  { id: 2, title: '上传简历版本', description: '添加你的简历内容，系统会与岗位要求进行匹配分析', action: '创建简历', route: '/resumes' },
  { id: 3, title: '开始匹配分析', description: '选择岗位和简历，获取详细的匹配报告和改进建议', action: '开始分析', route: '/analysis-run' },
]

function goToStep(route: string) {
  router.push(route)
}
</script>

<template>
  <section class="onboarding-guide" aria-label="新手引导">
    <header class="onboarding-guide__header">
      <h2 class="onboarding-guide__title">欢迎使用 CareerFit</h2>
      <p class="onboarding-guide__subtitle">三步开始你的求职成长之旅</p>
    </header>

    <div class="onboarding-guide__steps">
      <article
        v-for="step in steps"
        :key="step.id"
        class="onboarding-step"
        :class="{
          'onboarding-step--active': currentStep === step.id,
          'onboarding-step--completed': currentStep > step.id,
        }"
      >
        <div class="onboarding-step__indicator">
          <span v-if="currentStep > step.id" class="onboarding-step__check" aria-hidden="true">✓</span>
          <span v-else class="onboarding-step__number">{{ step.id }}</span>
        </div>
        <div class="onboarding-step__content">
          <h3 class="onboarding-step__title">{{ step.title }}</h3>
          <p class="onboarding-step__description">{{ step.description }}</p>
          <button
            v-if="currentStep === step.id"
            type="button"
            class="onboarding-step__action"
            @click="goToStep(step.route)"
          >
            {{ step.action }}
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
              <path d="M6 12L10 8L6 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
      </article>
    </div>

    <div class="onboarding-guide__progress">
      <div class="onboarding-guide__progress-bar">
        <div 
          class="onboarding-guide__progress-fill" 
          :style="{ width: `${((currentStep - 1) / 3) * 100}%` }"
        />
      </div>
      <span class="onboarding-guide__progress-label">步骤 {{ currentStep }} / 3</span>
    </div>
  </section>
</template>

<style scoped>
.onboarding-guide {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  padding: var(--space-xl);
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
}

.onboarding-guide__header {
  text-align: center;
}

.onboarding-guide__title {
  margin: 0 0 var(--space-xs);
  font-size: var(--font-headline-size);
  font-weight: var(--font-headline-weight);
  line-height: var(--font-headline-line);
  color: var(--color-ink);
}

.onboarding-guide__subtitle {
  margin: 0;
  font-size: var(--font-body-size);
  color: var(--color-ink-muted);
}

.onboarding-guide__steps {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.onboarding-step {
  display: flex;
  gap: var(--space-md);
  padding: var(--space-md);
  border-radius: var(--rounded-md);
  transition: background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.onboarding-step--active {
  background-color: var(--color-surface-2);
}

.onboarding-step__indicator {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: var(--color-surface-3);
  color: var(--color-ink-muted);
  font-size: var(--font-body-sm-size);
  font-weight: 600;
  transition: all var(--motion-duration-fast) var(--motion-easing-standard);
}

.onboarding-step--active .onboarding-step__indicator {
  background-color: var(--color-primary);
  color: var(--color-on-primary);
}

.onboarding-step--completed .onboarding-step__indicator {
  background-color: var(--color-risk-low);
  color: #fff;
}

.onboarding-step__check {
  font-size: 14px;
}

.onboarding-step__content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.onboarding-step__title {
  margin: 0;
  font-size: var(--font-body-size);
  font-weight: 500;
  color: var(--color-ink);
}

.onboarding-step--completed .onboarding-step__title {
  color: var(--color-ink-muted);
}

.onboarding-step__description {
  margin: 0;
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-subtle);
}

.onboarding-step__action {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs);
  margin-top: var(--space-xs);
  padding: var(--space-sm) var(--space-md);
  background-color: var(--color-primary);
  color: var(--color-on-primary);
  border: none;
  border-radius: var(--rounded-md);
  font-size: var(--font-button-size);
  font-weight: var(--font-button-weight);
  cursor: pointer;
  transition: background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.onboarding-step__action:hover {
  background-color: var(--color-primary-hover);
}

.onboarding-guide__progress {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  align-items: center;
}

.onboarding-guide__progress-bar {
  width: 100%;
  height: 4px;
  background-color: var(--color-surface-3);
  border-radius: var(--rounded-pill);
  overflow: hidden;
}

.onboarding-guide__progress-fill {
  height: 100%;
  background-color: var(--color-primary);
  transition: width 0.3s var(--motion-easing-standard);
}

.onboarding-guide__progress-label {
  font-size: var(--font-caption-size);
  color: var(--color-ink-tertiary);
}

@media (max-width: 768px) {
  .onboarding-guide {
    padding: var(--space-lg);
  }

  .onboarding-guide__title {
    font-size: 22px;
  }
}

@media (max-width: 480px) {
  .onboarding-guide {
    padding: var(--space-md);
  }

  .onboarding-step {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-sm);
  }

  .onboarding-step__action {
    width: 100%;
    justify-content: center;
  }
}
</style>
