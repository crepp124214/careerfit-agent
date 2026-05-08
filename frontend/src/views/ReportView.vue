<script setup lang="ts">
import { computed, onMounted, watch, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAvailabilityStore } from '@/stores/availability'
import { useAnalysesStore } from '@/stores/analyses'
import { useInterviewStore } from '@/stores/interview'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'
import LoadingCard from '@/components/feedback/LoadingCard.vue'
import ErrorBanner from '@/components/feedback/ErrorBanner.vue'
import NextBestActionCallout from '@/components/workbench/NextBestActionCallout.vue'
import ScoringOverviewCard from '@/components/report/ScoringOverviewCard.vue'
import SkillsRadarChart from '@/components/report/SkillsRadarChart.vue'
import CapabilityGapCard from '@/components/report/CapabilityGapCard.vue'
import ResumeSuggestionReview from '@/components/report/ResumeSuggestionReview.vue'
import ScoreDimensionGrid from '@/components/report/ScoreDimensionGrid.vue'
import EvidenceChainTable from '@/components/report/EvidenceChainTable.vue'
import InterviewQuestionCard from '@/components/report/InterviewQuestionCard.vue'
import AgentTraceTimeline from '@/components/report/AgentTraceTimeline.vue'

const route = useRoute()
const router = useRouter()
const availability = useAvailabilityStore()
const analyses = useAnalysesStore()
const interviewStore = useInterviewStore()

const taskId = computed(() => (route.params.taskId as string) ?? '')
const isUnavailable = computed(() => availability.states.reports === 'unavailable')
const isValidTaskId = computed(() => taskId.value.trim().length > 0)

const hasReport = computed(
  () => !analyses.loading && !analyses.error && analyses.report !== null,
)

const activeTab = ref<string>('analysis')

const showEvidence = ref(false)
const showAgentTrace = ref(false)

const tabs = computed(() => [
  { id: 'analysis', label: '匹配分析', visible: true },
  { id: 'resume', label: '简历优化', visible: (analyses.report?.suggestions?.length ?? 0) > 0 },
  { id: 'actions', label: '下一步行动', visible: (analyses.report?.interviewQuestions?.length ?? 0) > 0 || (analyses.report?.learningPlan?.length ?? 0) > 0 },
])

const visibleTabs = computed(() => tabs.value.filter(t => t.visible))

const hasAgentTrace = computed(() => (analyses.nodes?.length ?? 0) > 0)

const highRiskCount = computed(() => {
  if (!analyses.report?.dimensions) return 0
  return analyses.report.dimensions.filter(d => d.riskLevel === 'high').length
})

const safeSuggestions = computed(() => {
  if (!analyses.report?.suggestions) return []
  return analyses.report.suggestions.filter(s => s.riskLevel !== 'high' && !s.blocked)
})

async function load() {
  if (!isValidTaskId.value) return
  if (isUnavailable.value) return
  await analyses.loadReport(taskId.value)
}

async function startInterviewTraining() {
  if (!analyses.report) return
  const reportId = Number(analyses.report.id)
  if (!reportId) return
  const session = await interviewStore.createSession(reportId)
  if (session) {
    router.push(`/interview/${session.id}`)
  }
}

function exportMarkdown() {
  const id = Number(taskId.value)
  if (!id) return
  window.open(`/api/reports/${id}/export?format=markdown`, '_blank')
}

function printReport() {
  window.print()
}

function selectTab(tabId: string) {
  activeTab.value = tabId
}

onMounted(load)

watch(
  () => route.params.taskId,
  (id) => {
    if (typeof id === 'string' && id.trim().length > 0) {
      analyses.clear()
      load()
    }
  },
)
</script>

<template>
  <section class="report-view" role="main" aria-label="分析报告">
    <div class="report-view__header-row">
      <h1 class="report-view__title animate-in">分析报告</h1>
      <div v-if="hasReport" class="report-view__export">
        <button type="button" class="report-view__export-btn" @click="exportMarkdown">
          导出 Markdown
        </button>
        <button type="button" class="report-view__export-btn report-view__export-btn--print" @click="printReport">
          打印
        </button>
      </div>
    </div>

    <ErrorBanner
      v-if="!isValidTaskId"
      title="无效的任务 ID"
      detail="请从工作台或分析记录中选择一个有效的分析任务。"
    />

    <BackendNotReadyNotice
      v-else-if="isUnavailable"
      feature="评分报告"
      waitingFor="analysis pipeline"
    />

    <LoadingCard
      v-else-if="analyses.loading"
      title="正在加载报告…"
      :lines="4"
    />

    <ErrorBanner
      v-else-if="analyses.error"
      title="报告加载失败"
      :detail="analyses.error"
    />

    <template v-else-if="hasReport">
      <div v-if="analyses.report?.mode" class="report-view__mode-badge animate-in">
        {{ analyses.report.mode === 'lite_analysis' ? '快速分析' : '完整分析' }}
      </div>

      <NextBestActionCallout
        v-if="analyses.report!.nextBestAction"
        class="report-view__nba animate-in animate-in-stagger-1"
        :state="analyses.report!.nextBestAction.state"
        :headline="analyses.report!.nextBestAction.headline"
        :action-label="analyses.report!.nextBestAction.actionLabel"
        :cta-to="analyses.report!.nextBestAction.ctaTo ?? '/learning'"
        :waiting-reason="analyses.report!.nextBestAction.waitingReason"
      />

      <div v-if="highRiskCount > 0" class="report-view__risk-summary animate-in animate-in-stagger-1">
        <span class="report-view__risk-icon" aria-hidden="true">⚠️</span>
        <span class="report-view__risk-text">{{ highRiskCount }} 项高风险技能需关注</span>
      </div>

      <div class="report-view__overview-grid animate-in animate-in-stagger-2">
        <ScoringOverviewCard
          :total-score="analyses.report!.totalScore"
          :dimensions="analyses.report!.dimensions"
        />
        <SkillsRadarChart
          :dimensions="analyses.report!.dimensions"
        />
        <CapabilityGapCard
          :dimensions="analyses.report!.dimensions"
        />
        <section class="report-view__suggestions-preview" aria-label="优化建议摘要">
          <header class="suggestions-preview__header">
            <h3 class="suggestions-preview__title">简历优化建议</h3>
            <span class="suggestions-preview__count">{{ safeSuggestions.length }} 条</span>
          </header>

          <div v-if="safeSuggestions.length === 0" class="suggestions-preview__empty">
            <p>暂无可采纳的优化建议</p>
          </div>

          <ul v-else class="suggestions-preview__list">
            <li
              v-for="(sug, i) in safeSuggestions.slice(0, 3)"
              :key="i"
              class="suggestions-preview__item"
            >
              <div class="suggestions-preview__item-header">
                <span class="suggestions-preview__item-original">{{ sug.original }}</span>
              </div>
              <p class="suggestions-preview__item-optimized">{{ sug.optimized }}</p>
              <span class="suggestions-preview__item-jd">关联：{{ sug.jdRequirement || '无' }}</span>
            </li>
          </ul>

          <button
            v-if="safeSuggestions.length > 3"
            type="button"
            class="suggestions-preview__more"
            @click="selectTab('resume')"
          >
            查看全部 {{ safeSuggestions.length }} 条建议
          </button>
        </section>
      </div>

      <div class="report-view__tabs animate-in animate-in-stagger-3" role="tablist" aria-label="报告内容导航">
        <button
          v-for="tab in visibleTabs"
          :key="tab.id"
          type="button"
          role="tab"
          :aria-selected="activeTab === tab.id"
          :aria-controls="`panel-${tab.id}`"
          :id="`tab-${tab.id}`"
          class="report-view__tab"
          :class="{ 'report-view__tab--active': activeTab === tab.id }"
          @click="selectTab(tab.id)"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="report-view__content animate-in animate-in-stagger-3">
        <Transition name="tab-panel" mode="out-in">
          <div
            v-if="activeTab === 'analysis'"
            id="panel-analysis"
            key="analysis"
            role="tabpanel"
            aria-labelledby="tab-analysis"
            class="report-view__panel"
          >
            <ScoreDimensionGrid :dimensions="analyses.report!.dimensions" />

            <div class="report-view__evidence-section">
              <button
                type="button"
                class="report-view__evidence-toggle"
                :aria-expanded="showEvidence"
                @click="showEvidence = !showEvidence"
              >
                <svg
                  class="report-view__evidence-icon"
                  :class="{ 'report-view__evidence-icon--open': showEvidence }"
                  width="16"
                  height="16"
                  viewBox="0 0 16 16"
                  fill="none"
                  aria-hidden="true"
                >
                  <path d="M6 4L10 8L6 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span>{{ showEvidence ? '收起证据链详情' : '展开证据链详情' }}</span>
                <span class="report-view__evidence-count">({{ analyses.report!.dimensions?.length ?? 0 }} 项)</span>
              </button>

              <Transition name="evidence-fade">
                <EvidenceChainTable
                  v-if="showEvidence"
                  :dimensions="analyses.report!.dimensions"
                />
              </Transition>
            </div>

            <div v-if="hasAgentTrace" class="report-view__trace-section">
              <button
                type="button"
                class="report-view__trace-toggle"
                :aria-expanded="showAgentTrace"
                @click="showAgentTrace = !showAgentTrace"
              >
                <svg
                  class="report-view__evidence-icon"
                  :class="{ 'report-view__evidence-icon--open': showAgentTrace }"
                  width="16"
                  height="16"
                  viewBox="0 0 16 16"
                  fill="none"
                  aria-hidden="true"
                >
                  <path d="M6 4L10 8L6 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span>{{ showAgentTrace ? '收起技术详情' : '展开技术详情 (Agent Trace)' }}</span>
              </button>

              <Transition name="evidence-fade">
                <div v-if="showAgentTrace" class="report-view__trace-content">
                  <AgentTraceTimeline :nodes="analyses.nodes" />
                </div>
              </Transition>
            </div>
          </div>

          <div
            v-else-if="activeTab === 'resume'"
            id="panel-resume"
            key="resume"
            role="tabpanel"
            aria-labelledby="tab-resume"
            class="report-view__panel"
          >
            <ResumeSuggestionReview :suggestions="analyses.report!.suggestions" />
          </div>

          <div
            v-else-if="activeTab === 'actions'"
            id="panel-actions"
            key="actions"
            role="tabpanel"
            aria-labelledby="tab-actions"
            class="report-view__panel"
          >
            <section v-if="(analyses.report!.interviewQuestions?.length ?? 0) > 0" class="report-view__interview" aria-label="面试准备">
              <h3 class="report-view__section-title">面试准备</h3>
              <div class="report-view__interview-list">
                <InterviewQuestionCard
                  v-for="(q, i) in analyses.report!.interviewQuestions"
                  :key="i"
                  :question="q"
                />
              </div>
              <div class="report-view__interview-cta">
                <button
                  type="button"
                  class="report-view__interview-btn"
                  @click="startInterviewTraining"
                >
                  开始面试训练
                </button>
              </div>
            </section>
          </div>
        </Transition>
      </div>
    </template>

    <LoadingCard
      v-else
      title="等待分析结果…"
      :lines="3"
    />
  </section>
</template>

<style scoped>
.report-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  max-width: 1100px;
}

.report-view__title {
  margin: 0;
  font-size: var(--font-headline-size);
  font-weight: var(--font-headline-weight);
  line-height: var(--font-headline-line);
}

.report-view__header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.report-view__mode-badge {
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
  width: fit-content;
}

.report-view__export {
  display: flex;
  gap: var(--space-xs);
}

.report-view__export-btn {
  padding: var(--space-xs) var(--space-sm);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-sm);
  background: var(--color-surface-1);
  font-size: var(--font-caption-size);
  cursor: pointer;
  transition: background 0.15s ease;
}

.report-view__export-btn:hover {
  background: var(--color-surface-2);
}

.report-view__nba {
  flex-shrink: 0;
}

.report-view__risk-summary {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-sm) var(--space-md);
  background-color: var(--color-risk-high-bg);
  border: 1px solid rgba(229, 72, 77, 0.2);
  border-radius: var(--rounded-md);
}

.report-view__risk-icon {
  font-size: 16px;
}

.report-view__risk-text {
  font-size: var(--font-body-sm-size);
  color: var(--color-risk-high);
  font-weight: 500;
}

.report-view__overview-grid {
  display: grid;
  grid-template-columns: minmax(240px, 300px) minmax(0, 1fr);
  grid-template-rows: auto auto;
  gap: var(--space-md);
}

.report-view__overview-grid > :first-child {
  grid-row: 1;
  grid-column: 1;
}

.report-view__overview-grid > :nth-child(2) {
  grid-row: 1 / 3;
  grid-column: 2;
}

.report-view__overview-grid > :nth-child(3) {
  grid-row: 2;
  grid-column: 1;
}

.suggestions-preview {
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-xl);
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.suggestions-preview__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-sm);
}

.suggestions-preview__title {
  margin: 0;
  font-size: var(--font-body-lg-size);
  font-weight: 600;
  color: var(--color-ink);
}

.suggestions-preview__count {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

.suggestions-preview__empty {
  padding: var(--space-md);
  text-align: center;
  color: var(--color-ink-subtle);
  font-size: var(--font-body-sm-size);
}

.suggestions-preview__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.suggestions-preview__item {
  padding: var(--space-sm) var(--space-md);
  background-color: var(--color-surface-2);
  border-radius: var(--rounded-md);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.suggestions-preview__item-header {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.suggestions-preview__item-original {
  font-size: var(--font-caption-size);
  font-weight: 500;
  color: var(--color-ink-subtle);
}

.suggestions-preview__item-optimized {
  margin: 0;
  font-size: var(--font-body-sm-size);
  color: var(--color-ink);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.suggestions-preview__item-jd {
  font-size: var(--font-caption-size);
  color: var(--color-ink-tertiary);
}

.suggestions-preview__more {
  align-self: flex-start;
  padding: var(--space-xs) var(--space-sm);
  background: transparent;
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-sm);
  color: var(--color-primary);
  font-size: var(--font-caption-size);
  font-weight: 500;
  cursor: pointer;
  transition: background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.suggestions-preview__more:hover {
  background-color: var(--color-surface-2);
}

.report-view__tabs {
  display: flex;
  gap: var(--space-xs);
  padding: var(--space-xs);
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  overflow-x: auto;
}

.report-view__tab {
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

.report-view__tab:hover {
  background-color: var(--color-surface-2);
  color: var(--color-ink);
}

.report-view__tab--active {
  background-color: var(--color-primary);
  color: var(--color-on-primary);
}

.report-view__content {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.report-view__panel {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.report-view__section-title {
  margin: 0 0 var(--space-md);
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
  color: var(--color-ink);
}

.report-view__evidence-section,
.report-view__trace-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.report-view__evidence-toggle,
.report-view__trace-toggle {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-sm) var(--space-md);
  background-color: var(--color-surface-2);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-md);
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-muted);
  cursor: pointer;
  transition: all var(--motion-duration-fast) var(--motion-easing-standard);
}

.report-view__evidence-toggle:hover,
.report-view__trace-toggle:hover {
  background-color: var(--color-surface-3);
  color: var(--color-ink);
}

.report-view__evidence-icon {
  flex-shrink: 0;
  transition: transform var(--motion-duration-fast) var(--motion-easing-standard);
}

.report-view__evidence-icon--open {
  transform: rotate(90deg);
}

.report-view__evidence-count {
  color: var(--color-ink-tertiary);
}

.report-view__trace-content {
  padding: var(--space-md);
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-md);
}

.report-view__interview {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.report-view__interview-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.report-view__interview-cta {
  margin-top: var(--space-sm);
  display: flex;
  justify-content: center;
}

.report-view__interview-btn {
  padding: var(--space-sm) var(--space-lg);
  background: var(--color-primary);
  color: var(--color-on-primary);
  border: none;
  border-radius: var(--rounded-md);
  font-size: var(--font-body-size);
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s ease;
}

.report-view__interview-btn:hover {
  opacity: 0.9;
}

.report-view__learning {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

@media (max-width: 1024px) {
  .report-view__overview-grid {
    grid-template-columns: 1fr 1fr;
  }

  .report-view__overview-grid > :first-child,
  .report-view__overview-grid > :nth-child(2),
  .report-view__overview-grid > :nth-child(3) {
    grid-row: auto;
    grid-column: auto;
  }
}

@media (max-width: 768px) {
  .report-view__overview-grid {
    grid-template-columns: 1fr;
  }

  .report-view__tabs {
    flex-wrap: nowrap;
    -webkit-overflow-scrolling: touch;
  }

  .report-view__tab {
    flex: 0 0 auto;
    padding: var(--space-sm) var(--space-md);
    font-size: var(--font-caption-size);
    min-height: 44px;
  }
}

@media (max-width: 480px) {
  .report-view {
    gap: var(--space-md);
  }

  .report-view__title {
    font-size: 28px;
    letter-spacing: -0.5px;
  }

  .report-view__header-row {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-sm);
  }
}

.tab-panel-enter-active,
.tab-panel-leave-active {
  transition:
    opacity var(--motion-duration-base) var(--motion-easing-standard),
    transform var(--motion-duration-base) var(--motion-easing-standard);
}

.tab-panel-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.tab-panel-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.evidence-fade-enter-active,
.evidence-fade-leave-active {
  transition:
    opacity var(--motion-duration-base) var(--motion-easing-standard),
    max-height 0.3s var(--motion-easing-standard);
  max-height: 2000px;
  overflow: hidden;
}

.evidence-fade-enter-from,
.evidence-fade-leave-to {
  opacity: 0;
  max-height: 0;
}

@media print {
  .report-view__export,
  .report-view__tabs,
  .report-view__interview-cta,
  .report-view__evidence-toggle,
  .report-view__trace-toggle {
    display: none !important;
  }

  .report-view {
    max-width: none;
    gap: var(--space-md);
  }

  .report-view__header-row {
    margin-bottom: var(--space-sm);
  }

  .report-view__panel {
    gap: var(--space-md);
  }

  .report-view__evidence-section,
  .report-view__trace-section {
    display: block !important;
  }

  .report-view__trace-content {
    display: block !important;
    border: none;
    padding: 0;
  }
}
</style>
