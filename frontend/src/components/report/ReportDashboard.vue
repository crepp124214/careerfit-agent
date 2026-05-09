<script setup lang="ts">
import { ref, computed } from 'vue'
import ReportCard from './ReportCard.vue'
import ScoringOverviewCard from './ScoringOverviewCard.vue'
import SkillsRadarChart from './SkillsRadarChart.vue'
import NextBestActionCallout from '@/components/workbench/NextBestActionCallout.vue'
import CapabilityGapCard from './CapabilityGapCard.vue'
import SuggestionCard from './SuggestionCard.vue'
import InterviewQuestionCard from './InterviewQuestionCard.vue'
import ScoreDimensionGrid from './ScoreDimensionGrid.vue'
import ResumeSuggestionReview from './ResumeSuggestionReview.vue'
import EvidenceChainTable from './EvidenceChainTable.vue'
import AgentTraceTimeline from './AgentTraceTimeline.vue'
import Breadcrumb from '@/components/common/Breadcrumb.vue'

const props = defineProps<{
  report: Record<string, any>
  nodes: any[]
}>()

const emit = defineEmits<{
  (e: 'start-interview'): void
  (e: 'export-markdown'): void
  (e: 'print'): void
}>()

const showEvidence = ref(false)
const showAgentTrace = ref(false)
const activeTab = ref<string>('analysis')

const highRiskCount = computed(() => {
  if (!props.report?.dimensions) return 0
  return props.report.dimensions.filter((d: any) => d.riskLevel === 'high').length
})

const safeSuggestions = computed(() => {
  if (!props.report?.suggestions) return []
  return props.report.suggestions.filter((s: any) => s.riskLevel !== 'high' && !s.blocked)
})

const hasAgentTrace = computed(() => (props.nodes?.length ?? 0) > 0)

const tabs = computed(() => [
  { id: 'analysis', label: '匹配分析', visible: true },
  { id: 'resume', label: '简历优化', visible: (props.report?.suggestions?.length ?? 0) > 0 },
  { id: 'actions', label: '下一步行动', visible: (props.report?.interviewQuestions?.length ?? 0) > 0 || (props.report?.learningPlan?.length ?? 0) > 0 },
])

const visibleTabs = computed(() => tabs.value.filter(t => t.visible))
</script>

<template>
  <div class="dashboard">
    <Breadcrumb :items="[{ label: '工作台', to: '/' }, { label: '报告' }]" />

    <div class="dashboard__header-row">
      <div v-if="report?.mode" class="dashboard__mode-badge">
        {{ report.mode === 'lite_analysis' ? '快速分析' : '完整分析' }}
      </div>
      <div class="dashboard__export">
        <button type="button" class="dashboard__export-btn" @click="emit('export-markdown')">
          导出 Markdown
        </button>
        <button type="button" class="dashboard__export-btn" @click="emit('print')">
          打印
        </button>
      </div>
    </div>

    <div v-if="highRiskCount > 0" class="dashboard__risk-summary">
      <span class="dashboard__risk-icon" aria-hidden="true">⚠️</span>
      <span class="dashboard__risk-text">{{ highRiskCount }} 项高风险技能需关注</span>
    </div>

    <div class="dashboard__grid">
      <ReportCard title="总分">
        <ScoringOverviewCard
          :total-score="report.totalScore"
          :dimensions="report.dimensions"
        />
      </ReportCard>

      <ReportCard title="技能雷达">
        <SkillsRadarChart :dimensions="report.dimensions" />
      </ReportCard>

      <ReportCard title="下一步建议">
        <NextBestActionCallout
          v-if="report.nextBestAction"
          :state="report.nextBestAction.state"
          :headline="report.nextBestAction.headline"
          :action-label="report.nextBestAction.actionLabel"
          :cta-to="report.nextBestAction.ctaTo ?? '/interview?tab=learning'"
          :waiting-reason="report.nextBestAction.waitingReason"
          @action="emit('start-interview')"
        />
        <p v-else class="dashboard__empty-nba">暂无建议</p>
      </ReportCard>

      <ReportCard title="能力缺口">
        <CapabilityGapCard :dimensions="report.dimensions" />
      </ReportCard>

      <ReportCard title="简历建议">
        <div v-if="safeSuggestions.length > 0" class="dashboard__suggestion-list">
          <SuggestionCard
            v-for="(sug, i) in safeSuggestions.slice(0, 3)"
            :key="i"
            :suggestion="sug"
          />
        </div>
        <p v-else class="dashboard__empty-nba">暂无可采纳的优化建议</p>
      </ReportCard>

      <ReportCard title="面试题">
        <div v-if="(report.interviewQuestions?.length ?? 0) > 0" class="dashboard__interview-preview">
          <InterviewQuestionCard
            v-for="(q, i) in report.interviewQuestions.slice(0, 3)"
            :key="i"
            :question="q"
          />
        </div>
        <p v-else class="dashboard__empty-nba">暂无面试题</p>
        <template #cta>
          <button type="button" class="dashboard__card-cta" @click="emit('start-interview')">
            开始面试训练
          </button>
        </template>
      </ReportCard>
    </div>

    <div class="dashboard__tabs" role="tablist" aria-label="报告详情导航">
      <button
        v-for="tab in visibleTabs"
        :key="tab.id"
        type="button"
        role="tab"
        :aria-selected="activeTab === tab.id"
        :class="['dashboard__tab', { 'dashboard__tab--active': activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </div>

    <div class="dashboard__detail-content">
      <div v-if="activeTab === 'analysis'" class="dashboard__panel">
        <ScoreDimensionGrid :dimensions="report.dimensions" />

        <details class="dashboard__details" :open="showEvidence">
          <summary class="dashboard__details-summary" @click.prevent="showEvidence = !showEvidence">
            {{ showEvidence ? '收起证据链详情' : '展开证据链详情' }}
            ({{ report.dimensions?.length ?? 0 }} 项)
          </summary>
          <EvidenceChainTable v-if="showEvidence" :dimensions="report.dimensions" />
        </details>

        <details v-if="hasAgentTrace" class="dashboard__details" :open="showAgentTrace">
          <summary class="dashboard__details-summary" @click.prevent="showAgentTrace = !showAgentTrace">
            {{ showAgentTrace ? '收起技术详情' : '展开技术详情 (Agent Trace)' }}
          </summary>
          <AgentTraceTimeline v-if="showAgentTrace" :nodes="nodes" />
        </details>
      </div>

      <div v-else-if="activeTab === 'resume'" class="dashboard__panel">
        <ResumeSuggestionReview :suggestions="report.suggestions" />
      </div>

      <div v-else-if="activeTab === 'actions'" class="dashboard__panel">
        <section v-if="(report.interviewQuestions?.length ?? 0) > 0" aria-label="面试准备">
          <h3 class="dashboard__section-title">面试准备</h3>
          <div class="dashboard__interview-list">
            <InterviewQuestionCard
              v-for="(q, i) in report.interviewQuestions"
              :key="i"
              :question="q"
            />
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.dashboard__header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dashboard__mode-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs);
  padding: 4px 12px;
  font-size: var(--font-caption-size);
  font-weight: 600;
  color: var(--color-primary);
  background-color: var(--color-surface-2);
  border: 1px solid var(--color-primary);
  border-radius: var(--rounded-full);
}

.dashboard__export {
  display: flex;
  gap: var(--space-xs);
}

.dashboard__export-btn {
  padding: var(--space-xs) var(--space-sm);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-sm);
  background: var(--color-surface-1);
  font-size: var(--font-caption-size);
  cursor: pointer;
  transition: background 0.15s ease;
}

.dashboard__export-btn:hover {
  background: var(--color-surface-2);
}

.dashboard__risk-summary {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-sm) var(--space-md);
  background-color: var(--color-risk-high-bg);
  border: 1px solid rgba(229, 72, 77, 0.2);
  border-radius: var(--rounded-md);
}

.dashboard__risk-icon {
  font-size: 16px;
}

.dashboard__risk-text {
  font-size: var(--font-body-sm-size);
  color: var(--color-risk-high);
  font-weight: 500;
}

.dashboard__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-md);
}

.dashboard__empty-nba {
  color: var(--color-ink-subtle);
  font-size: var(--font-body-sm-size);
  text-align: center;
  padding: var(--space-md);
}

.dashboard__interview-preview {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.dashboard__card-cta {
  width: 100%;
  padding: var(--space-sm);
  background-color: var(--color-primary);
  color: var(--color-on-primary);
  border: none;
  border-radius: var(--rounded-md);
  font-size: var(--font-button-size);
  font-weight: var(--font-button-weight);
  cursor: pointer;
  transition: background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.dashboard__card-cta:hover {
  background-color: var(--color-primary-hover);
}

.dashboard__tabs {
  display: flex;
  gap: var(--space-xs);
  padding: var(--space-xs);
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  overflow-x: auto;
}

.dashboard__tab {
  flex: 1;
  min-width: max-content;
  padding: var(--space-sm) var(--space-md);
  border: none;
  border-radius: var(--rounded-md);
  background: transparent;
  font-size: var(--font-body-sm-size);
  font-weight: 500;
  color: var(--color-ink-muted);
  cursor: pointer;
  transition: all var(--motion-duration-fast) var(--motion-easing-standard);
}

.dashboard__tab:hover {
  background-color: var(--color-surface-2);
  color: var(--color-ink);
}

.dashboard__tab--active {
  background-color: var(--color-primary);
  color: var(--color-on-primary);
}

.dashboard__detail-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.dashboard__panel {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.dashboard__section-title {
  margin: 0 0 var(--space-md);
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
  color: var(--color-ink);
}

.dashboard__details {
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-md);
  overflow: hidden;
}

.dashboard__details-summary {
  padding: var(--space-sm) var(--space-md);
  background-color: var(--color-surface-2);
  cursor: pointer;
  font-size: var(--font-body-sm-size);
  font-weight: 500;
  color: var(--color-ink-muted);
  list-style: none;
}

.dashboard__details-summary::before {
  content: '▶ ';
  font-size: 10px;
}

.dashboard__details[open] .dashboard__details-summary::before {
  content: '▼ ';
}

.dashboard__interview-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

@media (max-width: 1024px) {
  .dashboard__grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .dashboard__grid {
    grid-template-columns: 1fr;
  }

  .dashboard__tabs {
    flex-wrap: nowrap;
    -webkit-overflow-scrolling: touch;
  }

  .dashboard__tab {
    flex: 0 0 auto;
    padding: var(--space-sm) var(--space-md);
    font-size: var(--font-caption-size);
    min-height: 44px;
  }
}

@media print {
  .dashboard__export,
  .dashboard__tabs,
  .dashboard__card-cta {
    display: none !important;
  }
}
</style>
