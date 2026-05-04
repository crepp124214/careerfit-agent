<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAvailabilityStore } from '@/stores/availability'
import { useResumesStore } from '@/stores/resumes'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'
import LoadingCard from '@/components/feedback/LoadingCard.vue'
import EmptyState from '@/components/feedback/EmptyState.vue'
import AppButton from '@/components/common/AppButton.vue'
import AppInput from '@/components/common/AppInput.vue'
import AppTextarea from '@/components/common/AppTextarea.vue'
import Modal from '@/components/common/Modal.vue'

const router = useRouter()
const availability = useAvailabilityStore()
const resumes = useResumesStore()

const showModal = ref(false)
const newName = ref('')
const newContent = ref('')
const submitting = ref(false)

onMounted(() => {
  availability.probe()
  if (availability.states.resumes !== 'unavailable') {
    resumes.load()
  }
})

async function submit() {
  if (!newName.value.trim()) return
  const rawText = newContent.value.trim() || newName.value.trim()
  submitting.value = true
  await resumes.add({
    candidate_name: newName.value.trim(),
    version_label: 'v1',
    raw_text: rawText,
  })
  submitting.value = false
  showModal.value = false
  newName.value = ''
  newContent.value = ''
}

function goToDetail(id: number) {
  router.push({ name: 'resume-detail', params: { id } })
}
</script>

<template>
  <section class="resumes-view" role="main" aria-label="简历版本">
    <header class="resumes-view__header">
      <h1 class="resumes-view__title">简历版本</h1>
      <AppButton
        variant="primary"
        :disabled="availability.states.resumes !== 'ready'"
        @click="showModal = true"
      >
        新建简历
      </AppButton>
    </header>

    <BackendNotReadyNotice
      v-if="availability.states.resumes === 'unavailable'"
      feature="简历管理"
      waitingFor="resumes API"
    />

    <LoadingCard v-else-if="resumes.loading" title="加载简历列表中…" />

    <EmptyState
      v-else-if="resumes.list.length === 0"
      title="还没有简历版本"
      description="添加一个简历版本，系统才能进行匹配分析。"
      action-label="新建简历"
      @action="showModal = true"
    />

    <ul v-else class="resumes-view__list" role="list">
      <li
        v-for="resume in resumes.list"
        :key="resume.id"
        class="resumes-view__item"
        @click="goToDetail(resume.id)"
      >
        <div class="resumes-view__item-main">
          <span class="resumes-view__item-name">{{ resume.candidate_name }} — {{ resume.version_label }}</span>
        </div>
        <span class="resumes-view__item-date">{{ resume.created_at }}</span>
      </li>
    </ul>

    <Modal
      :open="showModal"
      title="新建简历"
      description="填写简历版本名称与内容。"
      @close="showModal = false"
    >
      <div class="resumes-view__form">
        <AppInput
          v-model="newName"
          label="版本名称"
          placeholder="例如：v1 — 面向字节跳动后端"
          :required="true"
        />
        <AppTextarea
          v-model="newContent"
          label="简历内容（可选）"
          placeholder="粘贴完整简历内容…"
          :min-height="'200px'"
        />
      </div>
      <template #footer>
        <AppButton variant="tertiary" @click="showModal = false">取消</AppButton>
        <AppButton
          variant="primary"
          :loading="submitting"
          :disabled="!newName.trim()"
          @click="submit"
        >
          保存
        </AppButton>
      </template>
    </Modal>
  </section>
</template>

<style scoped>
.resumes-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  max-width: 960px;
}

.resumes-view__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-md);
}

.resumes-view__title {
  margin: 0;
  font-size: var(--font-headline-size);
  font-weight: var(--font-headline-weight);
  line-height: var(--font-headline-line);
  letter-spacing: var(--font-headline-letter);
}

.resumes-view__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.resumes-view__item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  cursor: pointer;
  transition: background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.resumes-view__item:hover {
  background-color: var(--color-surface-2);
}

.resumes-view__item-main {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.resumes-view__item-name {
  font-size: var(--font-body-size);
  font-weight: 500;
  color: var(--color-ink);
}

.resumes-view__item-date {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
  flex-shrink: 0;
}

.resumes-view__form {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}
</style>
