<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Dimension } from '@/api/reports'
import ScoringDimensionCard from './ScoringDimensionCard.vue'

const props = defineProps<{
  dimensions: Dimension[]
  maxVisible?: number
}>()

const maxVisible = computed(() => props.maxVisible ?? 5)
const showAll = ref(false)

const visibleDimensions = computed(() => {
  if (showAll.value || props.dimensions.length <= maxVisible.value) {
    return props.dimensions
  }
  return props.dimensions.slice(0, maxVisible.value)
})

const hiddenCount = computed(() => {
  return props.dimensions.length - maxVisible.value
})

const hasMore = computed(() => props.dimensions.length > maxVisible.value)

function toggleShowAll() {
  showAll.value = !showAll.value
}

const highRiskCount = computed(() => 
  props.dimensions.filter(d => d.riskLevel === 'high').length
)

const mediumRiskCount = computed(() => 
  props.dimensions.filter(d => d.riskLevel === 'medium').length
)
</script>

<template>
  <section class="score-grid" aria-label="评分维度">
    <header class="score-grid__header">
      <h3 class="score-grid__title">评分维度</h3>
      <div class="score-grid__stats">
        <span class="score-grid__count">{{ dimensions.length }} 项</span>
        <span v-if="highRiskCount > 0" class="score-grid__risk score-grid__risk--high">
          {{ highRiskCount }} 高风险
        </span>
        <span v-if="mediumRiskCount > 0" class="score-grid__risk score-grid__risk--medium">
          {{ mediumRiskCount }} 需关注
        </span>
      </div>
    </header>

    <div v-if="dimensions.length === 0" class="score-grid__empty">
      <p>暂无评分维度数据</p>
    </div>

    <div v-else class="score-grid__grid">
      <ScoringDimensionCard
        v-for="(dimension, i) in visibleDimensions"
        :key="i"
        :dimension="dimension"
      />
    </div>

    <div v-if="hasMore" class="score-grid__more">
      <button
        type="button"
        class="score-grid__toggle"
        @click="toggleShowAll"
      >
        <template v-if="showAll">
          收起（隐藏 {{ hiddenCount }} 项）
        </template>
        <template v-else>
          展开全部（还有 {{ hiddenCount }} 项）
        </template>
      </button>
    </div>
  </section>
</template>

<style scoped>
.score-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.score-grid__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-md);
}

.score-grid__title {
  margin: 0;
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
  line-height: var(--font-card-title-line);
  color: var(--color-ink);
}

.score-grid__stats {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: var(--font-caption-size);
}

.score-grid__count {
  color: var(--color-ink-subtle);
}

.score-grid__risk {
  padding: 2px 8px;
  border-radius: var(--rounded-sm);
  font-weight: 500;
}

.score-grid__risk--high {
  background-color: rgba(235, 87, 87, 0.15);
  color: #eb5757;
}

.score-grid__risk--medium {
  background-color: rgba(242, 153, 74, 0.15);
  color: #f2994a;
}

.score-grid__empty {
  padding: var(--space-lg);
  text-align: center;
  color: var(--color-ink-subtle);
  font-size: var(--font-body-size);
}

.score-grid__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-md);
}

.score-grid__more {
  display: flex;
  justify-content: center;
  padding-top: var(--space-sm);
}

.score-grid__toggle {
  padding: 8px 16px;
  background-color: var(--color-surface-2);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-md);
  color: var(--color-ink-muted);
  font-size: var(--font-caption-size);
  cursor: pointer;
  transition: all var(--motion-duration-fast) var(--motion-easing-standard);
}

.score-grid__toggle:hover {
  background-color: var(--color-surface-3);
  color: var(--color-ink);
}

@media (max-width: 768px) {
  .score-grid__header {
    flex-direction: column;
    align-items: flex-start;
  }

  .score-grid__grid {
    grid-template-columns: 1fr;
  }

  .score-grid__toggle {
    min-height: 44px;
    width: 100%;
  }
}
</style>
