<script setup lang="ts">
import { computed } from 'vue'
import { useAvailabilityStore } from '@/stores/availability'
import { useJobsStore } from '@/stores/jobs'
import { Briefcase } from 'lucide-vue-next'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'
import LoadingCard from '@/components/feedback/LoadingCard.vue'
import EmptyState from '@/components/feedback/EmptyState.vue'

const availability = useAvailabilityStore()
const jobs = useJobsStore()

const isUnavailable = computed(() => availability.states.jobs === 'unavailable')
const isLoading = computed(() => jobs.loading)
const isEmpty = computed(() => !isUnavailable.value && !isLoading.value && jobs.list.length === 0)

const emit = defineEmits<{
  (e: 'create'): void
}>()
</script>

<template>
  <section class="job-selector" aria-label="岗位选择">
    <h2 class="job-selector__title">目标岗位</h2>

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

    <ul v-else class="job-selector__list" role="listbox" aria-label="岗位列表">
      <li
        v-for="job in jobs.list"
        :key="job.id"
        class="job-selector__item"
        :class="{ 'job-selector__item--selected': jobs.selectedId === job.id }"
        role="option"
        :aria-selected="jobs.selectedId === job.id"
        @click="jobs.select(job.id)"
      >
        <span class="job-selector__name">{{ job.title }}</span>
      </li>
    </ul>
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

.job-selector__title {
  margin: 0;
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
  line-height: var(--font-card-title-line);
  color: var(--color-ink);
}

.job-selector__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
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

.job-selector__company {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}
</style>
