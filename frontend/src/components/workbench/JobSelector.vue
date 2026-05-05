<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAvailabilityStore } from '@/stores/availability'
import { useJobsStore } from '@/stores/jobs'
import { Briefcase, Search, X } from 'lucide-vue-next'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'
import LoadingCard from '@/components/feedback/LoadingCard.vue'
import EmptyState from '@/components/feedback/EmptyState.vue'

const availability = useAvailabilityStore()
const jobs = useJobsStore()

const searchQuery = ref('')
const searchInput = ref<HTMLInputElement | null>(null)

const isUnavailable = computed(() => availability.states.jobs === 'unavailable')
const isLoading = computed(() => jobs.loading)
const isEmpty = computed(() => !isUnavailable.value && !isLoading.value && jobs.list.length === 0)

const filteredJobs = computed(() => {
  if (!searchQuery.value.trim()) return jobs.list
  const query = searchQuery.value.toLowerCase()
  return jobs.list.filter(job =>
    job.title.toLowerCase().includes(query) ||
    (job.profile?.job_family && String(job.profile.job_family).toLowerCase().includes(query))
  )
})

const showSearch = computed(() => !isUnavailable.value && !isLoading.value && !isEmpty.value && jobs.list.length > 5)

const emit = defineEmits<{
  (e: 'create'): void
}>()

function clearSearch() {
  searchQuery.value = ''
  searchInput.value?.focus()
}
</script>

<template>
  <section class="job-selector" aria-label="岗位选择">
    <div class="job-selector__header">
      <h2 class="job-selector__title">目标岗位</h2>
      <span v-if="!isEmpty && !isLoading" class="job-selector__count">{{ jobs.list.length }} 个</span>
    </div>

    <BackendNotReadyNotice
      v-if="isUnavailable"
      feature="岗位列表"
      waitingFor="jobs API"
    />

    <LoadingCard v-else-if="isLoading" title="加载岗位列表中…" />

    <EmptyState
      v-else-if="isEmpty"
      :icon="Briefcase"
      title="还没有目标岗位"
      description="添加一个目标岗位，系统才能进行匹配分析。"
      action-label="新建岗位"
      @action="emit('create')"
    />

    <template v-else>
      <div v-if="showSearch" class="job-selector__search">
        <Search class="job-selector__search-icon" :size="16" aria-hidden="true" />
        <input
          ref="searchInput"
          v-model="searchQuery"
          type="text"
          class="job-selector__search-input"
          placeholder="搜索岗位..."
          aria-label="搜索岗位"
        />
        <button
          v-if="searchQuery"
          type="button"
          class="job-selector__search-clear"
          aria-label="清除搜索"
          @click="clearSearch"
        >
          <X :size="14" aria-hidden="true" />
        </button>
      </div>

      <p v-if="searchQuery && filteredJobs.length === 0" class="job-selector__no-results">
        没有找到匹配「{{ searchQuery }}」的岗位
      </p>

      <ul v-else class="job-selector__list" role="listbox" aria-label="岗位列表">
        <li
          v-for="job in filteredJobs"
          :key="job.id"
          class="job-selector__item"
          :class="{ 'job-selector__item--selected': jobs.selectedId === job.id }"
          role="option"
          :aria-selected="jobs.selectedId === job.id"
          @click="jobs.select(job.id)"
        >
          <span class="job-selector__name">{{ job.title }}</span>
          <span v-if="job.profile?.job_family" class="job-selector__meta">
            {{ job.profile.job_family }}
          </span>
        </li>
      </ul>
    </template>
  </section>
</template>

<style scoped>
.job-selector {
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

.job-selector:hover {
  border-color: var(--color-hairline-strong);
}

.job-selector__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.job-selector__title {
  margin: 0;
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
  line-height: var(--font-card-title-line);
  color: var(--color-ink);
}

.job-selector__count {
  font-size: var(--font-caption-size);
  color: var(--color-ink-tertiary);
}

.job-selector__search {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-sm);
  background-color: var(--color-surface-2);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-md);
  transition: border-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.job-selector__search:focus-within {
  border-color: var(--color-primary);
}

.job-selector__search-icon {
  flex-shrink: 0;
  color: var(--color-ink-tertiary);
}

.job-selector__search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: var(--font-body-size);
  color: var(--color-ink);
  outline: none;
  min-width: 0;
}

.job-selector__search-input::placeholder {
  color: var(--color-ink-tertiary);
}

.job-selector__search-clear {
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

.job-selector__search-clear:hover {
  color: var(--color-ink);
}

.job-selector__no-results {
  margin: 0;
  padding: var(--space-lg);
  text-align: center;
  color: var(--color-ink-subtle);
  font-size: var(--font-body-sm-size);
}

.job-selector__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.job-selector__item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 10px 12px;
  border-radius: var(--rounded-sm);
  cursor: pointer;
  border: 1px solid transparent;
  transition: background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.job-selector__item:hover {
  background-color: var(--color-surface-2);
}

.job-selector__item:active {
  transform: scale(0.99);
}

.job-selector__item--selected {
  background-color: var(--color-surface-2);
  border-color: var(--color-hairline-strong);
}

.job-selector__name {
  font-size: var(--font-body-size);
  font-weight: 500;
  color: var(--color-ink);
}

.job-selector__meta {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

@media (max-width: 480px) {
  .job-selector {
    padding: var(--space-md);
  }

  .job-selector__item {
    min-height: 44px;
  }
}
</style>
