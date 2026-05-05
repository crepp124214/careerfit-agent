<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Evidence } from '@/api/reports'
import StatusBadge from '@/components/common/StatusBadge.vue'

const props = defineProps<{
  evidence: Evidence
}>()

const MAX_LENGTH = 200
const expanded = ref(false)

function truncate(text: string) {
  if (text.length <= MAX_LENGTH) return text
  return text.slice(0, MAX_LENGTH) + '…'
}

const jdDisplay = computed(() => {
  const excerpt = props.evidence.jdExcerpt
  if (!excerpt) return null
  return expanded.value ? excerpt : truncate(excerpt)
})

const resumeDisplay = computed(() => {
  const excerpt = props.evidence.resumeExcerpt
  if (!excerpt) return null
  return expanded.value ? excerpt : truncate(excerpt)
})

const needsExpand = computed(() => {
  const jd = props.evidence.jdExcerpt
  const resume = props.evidence.resumeExcerpt
  return jd.length > MAX_LENGTH || resume.length > MAX_LENGTH
})

const hasKnowledgeEvidence = computed(() => {
  const ke = props.evidence.knowledgeEvidence
  return ke && ke.length > 0
})

function toggle() {
  expanded.value = !expanded.value
}
</script>

<template>
  <article class="evidence-card">
    <div class="evidence-card__header">
      <StatusBadge tone="neutral">{{ evidence.dimensionName }}</StatusBadge>
    </div>

    <div class="evidence-card__columns">
      <div class="evidence-card__column">
        <span class="evidence-card__label">JD 证据</span>
        <pre v-if="jdDisplay" class="evidence-card__text">{{ jdDisplay }}</pre>
        <span v-else class="evidence-card__missing">未在 JD 中找到对应要求</span>
      </div>

      <div class="evidence-card__column">
        <span class="evidence-card__label">简历证据</span>
        <pre v-if="resumeDisplay" class="evidence-card__text">{{ resumeDisplay }}</pre>
        <span v-else class="evidence-card__missing">未在简历中找到对应证据</span>
      </div>
    </div>

    <div v-if="hasKnowledgeEvidence" class="evidence-card__knowledge">
      <span class="evidence-card__label">知识库标准</span>
      <ul class="evidence-card__knowledge-list">
        <li
          v-for="(item, idx) in evidence.knowledgeEvidence"
          :key="idx"
          class="evidence-card__knowledge-item"
        >
          <template v-if="item.available">
            <span class="evidence-card__knowledge-title">{{ item.title }}</span>
            <pre class="evidence-card__text evidence-card__text--compact">{{ item.snippet }}</pre>
          </template>
          <span v-else class="evidence-card__knowledge-unavailable">
            {{ item.reason || '知识库证据不足' }}
          </span>
        </li>
      </ul>
    </div>

    <button
      v-if="needsExpand"
      type="button"
      class="evidence-card__toggle"
      @click="toggle"
    >
      {{ expanded ? '收起' : '展开全部' }}
    </button>
  </article>
</template>

<style scoped>
.evidence-card {
  background-color: var(--color-surface-2);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-md);
  padding: var(--space-sm) var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.evidence-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.evidence-card__columns {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-sm);
}

.evidence-card__column {
  display: flex;
  flex-direction: column;
  gap: var(--space-xxs);
}

.evidence-card__label {
  font-size: var(--font-caption-size);
  font-weight: 500;
  color: var(--color-ink-subtle);
}

.evidence-card__text {
  margin: 0;
  font-family: var(--font-family-mono);
  font-size: var(--font-mono-size);
  line-height: var(--font-mono-line);
  color: var(--color-ink-muted);
  white-space: pre-wrap;
  word-break: break-word;
  background-color: var(--color-surface-2);
  padding: var(--space-xs);
  border-radius: var(--rounded-xs);
}

.evidence-card__text--compact {
  font-size: var(--font-caption-size);
  padding: var(--space-xxs) var(--space-xs);
}

.evidence-card__missing {
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-tertiary);
  font-style: italic;
}

.evidence-card__knowledge {
  border-top: 1px solid var(--color-hairline);
  padding-top: var(--space-xs);
  display: flex;
  flex-direction: column;
  gap: var(--space-xxs);
}

.evidence-card__knowledge-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-xxs);
}

.evidence-card__knowledge-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.evidence-card__knowledge-title {
  font-size: var(--font-caption-size);
  font-weight: 600;
  color: var(--color-ink-subtle);
}

.evidence-card__knowledge-unavailable {
  font-size: var(--font-caption-size);
  color: var(--color-status-warning, #d97706);
  font-style: italic;
}

.evidence-card__toggle {
  align-self: flex-start;
  background: transparent;
  border: 1px solid var(--color-hairline);
  color: var(--color-ink-muted);
  font-size: var(--font-caption-size);
  padding: 2px 8px;
  border-radius: var(--rounded-xs);
  cursor: pointer;
}

.evidence-card__toggle:hover {
  background-color: var(--color-surface-1);
}

</style>
