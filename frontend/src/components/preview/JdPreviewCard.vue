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
