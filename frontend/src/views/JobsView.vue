<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAvailabilityStore } from '@/stores/availability'
import { useJobsStore } from '@/stores/jobs'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'
import LoadingCard from '@/components/feedback/LoadingCard.vue'
import EmptyState from '@/components/feedback/EmptyState.vue'
import AppButton from '@/components/common/AppButton.vue'
import AppInput from '@/components/common/AppInput.vue'
import AppTextarea from '@/components/common/AppTextarea.vue'
import Modal from '@/components/common/Modal.vue'
import { formatDate } from '@/utils/format'

const router = useRouter()
const availability = useAvailabilityStore()
const jobs = useJobsStore()

const showModal = ref(false)
const newTitle = ref('')
const newCompany = ref('')
const newJdText = ref('')
const submitting = ref(false)

onMounted(async () => {
  await availability.probe()
  if (availability.states.jobs === 'ready') {
    jobs.load()
  }
})

async function submit() {
  if (!newTitle.value.trim()) return
  const rawText = newJdText.value.trim() || newTitle.value.trim()
  submitting.value = true
  await jobs.add({
    title: newTitle.value.trim(),
    raw_text: rawText,
  })
  submitting.value = false
  showModal.value = false
  newTitle.value = ''
  newCompany.value = ''
  newJdText.value = ''
}

function goToDetail(id: number) {
  router.push({ name: 'job-detail', params: { id: String(id) } })
}

const allDimensionNames = ref<string[]>([])

async function handleCompare() {
  await jobs.runCompare()
  if (jobs.compareData && jobs.compareData.length > 0) {
    const names = new Set<string>()
    for (const item of jobs.compareData) {
      for (const dim of item.dimensions) {
        names.add(dim.name)
      }
    }
    allDimensionNames.value = Array.from(names)
  }
}

const requiredLevelLabel: Record<string, string> = {
  mentioned: '了解',
  basic_usage: '基础使用',
  project_practice: '项目实践',
  deep_experience: '深入经验',
}
</script>

<template>
  <section class="jobs-view" role="main" aria-label="目标岗位">
    <header class="jobs-view__header">
      <h1 class="jobs-view__title">
        {{ jobs.compareMode ? '岗位对比' : '目标岗位' }}
      </h1>
      <div class="jobs-view__header-actions">
        <AppButton
          v-if="!jobs.compareMode"
          variant="primary"
          :disabled="availability.states.jobs !== 'ready'"
          @click="showModal = true"
        >
          新建岗位
        </AppButton>
        <AppButton
          v-if="!jobs.compareMode"
          variant="secondary"
          @click="jobs.toggleCompareMode()"
        >
          对比模式
        </AppButton>
        <AppButton
          v-else
          variant="tertiary"
          @click="jobs.clearCompare()"
        >
          退出对比
        </AppButton>
      </div>
    </header>

    <!-- 对比结果 -->
    <div v-if="jobs.compareData" class="jobs-view__compare-results">
      <div class="jobs-view__compare-table-wrap">
        <table class="jobs-view__compare-table">
          <thead>
            <tr>
              <th class="jobs-view__compare-th">技能维度</th>
              <th v-for="item in jobs.compareData" :key="item.job_id" class="jobs-view__compare-th">
                {{ item.job_title }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="dimName in allDimensionNames" :key="dimName" class="jobs-view__compare-row">
              <td class="jobs-view__compare-dim">{{ dimName }}</td>
              <td v-for="item in jobs.compareData" :key="item.job_id" class="jobs-view__compare-cell">
                <template v-if="item.dimensions.find(d => d.name === dimName)">
                  <span class="jobs-view__compare-level">
                    {{ requiredLevelLabel[item.dimensions.find(d => d.name === dimName)!.required_level] || item.dimensions.find(d => d.name === dimName)!.required_level }}
                  </span>
                </template>
                <span v-else class="jobs-view__compare-none">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="jobs-view__compare-actions">
        <AppButton variant="tertiary" @click="jobs.clearCompare()">
          返回列表
        </AppButton>
      </div>
    </div>

    <template v-else>
      <BackendNotReadyNotice
        v-if="availability.states.jobs === 'unavailable'"
        feature="岗位管理"
        waitingFor="jobs API"
      />

      <LoadingCard v-else-if="jobs.loading" title="加载岗位列表中…" />

      <EmptyState
        v-else-if="jobs.list.length === 0"
        title="还没有目标岗位"
        description="添加一个目标岗位，系统才能进行匹配分析。"
        action-label="新建岗位"
        @action="showModal = true"
      />

      <div v-else-if="jobs.compareMode" class="jobs-view__compare-bar">
        <span class="jobs-view__compare-bar-text">
          已选 {{ jobs.compareSelection.size }} / 5 个岗位
        </span>
        <AppButton
          variant="primary"
          :disabled="!jobs.compareEnabled"
          :loading="jobs.compareLoading"
          @click="handleCompare"
        >
          开始对比
        </AppButton>
      </div>

      <ul class="jobs-view__list" role="list">
        <li
          v-for="job in jobs.list"
          :key="job.id"
          class="jobs-view__item"
          @click="!jobs.compareMode && goToDetail(job.id)"
        >
          <div v-if="jobs.compareMode" class="jobs-view__item-checkbox" @click.stop>
            <input
              type="checkbox"
              :checked="jobs.compareSelection.has(job.id)"
              :disabled="!jobs.compareSelection.has(job.id) && jobs.compareSelection.size >= 5"
              @change="jobs.toggleCompareSelection(job.id)"
            />
          </div>
          <div class="jobs-view__item-main">
            <span class="jobs-view__item-title">{{ job.title }}</span>
          </div>
          <span class="jobs-view__item-date">{{ formatDate(job.created_at) }}</span>
        </li>
      </ul>
    </template>

    <Modal
      :open="showModal"
      title="新建岗位"
      description="填写岗位基本信息，后续可补充 JD 全文。"
      @close="showModal = false"
    >
      <div class="jobs-view__form">
        <AppInput
          v-model="newTitle"
          label="岗位名称"
          placeholder="例如：后端开发工程师"
          :required="true"
        />
        <AppInput
          v-model="newCompany"
          label="公司（可选）"
          placeholder="例如：某科技有限公司"
        />
        <AppTextarea
          v-model="newJdText"
          label="职位描述 JD（可选）"
          placeholder="粘贴完整的 JD 内容…"
          :min-height="'120px'"
        />
      </div>
      <template #footer>
        <AppButton variant="tertiary" @click="showModal = false">取消</AppButton>
        <AppButton
          variant="primary"
          :loading="submitting"
          :disabled="!newTitle.trim()"
          @click="submit"
        >
          保存
        </AppButton>
      </template>
    </Modal>
  </section>
</template>

<style scoped>
.jobs-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  max-width: 960px;
}

.jobs-view__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-md);
}

.jobs-view__title {
  margin: 0;
  font-size: var(--font-headline-size);
  font-weight: var(--font-headline-weight);
  line-height: var(--font-headline-line);
  letter-spacing: var(--font-headline-letter);
}

.jobs-view__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.jobs-view__item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  cursor: pointer;
  transition:
    background-color var(--motion-duration-fast) var(--motion-easing-standard),
    border-color var(--motion-duration-fast) var(--motion-easing-standard),
    box-shadow var(--motion-duration-fast) var(--motion-easing-standard);
}

.jobs-view__item:hover {
  background-color: var(--color-surface-2);
  border-color: var(--color-hairline-strong);
  box-shadow: var(--shadow-sm);
}

.jobs-view__item-main {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.jobs-view__item-title {
  font-size: var(--font-body-size);
  font-weight: 500;
  color: var(--color-ink);
}

.jobs-view__item-company {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

.jobs-view__item-date {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
  flex-shrink: 0;
}

.jobs-view__form {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.jobs-view__header-actions {
  display: flex;
  gap: var(--space-sm);
}

.jobs-view__compare-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-sm) var(--space-md);
  background: var(--color-surface-2);
  border-radius: var(--rounded-md);
  gap: var(--space-md);
}

.jobs-view__compare-bar-text {
  font-size: var(--font-caption-size);
  color: var(--color-ink-muted);
}

.jobs-view__compare-results {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.jobs-view__compare-table-wrap {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.jobs-view__compare-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-body-sm-size);
}

.jobs-view__compare-th {
  text-align: left;
  padding: var(--space-sm) var(--space-md);
  background: var(--color-surface-2);
  font-weight: 600;
  color: var(--color-ink);
  border-bottom: 2px solid var(--color-hairline);
  white-space: nowrap;
}

.jobs-view__compare-dim {
  padding: var(--space-sm) var(--space-md);
  font-weight: 500;
  color: var(--color-ink);
  border-bottom: 1px solid var(--color-hairline);
  white-space: nowrap;
}

.jobs-view__compare-cell {
  padding: var(--space-sm) var(--space-md);
  text-align: center;
  border-bottom: 1px solid var(--color-hairline);
}

.jobs-view__compare-level {
  display: inline-block;
  padding: 2px 8px;
  background: var(--color-surface-2);
  border-radius: var(--rounded-xs);
  font-size: var(--font-caption-size);
  color: var(--color-primary);
}

.jobs-view__compare-none {
  color: var(--color-ink-tertiary);
  font-size: var(--font-caption-size);
}

.jobs-view__compare-actions {
  display: flex;
  justify-content: center;
  padding-top: var(--space-sm);
}

.jobs-view__item-checkbox {
  display: flex;
  align-items: center;
  padding-right: var(--space-xs);
}
</style>
