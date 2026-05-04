<script setup lang="ts">
import { computed } from 'vue'
import { useAvailabilityStore } from '@/stores/availability'
import { useResumesStore } from '@/stores/resumes'
import { FileText } from 'lucide-vue-next'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'
import LoadingCard from '@/components/feedback/LoadingCard.vue'
import EmptyState from '@/components/feedback/EmptyState.vue'

const availability = useAvailabilityStore()
const resumes = useResumesStore()

const isUnavailable = computed(() => availability.states.resumes === 'unavailable')
const isLoading = computed(() => resumes.loading)
const isEmpty = computed(() => !isUnavailable.value && !isLoading.value && resumes.list.length === 0)

const emit = defineEmits<{
  (e: 'create'): void
}>()
</script>

<template>
  <section class="resume-selector" aria-label="简历选择">
    <h2 class="resume-selector__title">简历版本</h2>

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

    <ul v-else class="resume-selector__list" role="listbox" aria-label="简历列表">
      <li
        v-for="resume in resumes.list"
        :key="resume.id"
        class="resume-selector__item"
        :class="{ 'resume-selector__item--selected': resumes.selectedId === resume.id }"
        role="option"
        :aria-selected="resumes.selectedId === resume.id"
        @click="resumes.select(resume.id)"
      >
        <span class="resume-selector__name">{{ resume.candidate_name }} — {{ resume.version_label }}</span>
        <span class="resume-selector__date">{{ resume.created_at }}</span>
      </li>
    </ul>
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

.resume-selector__title {
  margin: 0;
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
  line-height: var(--font-card-title-line);
  color: var(--color-ink);
}

.resume-selector__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
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
</style>
