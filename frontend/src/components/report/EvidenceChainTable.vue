<script setup lang="ts">
import { computed } from 'vue'
import type { Dimension } from '@/api/reports'

const props = defineProps<{
  dimensions: Dimension[]
}>()

interface FlattenedEvidence {
  dimensionName: string
  jdExcerpt: string
  resumeExcerpt: string
  knowledgeTitle?: string
  knowledgeSnippet?: string
  knowledgeAvailable?: boolean
}

const flattenedEvidence = computed<FlattenedEvidence[]>(() => {
  const result: FlattenedEvidence[] = []
  
  for (const dim of props.dimensions) {
    if (dim.evidence && dim.evidence.length > 0) {
      for (const ev of dim.evidence) {
        result.push({
          dimensionName: dim.name,
          jdExcerpt: ev.jdExcerpt || '',
          resumeExcerpt: ev.resumeExcerpt || '',
          knowledgeTitle: ev.knowledgeEvidence?.[0]?.title,
          knowledgeSnippet: ev.knowledgeEvidence?.[0]?.snippet,
          knowledgeAvailable: ev.knowledgeEvidence?.[0]?.available,
        })
      }
    } else {
      result.push({
        dimensionName: dim.name,
        jdExcerpt: '',
        resumeExcerpt: '',
      })
    }
  }
  
  return result
})

const hasEvidence = computed(() => flattenedEvidence.value.length > 0)

function truncate(text: string, maxLength: number = 100): string {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}
</script>

<template>
  <section class="evidence-chain" aria-label="证据链">
    <header class="evidence-chain__header">
      <h3 class="evidence-chain__title">证据链</h3>
      <span class="evidence-chain__count">{{ flattenedEvidence.length }} 项</span>
    </header>

    <div v-if="!hasEvidence" class="evidence-chain__empty">
      <p>暂无证据链数据</p>
    </div>

    <div v-else class="evidence-chain__table-wrapper">
      <table class="evidence-chain__table">
        <thead>
          <tr>
            <th scope="col" class="evidence-chain__th evidence-chain__th--dimension">技能维度</th>
            <th scope="col" class="evidence-chain__th evidence-chain__th--jd">JD 证据</th>
            <th scope="col" class="evidence-chain__th evidence-chain__th--resume">简历证据</th>
            <th scope="col" class="evidence-chain__th evidence-chain__th--knowledge">知识库证据</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(ev, i) in flattenedEvidence"
            :key="i"
            class="evidence-chain__row"
          >
            <td class="evidence-chain__td evidence-chain__td--dimension">
              <span class="evidence-chain__dimension-name">{{ ev.dimensionName }}</span>
            </td>
            <td class="evidence-chain__td evidence-chain__td--jd">
              <template v-if="ev.jdExcerpt">
                <span class="evidence-chain__excerpt">{{ truncate(ev.jdExcerpt) }}</span>
              </template>
              <template v-else>
                <span class="evidence-chain__missing">未找到 JD 证据</span>
              </template>
            </td>
            <td class="evidence-chain__td evidence-chain__td--resume">
              <template v-if="ev.resumeExcerpt">
                <span class="evidence-chain__excerpt">{{ truncate(ev.resumeExcerpt) }}</span>
              </template>
              <template v-else>
                <span class="evidence-chain__missing">未找到简历证据</span>
              </template>
            </td>
            <td class="evidence-chain__td evidence-chain__td--knowledge">
              <template v-if="ev.knowledgeTitle || ev.knowledgeSnippet">
                <span class="evidence-chain__knowledge-title">{{ ev.knowledgeTitle }}</span>
                <span v-if="ev.knowledgeSnippet" class="evidence-chain__excerpt">
                  {{ truncate(ev.knowledgeSnippet, 80) }}
                </span>
                <span
                  v-if="ev.knowledgeAvailable === false"
                  class="evidence-chain__knowledge-unavailable"
                >
                  (不可用)
                </span>
              </template>
              <template v-else>
                <span class="evidence-chain__missing">未找到知识库证据</span>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.evidence-chain {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.evidence-chain__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-md);
}

.evidence-chain__title {
  margin: 0;
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
  line-height: var(--font-card-title-line);
  color: var(--color-ink);
}

.evidence-chain__count {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

.evidence-chain__empty {
  padding: var(--space-lg);
  text-align: center;
  color: var(--color-ink-subtle);
  font-size: var(--font-body-size);
  background-color: var(--color-surface-1);
  border: 1px dashed var(--color-hairline);
  border-radius: var(--rounded-lg);
}

.evidence-chain__table-wrapper {
  overflow-x: auto;
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
}

.evidence-chain__table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-body-sm-size);
}

.evidence-chain__th {
  padding: var(--space-sm) var(--space-md);
  text-align: left;
  font-weight: 600;
  color: var(--color-ink-subtle);
  background-color: var(--color-surface-2);
  border-bottom: 1px solid var(--color-hairline);
  white-space: nowrap;
}

.evidence-chain__th--dimension {
  width: 120px;
}

.evidence-chain__th--jd,
.evidence-chain__th--resume,
.evidence-chain__th--knowledge {
  min-width: 150px;
}

.evidence-chain__row {
  border-bottom: 1px solid var(--color-hairline);
}

.evidence-chain__row:last-child {
  border-bottom: none;
}

.evidence-chain__td {
  padding: var(--space-sm) var(--space-md);
  vertical-align: top;
  color: var(--color-ink);
}

.evidence-chain__td--dimension {
  font-weight: 500;
}

.evidence-chain__dimension-name {
  display: inline-block;
  padding: 2px 8px;
  background-color: var(--color-surface-2);
  border-radius: var(--rounded-sm);
  font-size: var(--font-caption-size);
}

.evidence-chain__excerpt {
  display: block;
  color: var(--color-ink-muted);
  line-height: 1.4;
}

.evidence-chain__missing {
  display: inline-block;
  padding: 2px 8px;
  background-color: rgba(235, 87, 87, 0.1);
  color: #eb5757;
  border-radius: var(--rounded-sm);
  font-size: var(--font-caption-size);
}

.evidence-chain__knowledge-title {
  display: block;
  font-weight: 500;
  margin-bottom: 2px;
}

.evidence-chain__knowledge-unavailable {
  display: inline-block;
  padding: 1px 6px;
  background-color: rgba(242, 153, 74, 0.1);
  color: #f2994a;
  border-radius: var(--rounded-sm);
  font-size: var(--font-caption-size);
  margin-left: var(--space-xs);
}

@media (max-width: 768px) {
  .evidence-chain__table-wrapper {
    margin: 0 calc(-1 * var(--space-md));
    border-radius: 0;
    border-left: none;
    border-right: none;
  }

  .evidence-chain__th,
  .evidence-chain__td {
    padding: var(--space-xs) var(--space-sm);
  }
}
</style>
