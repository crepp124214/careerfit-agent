<script setup lang="ts">
import { computed } from 'vue'
import type { HistoryItem } from '@/api/reports'

const props = withDefaults(
  defineProps<{
    items: HistoryItem[]
    height?: number
  }>(),
  {
    height: 200,
  },
)

const chartWidth = 600
const chartHeight = computed(() => props.height)
const padding = { top: 20, right: 20, bottom: 40, left: 50 }

const innerWidth = computed(() => chartWidth - padding.left - padding.right)
const innerHeight = computed(() => chartHeight.value - padding.top - padding.bottom)

const scores = computed(() => props.items.map((item) => item.finalScore))
const minScore = computed(() => Math.max(0, Math.min(...scores.value) - 10))
const maxScore = computed(() => Math.min(100, Math.max(...scores.value) + 10))

const points = computed(() => {
  if (props.items.length === 0) return []

  return props.items.map((item, index) => {
    const x = padding.left + (index / Math.max(1, props.items.length - 1)) * innerWidth.value
    const normalizedScore = (item.finalScore - minScore.value) / (maxScore.value - minScore.value)
    const y = padding.top + innerHeight.value * (1 - normalizedScore)
    return { x, y, item }
  })
})

const pathD = computed(() => {
  if (points.value.length === 0) return ''
  return points.value.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
})

const areaD = computed(() => {
  if (points.value.length === 0) return ''
  const bottomY = padding.top + innerHeight.value
  const path = points.value.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
  const lastX = points.value[points.value.length - 1]!.x
  const firstX = points.value[0]!.x
  return `${path} L ${lastX} ${bottomY} L ${firstX} ${bottomY} Z`
})

const yTicks = computed(() => {
  const ticks: number[] = []
  const step = 20
  for (let i = Math.ceil(minScore.value / step) * step; i <= maxScore.value; i += step) {
    ticks.push(i)
  }
  return ticks
})

function formatScore(score: number): string {
  return Math.round(score).toString()
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}
</script>

<template>
  <div class="score-trend-chart" role="img" aria-label="分数趋势图表">
    <svg
      :viewBox="`0 0 ${chartWidth} ${chartHeight}`"
      class="score-trend-chart__svg"
      preserveAspectRatio="xMidYMid meet"
    >
      <defs>
        <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="var(--color-primary)" stop-opacity="0.3" />
          <stop offset="100%" stop-color="var(--color-primary)" stop-opacity="0.05" />
        </linearGradient>
      </defs>

      <g class="score-trend-chart__grid">
        <line
          v-for="tick in yTicks"
          :key="`grid-${tick}`"
          :x1="padding.left"
          :x2="chartWidth - padding.right"
          :y1="padding.top + innerHeight * (1 - (tick - minScore) / (maxScore - minScore))"
          :y2="padding.top + innerHeight * (1 - (tick - minScore) / (maxScore - minScore))"
          class="score-trend-chart__grid-line"
        />
      </g>

      <g class="score-trend-chart__y-axis">
        <text
          v-for="tick in yTicks"
          :key="`y-${tick}`"
          :x="padding.left - 10"
          :y="padding.top + innerHeight * (1 - (tick - minScore) / (maxScore - minScore)) + 4"
          class="score-trend-chart__axis-label"
          text-anchor="end"
        >
          {{ tick }}
        </text>
      </g>

      <path v-if="areaD" :d="areaD" class="score-trend-chart__area" fill="url(#areaGradient)" />

      <path v-if="pathD" :d="pathD" class="score-trend-chart__line" fill="none" />

      <g class="score-trend-chart__points">
        <g v-for="(point, index) in points" :key="index">
          <circle
            :cx="point.x"
            :cy="point.y"
            r="6"
            class="score-trend-chart__point"
          />
          <text
            :x="point.x"
            :y="point.y - 12"
            class="score-trend-chart__point-label"
            text-anchor="middle"
          >
            {{ formatScore(point.item.finalScore) }}
          </text>
        </g>
      </g>

      <g class="score-trend-chart__x-axis">
        <text
          v-for="(point, index) in points"
          :key="`x-${index}`"
          :x="point.x"
          :y="chartHeight - 10"
          class="score-trend-chart__axis-label"
          text-anchor="middle"
        >
          {{ formatDate(point.item.createdAt) }}
        </text>
      </g>
    </svg>

    <div v-if="items.length === 0" class="score-trend-chart__empty">
      <p>暂无数据</p>
    </div>
  </div>
</template>

<style scoped>
.score-trend-chart {
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  padding: var(--space-md);
  position: relative;
}

.score-trend-chart__svg {
  width: 100%;
  height: auto;
  display: block;
}

.score-trend-chart__grid-line {
  stroke: var(--color-hairline);
  stroke-dasharray: 4 4;
  opacity: 0.5;
}

.score-trend-chart__axis-label {
  font-size: 12px;
  fill: var(--color-ink-muted);
  font-family: var(--font-family-sans);
}

.score-trend-chart__line {
  stroke: var(--color-primary);
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.score-trend-chart__point {
  fill: var(--color-primary);
  stroke: var(--color-surface-1);
  stroke-width: 2;
  transition: r 0.15s ease;
}

.score-trend-chart__point:hover {
  r: 8;
}

.score-trend-chart__point-label {
  font-size: 11px;
  font-weight: 600;
  fill: var(--color-ink);
  font-family: var(--font-family-sans);
}

.score-trend-chart__empty {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.score-trend-chart__empty p {
  margin: 0;
  color: var(--color-ink-muted);
  font-size: var(--font-body-sm-size);
}

@media (max-width: 640px) {
  .score-trend-chart {
    padding: var(--space-sm);
  }

  .score-trend-chart__axis-label {
    font-size: 10px;
  }

  .score-trend-chart__point-label {
    font-size: 10px;
  }
}
</style>
