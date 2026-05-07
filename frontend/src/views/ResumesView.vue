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
import { formatDate } from '@/utils/format'

const router = useRouter()
const availability = useAvailabilityStore()
const resumes = useResumesStore()

const showModal = ref(false)
const newName = ref('')
const newContent = ref('')
const submitting = ref(false)
const uploadMode = ref<'paste' | 'upload'>('paste')
const uploadFile = ref<File | null>(null)
const uploadDragOver = ref(false)
const uploadError = ref('')
const uploading = ref(false)
const uploadProgress = ref(0)

const ALLOWED_TYPES = '.pdf,.docx'

onMounted(async () => {
  await availability.probe()
  if (availability.states.resumes === 'ready') {
    resumes.load()
  }
})

function resetForm() {
  newName.value = ''
  newContent.value = ''
  uploadFile.value = null
  uploadError.value = ''
  uploadProgress.value = 0
  uploadMode.value = 'paste'
}

function onFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) validateAndSetFile(file)
}

function onDragOver(event: DragEvent) {
  event.preventDefault()
  uploadDragOver.value = true
}

function onDragLeave() {
  uploadDragOver.value = false
}

function onDrop(event: DragEvent) {
  event.preventDefault()
  uploadDragOver.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file) validateAndSetFile(file)
}

function validateAndSetFile(file: File) {
  const ext = '.' + file.name.split('.').pop()?.toLowerCase()
  if (!['.pdf', '.docx'].includes(ext)) {
    uploadError.value = '仅支持 PDF 和 DOCX 格式'
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    uploadError.value = '文件大小不能超过 5MB'
    return
  }
  uploadError.value = ''
  uploadFile.value = file
}

async function submit() {
  if (uploadMode.value === 'upload' && uploadFile.value) {
    submitting.value = true
    await resumes.upload(uploadFile.value, newName.value.trim() || undefined)
    submitting.value = false
    showModal.value = false
    resetForm()
    return
  }

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
  resetForm()
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
        <span class="resumes-view__item-date">{{ formatDate(resume.created_at) }}</span>
      </li>
    </ul>

    <Modal
      :open="showModal"
      title="新建简历"
      description="粘贴简历内容或上传文件。"
      @close="showModal = false"
    >
      <div class="resumes-view__form">
        <AppInput
          v-model="newName"
          label="版本名称"
          placeholder="例如：v1 — 面向字节跳动后端"
          :required="true"
        />

        <div class="resumes-view__mode-tabs" role="tablist">
          <button
            class="resumes-view__mode-tab"
            :class="{ 'resumes-view__mode-tab--active': uploadMode === 'paste' }"
            role="tab"
            :aria-selected="uploadMode === 'paste'"
            @click="uploadMode = 'paste'"
          >
            粘贴内容
          </button>
          <button
            class="resumes-view__mode-tab"
            :class="{ 'resumes-view__mode-tab--active': uploadMode === 'upload' }"
            role="tab"
            :aria-selected="uploadMode === 'upload'"
            @click="uploadMode = 'upload'"
          >
            上传文件
          </button>
        </div>

        <template v-if="uploadMode === 'paste'">
          <AppTextarea
            v-model="newContent"
            label="简历内容（可选）"
            placeholder="粘贴完整简历内容…"
            :min-height="'200px'"
          />
        </template>

        <template v-else>
          <div
            class="resumes-view__dropzone"
            :class="{ 'resumes-view__dropzone--dragover': uploadDragOver, 'resumes-view__dropzone--has-file': uploadFile }"
            @dragover="onDragOver"
            @dragleave="onDragLeave"
            @drop="onDrop"
          >
            <template v-if="!uploadFile">
              <p class="resumes-view__dropzone-text">拖拽 PDF 或 DOCX 文件到此处</p>
              <p class="resumes-view__dropzone-or">或</p>
              <label class="resumes-view__dropzone-label">
                <input
                  type="file"
                  :accept="ALLOWED_TYPES"
                  class="resumes-view__dropzone-input"
                  @change="onFileSelect"
                >
                <span class="resumes-view__dropzone-button">选择文件</span>
              </label>
            </template>
            <template v-else>
              <p class="resumes-view__file-selected">{{ uploadFile.name }}</p>
              <p class="resumes-view__file-size">{{ (uploadFile.size / 1024).toFixed(1) }} KB</p>
              <AppButton variant="tertiary" @click="uploadFile = null">重新选择</AppButton>
            </template>
          </div>
          <p v-if="uploadError" class="resumes-view__upload-error" role="alert">{{ uploadError }}</p>
        </template>
      </div>

      <template #footer>
        <AppButton variant="tertiary" @click="showModal = false">取消</AppButton>
        <AppButton
          variant="primary"
          :loading="submitting"
          :disabled="
            uploading ||
            (uploadMode === 'paste' && !newName.trim()) ||
            (uploadMode === 'upload' && !uploadFile)
          "
          @click="submit"
        >
          {{ uploadMode === 'upload' ? '上传并保存' : '保存' }}
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
  transition:
    background-color var(--motion-duration-fast) var(--motion-easing-standard),
    border-color var(--motion-duration-fast) var(--motion-easing-standard),
    box-shadow var(--motion-duration-fast) var(--motion-easing-standard);
}

.resumes-view__item:hover {
  background-color: var(--color-surface-2);
  border-color: var(--color-hairline-strong);
  box-shadow: var(--shadow-sm);
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

.resumes-view__mode-tabs {
  display: flex;
  gap: 0;
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-sm);
  overflow: hidden;
}

.resumes-view__mode-tab {
  flex: 1;
  padding: var(--space-sm) var(--space-md);
  font-size: var(--font-body-sm-size);
  border: none;
  background: var(--color-canvas);
  color: var(--color-ink-muted);
  cursor: pointer;
  transition: background var(--motion-duration-fast) var(--motion-easing-standard);
}

.resumes-view__mode-tab--active {
  background: var(--color-surface-2);
  color: var(--color-ink);
  font-weight: 500;
}

.resumes-view__dropzone {
  border: 2px dashed var(--color-hairline-strong);
  border-radius: var(--rounded-md);
  padding: var(--space-lg);
  text-align: center;
  transition: border-color var(--motion-duration-fast) var(--motion-easing-standard);
  cursor: pointer;
}

.resumes-view__dropzone:hover,
.resumes-view__dropzone--dragover {
  border-color: var(--color-accent);
  background-color: var(--color-accent-subtle);
}

.resumes-view__dropzone--has-file {
  border-style: solid;
  border-color: var(--color-risk-low, #16a34a);
}

.resumes-view__dropzone-text {
  margin: 0;
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-muted);
}

.resumes-view__dropzone-or {
  margin: var(--space-xs) 0;
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

.resumes-view__dropzone-label {
  cursor: pointer;
}

.resumes-view__dropzone-input {
  display: none;
}

.resumes-view__dropzone-button {
  display: inline-block;
  padding: var(--space-xs) var(--space-md);
  font-size: var(--font-body-sm-size);
  background: var(--color-surface-2);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-sm);
  transition: background var(--motion-duration-fast) var(--motion-easing-standard);
}

.resumes-view__dropzone-button:hover {
  background: var(--color-surface-3);
}

.resumes-view__file-selected {
  margin: 0;
  font-weight: 500;
  color: var(--color-ink);
}

.resumes-view__file-size {
  margin: var(--space-xxs) 0 var(--space-sm);
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

.resumes-view__upload-error {
  margin: 0;
  font-size: var(--font-caption-size);
  color: var(--color-risk-high);
}
</style>
