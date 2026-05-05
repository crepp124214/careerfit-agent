<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Suggestion } from '@/api/reports'
import RiskPill from '@/components/risk/RiskPill.vue'

const props = defineProps<{
  suggestions: Suggestion[]
}>()

const expandedHighRisk = ref<Set<number>>(new Set())

const normalSuggestions = computed(() =>
  props.suggestions.filter((s) => s.riskLevel !== 'high' && !s.blocked)
)

const highRiskSuggestions = computed(() =>
  props.suggestions.filter((s) => s.riskLevel === 'high' || s.blocked)
)

function toggleHighRisk(index: number) {
  if (expandedHighRisk.value.has(index)) {
    expandedHighRisk.value.delete(index)
  } else {
    expandedHighRisk.value.add(index)
  }
}

function isExpanded(index: number): boolean {
  return expandedHighRisk.value.has(index)
}
</script>

<template>
  <section class="suggestion-review" aria-label="简历建议审核">
    <header class="suggestion-review__header">
      <h3 class="suggestion-review__title">简历建议</h3>
      <div class="suggestion-review__stats">
        <span class="suggestion-review__count">{{ suggestions.length }} 条建议</span>
        <span v-if="highRiskSuggestions.length > 0" class="suggestion-review__risk-badge">
          {{ highRiskSuggestions.length }} 条高风险
        </span>
      </div>
    </header>

    <div v-if="suggestions.length === 0" class="suggestion-review__empty">
      <p>暂无简历建议</p>
    </div>

    <template v-else>
      <div v-if="highRiskSuggestions.length > 0" class="suggestion-review__high-risk">
        <div class="suggestion-review__high-risk-header">
          <span class="suggestion-review__high-risk-icon" aria-hidden="true">⚠️</span>
          <span class="suggestion-review__high-risk-title">高风险建议</span>
          <span class="suggestion-review__high-risk-hint">（默认折叠，请谨慎审核）</span>
        </div>

        <div class="suggestion-review__high-risk-list">
          <article
            v-for="(sug, i) in highRiskSuggestions"
            :key="`high-${i}`"
            class="suggestion-review__item suggestion-review__item--high-risk"
          >
            <button
              type="button"
              class="suggestion-review__toggle"
              @click="toggleHighRisk(i)"
              :aria-expanded="isExpanded(i)"
            >
              <span class="suggestion-review__toggle-icon" aria-hidden="true">
                {{ isExpanded(i) ? '▼' : '▶' }}
              </span>
              <span class="suggestion-review__toggle-text">
                {{ sug.original || '简历建议' }}
              </span>
              <RiskPill :level="sug.riskLevel" />
            </button>

            <div v-if="isExpanded(i)" class="suggestion-review__content">
              <div class="suggestion-review__field">
                <span class="suggestion-review__label">原始依据</span>
                <p class="suggestion-review__value">{{ sug.original }}</p>
              </div>

              <div class="suggestion-review__field">
                <span class="suggestion-review__label">优化表达</span>
                <p class="suggestion-review__value suggestion-review__value--optimized">
                  {{ sug.optimized }}
                </p>
              </div>

              <div class="suggestion-review__field">
                <span class="suggestion-review__label">关联 JD 要求</span>
                <p class="suggestion-review__value">{{ sug.jdRequirement || '无' }}</p>
              </div>

              <div class="suggestion-review__field">
                <span class="suggestion-review__label">使用的简历证据</span>
                <p class="suggestion-review__value">{{ sug.resumeEvidence || '无' }}</p>
              </div>

              <div v-if="sug.blocked" class="suggestion-review__blocked-notice">
                <span class="suggestion-review__blocked-icon" aria-hidden="true">🚫</span>
                <span>此建议已被 Integrity Guard 拦截，不建议采用</span>
              </div>
            </div>
          </article>
        </div>
      </div>

      <div v-if="normalSuggestions.length > 0" class="suggestion-review__normal">
        <h4 class="suggestion-review__normal-title">建议优化</h4>

        <div class="suggestion-review__normal-list">
          <article
            v-for="(sug, i) in normalSuggestions"
            :key="`normal-${i}`"
            class="suggestion-review__item"
          >
            <header class="suggestion-review__item-header">
              <span class="suggestion-review__item-title">{{ sug.original || '简历建议' }}</span>
              <RiskPill :level="sug.riskLevel" />
            </header>

            <div class="suggestion-review__content">
              <div class="suggestion-review__field">
                <span class="suggestion-review__label">原始依据</span>
                <p class="suggestion-review__value">{{ sug.original }}</p>
              </div>

              <div class="suggestion-review__field">
                <span class="suggestion-review__label">优化表达</span>
                <p class="suggestion-review__value suggestion-review__value--optimized">
                  {{ sug.optimized }}
                </p>
              </div>

              <div class="suggestion-review__field">
                <span class="suggestion-review__label">关联 JD 要求</span>
                <p class="suggestion-review__value">{{ sug.jdRequirement || '无' }}</p>
              </div>

              <div class="suggestion-review__field">
                <span class="suggestion-review__label">使用的简历证据</span>
                <p class="suggestion-review__value">{{ sug.resumeEvidence || '无' }}</p>
              </div>
            </div>
          </article>
        </div>
      </div>

      <p class="suggestion-review__disclaimer">
        请仔细审核每条建议，确保优化表达不新增事实。系统不提供"一键应用全部"功能，以避免引入不准确内容。
      </p>
    </template>
  </section>
</template>

<style scoped>
.suggestion-review {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.suggestion-review__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-md);
}

.suggestion-review__title {
  margin: 0;
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
  line-height: var(--font-card-title-line);
  color: var(--color-ink);
}

.suggestion-review__stats {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: var(--font-caption-size);
}

.suggestion-review__count {
  color: var(--color-ink-subtle);
}

.suggestion-review__risk-badge {
  padding: 2px 8px;
  background-color: rgba(235, 87, 87, 0.15);
  color: #eb5757;
  border-radius: var(--rounded-sm);
  font-weight: 500;
}

.suggestion-review__empty {
  padding: var(--space-lg);
  text-align: center;
  color: var(--color-ink-subtle);
  font-size: var(--font-body-size);
  background-color: var(--color-surface-1);
  border: 1px dashed var(--color-hairline);
  border-radius: var(--rounded-lg);
}

.suggestion-review__high-risk {
  padding: var(--space-md);
  background-color: rgba(235, 87, 87, 0.05);
  border: 1px solid rgba(235, 87, 87, 0.2);
  border-radius: var(--rounded-lg);
}

.suggestion-review__high-risk-header {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  margin-bottom: var(--space-md);
}

.suggestion-review__high-risk-icon {
  font-size: 16px;
}

.suggestion-review__high-risk-title {
  font-weight: 600;
  color: #eb5757;
}

.suggestion-review__high-risk-hint {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

.suggestion-review__high-risk-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.suggestion-review__normal {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.suggestion-review__normal-title {
  margin: 0;
  font-size: var(--font-body-size);
  font-weight: 600;
  color: var(--color-ink);
}

.suggestion-review__normal-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.suggestion-review__item {
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  overflow: hidden;
}

.suggestion-review__item--high-risk {
  background-color: var(--color-surface-2);
}

.suggestion-review__item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md);
  border-bottom: 1px solid var(--color-hairline);
}

.suggestion-review__item-title {
  font-weight: 500;
  color: var(--color-ink);
}

.suggestion-review__toggle {
  width: 100%;
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md);
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
  min-height: 44px;
  transition: background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.suggestion-review__toggle:hover {
  background-color: var(--color-surface-2);
}

.suggestion-review__toggle-icon {
  font-size: 12px;
  color: var(--color-ink-subtle);
}

.suggestion-review__toggle-text {
  flex: 1;
  font-weight: 500;
  color: var(--color-ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.suggestion-review__content {
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  border-top: 1px solid var(--color-hairline);
}

.suggestion-review__field {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.suggestion-review__label {
  font-size: var(--font-caption-size);
  font-weight: 500;
  color: var(--color-ink-subtle);
}

.suggestion-review__value {
  margin: 0;
  font-size: var(--font-body-sm-size);
  color: var(--color-ink);
  line-height: 1.4;
}

.suggestion-review__value--optimized {
  background-color: var(--color-surface-2);
  padding: var(--space-xs);
  border-radius: var(--rounded-xs);
}

.suggestion-review__blocked-notice {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-sm);
  background-color: rgba(235, 87, 87, 0.1);
  border-radius: var(--rounded-sm);
  font-size: var(--font-caption-size);
  color: #eb5757;
  margin-top: var(--space-sm);
}

.suggestion-review__blocked-icon {
  font-size: 14px;
}

.suggestion-review__disclaimer {
  margin: 0;
  padding: var(--space-sm);
  background-color: var(--color-surface-2);
  border-radius: var(--rounded-sm);
  font-size: var(--font-caption-size);
  color: var(--color-ink-muted);
  text-align: center;
}

@media (max-width: 768px) {
  .suggestion-review__header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
