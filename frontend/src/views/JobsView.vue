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

onMounted(() => {
  availability.probe()
  if (availability.states.jobs !== 'unavailable') {
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
</script>

<template>
  <section class="jobs-view" role="main" aria-label="目标岗位">
    <header class="jobs-view__header">
      <h1 class="jobs-view__title">目标岗位</h1>
      <AppButton
        variant="primary"
        :disabled="availability.states.jobs !== 'ready'"
        @click="showModal = true"
      >
        新建岗位
      </AppButton>
    </header>

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

    <ul v-else class="jobs-view__list" role="list">
      <li
        v-for="job in jobs.list"
        :key="job.id"
        class="jobs-view__item"
        @click="goToDetail(job.id)"
      >
        <div class="jobs-view__item-main">
          <span class="jobs-view__item-title">{{ job.title }}</span>
        </div>
        <span class="jobs-view__item-date">{{ formatDate(job.created_at) }}</span>
      </li>
    </ul>

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
</style>
