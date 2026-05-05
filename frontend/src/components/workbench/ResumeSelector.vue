<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAvailabilityStore } from '@/stores/availability'
import { useResumesStore } from '@/stores/resumes'
import { FileText, Search, X } from 'lucide-vue-next'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'
import LoadingCard from '@/components/feedback/LoadingCard.vue'
import EmptyState from '@/components/feedback/EmptyState.vue'
import { formatDate } from '@/utils/format'

const availability = useAvailabilityStore()
const resumes = useResumesStore()

const searchQuery = ref('')
const searchInput = ref<HTMLInputElement | null>(null)

const isUnavailable = computed(() => availability.states.resumes === 'unavailable')
const isLoading = computed(() => resumes.loading)
const isEmpty = computed(() => !isUnavailable.value && !isLoading.value && resumes.list.length === 0)

const filteredResumes = computed(() => {
  if (!searchQuery.value.trim()) return resumes.list
  const query = searchQuery.value.toLowerCase()
  return resumes.list.filter(resume =>
    resume.candidate_name.toLowerCase().includes(query) ||
    resume.version_label.toLowerCase().includes(query)
  )
})

const showSearch = computed(() => !isUnavailable.value && !isLoading.value && !isEmpty.value && resumes.list.length > 5)

const emit = defineEmits<{
  (e: 'create'): void
}>()

function clearSearch() {
  searchQuery.value = ''
  searchInput.value?.focus()
}
</script>

<template>
  <section class="resume-selector" aria-label="简历选择">
    <div class="resume-selector__header">
      <h2 class="resume-selector__title">简历版本</h2>
      <span v-if="!isEmpty && !isLoading" class="resume-selector__count">{{ resumes.list.length }} 个</span>
    </div>

    <BackendNotReadyNotice
      v-if="isUnavailable"
      feature="简历列表"
      waitingFor="resumes API"
    />

    <LoadingCard v-else-if="isLoading" title="加载简历列表中…" />

    <EmptyState
      v-else-if="isEmpty"
      :icon="FileText"
      title="还没有简历版本"
      description="添加一个简历版本，系统才能进行匹配分析。"
      action-label="新建简历"
      @action="emit('create')"
    />

    <template v-else>
      <div v-if="showSearch" class="resume-selector__search">
        <Search class="resume-selector__search-icon" :size="16" aria-hidden="true" />
        <input
          ref="searchInput"
          v-model="searchQuery"
          type="text"
          class="resume-selector__search-input"
          placeholder="搜索简历..."
          aria-label="搜索简历"
        />
        <button
          v-if="searchQuery"
          type="button"
          class="resume-selector__search-clear"
          aria-label="清除搜索"
          @click="clearSearch"
        >
          <X :size="14" aria-hidden="true" />
        </button>
      </div>

      <p v-if="searchQuery && filteredResumes.length === 0" class="resume-selector__no-results">
        没有找到匹配「{{ searchQuery }}」的简历
      </p>

      <ul v-else class="resume-selector__list" role="listbox" aria-label="简历列表">
        <li
          v-for="resume in filteredResumes"
          :key="resume.id"
          class="resume-selector__item"
          :class="{ 'resume-selector__item--selected': resumes.selectedId === resume.id }"
          role="option"
          :aria-selected="resumes.selectedId === resume.id"
          @click="resumes.select(resume.id)"
        >
          <span class="resume-selector__name">{{ resume.candidate_name }} — {{ resume.version_label }}</span>
          <span class="resume-selector__date">{{ formatDate(resume.created_at) }}</span>
        </li>
      </ul>
    </template>
  </section>
</template>

<style scoped>
.resume-selector {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  padding: var(--space-lg);
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  min-height: 200px;
  transition: border-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.resume-selector:hover {
  border-color: var(--color-hairline-strong);
}

.resume-selector__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.resume-selector__title {
  margin: 0;
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
  line-height: var(--font-card-title-line);
  color: var(--color-ink);
}

.resume-selector__count {
  font-size: var(--font-caption-size);
  color: var(--color-ink-tertiary);
}

.resume-selector__search {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-sm);
  background-color: var(--color-surface-2);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-md);
  transition: border-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.resume-selector__search:focus-within {
  border-color: var(--color-primary);
}

.resume-selector__search-icon {
  flex-shrink: 0;
  color: var(--color-ink-tertiary);
}

.resume-selector__search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: var(--font-body-size);
  color: var(--color-ink);
  outline: none;
  min-width: 0;
}

.resume-selector__search-input::placeholder {
  color: var(--color-ink-tertiary);
}

.resume-selector__search-clear {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2px;
  background: none;
  border: none;
  color: var(--color-ink-tertiary);
  cursor: pointer;
  border-radius: var(--rounded-xs);
  transition: color var(--motion-duration-fast) var(--motion-easing-standard);
}

.resume-selector__search-clear:hover {
  color: var(--color-ink);
}

.resume-selector__no-results {
  margin: 0;
  padding: var(--space-lg);
  text-align: center;
  color: var(--color-ink-subtle);
  font-size: var(--font-body-sm-size);
}

.resume-selector__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.resume-selector__item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 10px 12px;
  border-radius: var(--rounded-sm);
  cursor: pointer;
  border: 1px solid transparent;
  transition: background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.resume-selector__item:hover {
  background-color: var(--color-surface-2);
}

.resume-selector__item:active {
  transform: scale(0.99);
}

.resume-selector__item--selected {
  background-color: var(--color-surface-2);
  border-color: var(--color-hairline-strong);
}

.resume-selector__name {
  font-size: var(--font-body-size);
  font-weight: 500;
  color: var(--color-ink);
}

.resume-selector__date {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

@media (max-width: 480px) {
  .resume-selector {
    padding: var(--space-md);
  }

  .resume-selector__item {
    min-height: 44px;
  }
}
</style>
