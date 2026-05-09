<script setup lang="ts">
import type { InterviewQuestion } from '@/api/reports'

defineProps<{
  question: InterviewQuestion
}>()

const typeLabels: Record<string, string> = {
  technical: '🔧 技术题',
  behavioral: '👥 行为题',
  scenario: '💼 场景题',
  project_deep_dive: '📄 项目深挖',
}

const difficultyLabels: Record<string, string> = {
  easy: '简单',
  medium: '中等',
  hard: '困难',
}
</script>

<template>
  <article class="interview-question-card">
    <header class="interview-question-card__header">
      <span class="interview-question-card__skill">{{ question.skill }}</span>

      <div class="interview-question-card__tags">
        <span
          v-if="question.type"
          class="tag tag--type"
          :title="typeLabels[question.type] || question.type"
        >
          {{ typeLabels[question.type] || question.type }}
        </span>
        <span
          v-if="question.difficulty"
          class="tag"
          :class="`tag--${question.difficulty}`"
        >
          {{ difficultyLabels[question.difficulty] || question.difficulty }}
        </span>
        <span
          v-if="question.source"
          class="tag tag--source"
          :title="question.source === 'jd_based' ? '基于 JD 要求' : '基于简历弱点'"
        >
          {{ question.source === 'jd_based' ? '📋 JD' : '📄 简历' }}
        </span>
      </div>
    </header>

    <p class="interview-question-card__text">{{ question.question }}</p>

    <div v-if="question.purpose" class="interview-question-card__purpose">
      <span class="purpose-label">考察目的：</span>
      <span class="purpose-text">{{ question.purpose }}</span>
    </div>

    <div v-if="question.whatItTests?.length" class="interview-question-card__tests">
      <span class="tests-label">考察点：</span>
      <ul class="tests-list">
        <li v-for="(point, idx) in question.whatItTests" :key="idx">{{ point }}</li>
      </ul>
    </div>

    <div v-if="question.idealAnswerHints?.length" class="interview-question-card__hints">
      <span class="hints-label">答题提示：</span>
      <ul class="hints-list">
        <li v-for="(hint, idx) in question.idealAnswerHints" :key="idx">{{ hint }}</li>
      </ul>
    </div>
  </article>
</template>

<style scoped>
.interview-question-card {
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-md);
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  transition: box-shadow 0.2s ease;
}

.interview-question-card:hover {
  box-shadow: var(--shadow-sm);
}

.interview-question-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--space-xs);
}

.interview-question-card__skill {
  font-size: var(--font-caption-size);
  font-weight: 600;
  color: var(--color-primary);
}

.interview-question-card__tags {
  display: flex;
  gap: var(--space-xs);
  flex-wrap: wrap;
}

.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.tag--type {
  background-color: #e3f2fd;
  color: #1565c0;
}

.tag--easy {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.tag--medium {
  background-color: #fff3e0;
  color: #e65100;
}

.tag--hard {
  background-color: #fce4ec;
  color: #c62828;
}

.tag--source {
  background-color: #f3e5f5;
  color: #7b1fa2;
}

.interview-question-card__text {
  margin: 0;
  font-size: var(--font-body-size);
  color: var(--color-ink);
  line-height: var(--font-body-line);
}

.interview-question-card__purpose,
.interview-question-card__tests,
.interview-question-card__hints {
  font-size: 13px;
  line-height: 1.5;
}

.purpose-label,
.tests-label,
.hints-label {
  font-weight: 600;
  color: var(--color-dim);
}

.purpose-text {
  color: var(--color-ink);
}

.tests-list,
.hints-list {
  margin: var(--space-xs) 0 0 0;
  padding-left: var(--space-lg);
  color: var(--color-dim);
}

.tests-list li,
.hints-list li {
  margin-bottom: 2px;
}
</style>
