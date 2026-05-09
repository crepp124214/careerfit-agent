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
