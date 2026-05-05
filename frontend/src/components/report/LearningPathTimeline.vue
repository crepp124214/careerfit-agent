<script setup lang="ts">
import { computed } from 'vue'
import type { LearningPlanItem } from '@/api/reports'

const props = defineProps<{
  items: LearningPlanItem[]
}>()

const hasItems = computed(() => props.items.length > 0)

function getStepNumber(index: number): number {
  return index + 1
}
</script>

<template>
  <section class="learning-timeline" aria-label="学习路径">
    <header class="learning-timeline__header">
      <h3 class="learning-timeline__title">学习路径</h3>
      <span v-if="hasItems" class="learning-timeline__count">
        {{ items.length }} 项任务
      </span>
    </header>

    <div v-if="!hasItems" class="learning-timeline__empty">
      <p>暂无学习任务</p>
      <p class="learning-timeline__empty-hint">完成分析后，系统会根据能力缺口生成学习建议。</p>
    </div>

    <ol v-else class="learning-timeline__list">
      <li
        v-for="(item, i) in items"
        :key="i"
        class="learning-timeline__item"
      >
        <div class="learning-timeline__marker">
          <span class="learning-timeline__step">{{ getStepNumber(i) }}</span>
        </div>

        <article class="learning-timeline__card">
          <header class="learning-timeline__card-header">
            <span class="learning-timeline__skill">{{ item.skill }}</span>
            <span class="learning-timeline__status">待开始</span>
          </header>

          <div class="learning-timeline__content">
            <h4 class="learning-timeline__task-title">学习任务</h4>
            <p class="learning-timeline__task">{{ item.task }}</p>
          </div>

          <div class="learning-timeline__meta">
            <span class="learning-timeline__meta-item learning-timeline__meta-item--missing">
              目标：后端未返回
            </span>
            <span class="learning-timeline__meta-item learning-timeline__meta-item--missing">
              验收标准：后端未返回
            </span>
          </div>
        </article>
      </li>
    </ol>

    <p v-if="hasItems" class="learning-timeline__disclaimer">
      学习路径基于分析结果生成，建议结合实际项目实践。
    </p>
  </section>
</template>

<style scoped>
.learning-timeline {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.learning-timeline__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-md);
}

.learning-timeline__title {
  margin: 0;
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
  line-height: var(--font-card-title-line);
  color: var(--color-ink);
}

.learning-timeline__count {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

.learning-timeline__empty {
  padding: var(--space-lg);
  text-align: center;
  color: var(--color-ink-subtle);
  font-size: var(--font-body-size);
  background-color: var(--color-surface-1);
  border: 1px dashed var(--color-hairline);
  border-radius: var(--rounded-lg);
}

.learning-timeline__empty-hint {
  margin: var(--space-sm) 0 0;
  font-size: var(--font-caption-size);
  color: var(--color-ink-muted);
}

.learning-timeline__list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.learning-timeline__item {
  display: flex;
  gap: var(--space-md);
}

.learning-timeline__marker {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.learning-timeline__step {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-primary);
  color: var(--color-on-primary);
  border-radius: 50%;
  font-size: var(--font-caption-size);
  font-weight: 600;
}

.learning-timeline__item:not(:last-child) .learning-timeline__marker::after {
  content: '';
  width: 2px;
  flex: 1;
  background-color: var(--color-hairline);
  margin-top: var(--space-xs);
  min-height: 40px;
}

.learning-timeline__card {
  flex: 1;
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  overflow: hidden;
}

.learning-timeline__card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-sm) var(--space-md);
  background-color: var(--color-surface-2);
  border-bottom: 1px solid var(--color-hairline);
}

.learning-timeline__skill {
  font-size: var(--font-caption-size);
  font-weight: 500;
  color: var(--color-primary);
}

.learning-timeline__status {
  padding: 2px 8px;
  background-color: var(--color-surface-1);
  border-radius: var(--rounded-sm);
  font-size: var(--font-caption-size);
  color: var(--color-ink-muted);
}

.learning-timeline__content {
  padding: var(--space-md);
}

.learning-timeline__task-title {
  margin: 0 0 var(--space-xs);
  font-size: var(--font-caption-size);
  font-weight: 500;
  color: var(--color-ink-subtle);
}

.learning-timeline__task {
  margin: 0;
  font-size: var(--font-body-size);
  color: var(--color-ink);
  line-height: 1.5;
}

.learning-timeline__meta {
  padding: var(--space-sm) var(--space-md);
  background-color: var(--color-surface-2);
  border-top: 1px solid var(--color-hairline);
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.learning-timeline__meta-item {
  font-size: var(--font-caption-size);
  color: var(--color-ink-muted);
}

.learning-timeline__meta-item--missing {
  color: var(--color-ink-subtle);
  font-style: italic;
}

.learning-timeline__disclaimer {
  margin: 0;
  padding: var(--space-sm);
  background-color: var(--color-surface-2);
  border-radius: var(--rounded-sm);
  font-size: var(--font-caption-size);
  color: var(--color-ink-muted);
  text-align: center;
}

@media (max-width: 768px) {
  .learning-timeline__header {
    flex-direction: column;
    align-items: flex-start;
  }

  .learning-timeline__marker {
    display: none;
  }

  .learning-timeline__item {
    gap: 0;
  }
}
</style>
