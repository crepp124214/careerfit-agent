<script setup lang="ts">
import { computed } from 'vue'
import { useAvailabilityStore } from '@/stores/availability'
import BackendNotReadyNotice from '@/components/feedback/BackendNotReadyNotice.vue'
import EmptyState from '@/components/feedback/EmptyState.vue'
import AppButton from '@/components/common/AppButton.vue'

const availability = useAvailabilityStore()
const isUnavailable = computed(() => availability.states.learning === 'unavailable')
</script>

<template>
  <section class="learning-view" role="main" aria-label="学习任务">
    <h1 class="learning-view__title">学习任务</h1>

    <BackendNotReadyNotice
      v-if="isUnavailable"
      feature="学习任务"
      waitingFor="learning 接口"
    />

    <template v-else>
      <AppButton variant="primary" disabled>
        按当前缺口生成学习任务
      </AppButton>

      <EmptyState
        title="暂无学习任务"
        description="完成分析后，系统将根据你的能力缺口生成个性化学习计划。"
      />
    </template>
  </section>
</template>

<style scoped>
.learning-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  max-width: 960px;
}

.learning-view__title {
  margin: 0;
  font-size: var(--font-headline-size);
  font-weight: var(--font-headline-weight);
  line-height: var(--font-headline-line);
}
</style>
