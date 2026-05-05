<script setup lang="ts">
import { computed, shallowRef, watch, onMounted, onUnmounted, onActivated, onDeactivated } from 'vue'
import type { Dimension } from '@/api/reports'

const props = defineProps<{
  dimensions: Dimension[]
}>()

const chartRef = shallowRef<HTMLDivElement | null>(null)
let chartInstance: any = null
let resizeObserver: ResizeObserver | null = null
let echartsModule: any = null

const MAX_DIMENSIONS = 8
const MIN_RADAR_DIMENSIONS = 3

const chartDimensions = computed(() =>
  props.dimensions.slice(0, MAX_DIMENSIONS),
)

const canUseRadar = computed(() =>
  chartDimensions.value.length >= MIN_RADAR_DIMENSIONS,
)

const indicator = computed(() =>
  chartDimensions.value.map(d => ({
    name: d.name.length > 6 ? d.name.slice(0, 6) + '…' : d.name,
    max: 100,
  })),
)

const currentScores = computed(() =>
  chartDimensions.value.map(d => d.score),
)

const jdThresholds = computed(() =>
  chartDimensions.value.map(d => d.threshold),
)

const barCategories = computed(() =>
  chartDimensions.value.map(d => d.name),
)

async function loadECharts() {
  if (echartsModule) return echartsModule

  const echarts = await import('echarts/core')
  const { RadarChart, BarChart } = await import('echarts/charts')
  const { TooltipComponent, LegendComponent, GridComponent } = await import('echarts/components')
  const { CanvasRenderer } = await import('echarts/renderers')

  echarts.use([RadarChart, BarChart, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])
  echartsModule = echarts
  return echarts
}

async function initChart() {
  const el = chartRef.value
  if (!el) return

  const echarts = await loadECharts()

  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }

  chartInstance = echarts.init(el, undefined, { renderer: 'canvas' })

  resizeObserver = new ResizeObserver(() => {
    chartInstance?.resize()
  })
  resizeObserver.observe(el)

  updateChart()
}

function getDarkMode() {
  return document.documentElement.getAttribute('data-theme') !== 'light'
}

function buildRadarOption() {
  const isDark = getDarkMode()

  return {
    tooltip: {
      trigger: 'item',
      backgroundColor: isDark ? '#141516' : '#ffffff',
      borderColor: isDark ? '#23252a' : '#dee2e6',
      textStyle: {
        color: isDark ? '#f7f8f8' : '#212529',
        fontSize: 12,
      },
    },
    legend: {
      bottom: 0,
      textStyle: {
        color: isDark ? '#8a8f98' : '#6c757d',
        fontSize: 11,
      },
      itemWidth: 12,
      itemHeight: 8,
      itemGap: 16,
    },
    radar: {
      indicator: indicator.value,
      shape: 'polygon',
      radius: '65%',
      axisName: {
        color: isDark ? '#d0d6e0' : '#495057',
        fontSize: 11,
      },
      splitArea: {
        areaStyle: {
          color: isDark
            ? ['rgba(255,255,255,0.02)', 'rgba(255,255,255,0.04)']
            : ['rgba(0,0,0,0.02)', 'rgba(0,0,0,0.04)'],
        },
      },
      splitLine: {
        lineStyle: {
          color: isDark ? '#23252a' : '#dee2e6',
        },
      },
      axisLine: {
        lineStyle: {
          color: isDark ? '#23252a' : '#dee2e6',
        },
      },
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: jdThresholds.value,
            name: '岗位要求',
            lineStyle: { color: '#5b8def', width: 2 },
            areaStyle: { color: 'rgba(91, 141, 239, 0.15)' },
            itemStyle: { color: '#5b8def' },
          },
          {
            value: currentScores.value,
            name: '当前能力',
            lineStyle: { color: '#6b75e0', width: 2 },
            areaStyle: { color: 'rgba(107, 117, 224, 0.2)' },
            itemStyle: { color: '#6b75e0' },
          },
        ],
      },
    ],
  }
}

function buildBarOption() {
  const isDark = getDarkMode()
  const inkColor = isDark ? '#f7f8f8' : '#212529'
  const mutedColor = isDark ? '#8a8f98' : '#6c757d'
  const lineColor = isDark ? '#23252a' : '#dee2e6'

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: isDark ? '#141516' : '#ffffff',
      borderColor: isDark ? '#23252a' : '#dee2e6',
      textStyle: { color: inkColor, fontSize: 12 },
    },
    legend: {
      bottom: 0,
      textStyle: { color: mutedColor, fontSize: 11 },
      itemWidth: 12,
      itemHeight: 8,
      itemGap: 16,
    },
    grid: {
      left: 16,
      right: 24,
      top: 16,
      bottom: 40,
      containLabel: true,
    },
    xAxis: {
      type: 'value',
      max: 100,
      axisLabel: { color: mutedColor, fontSize: 11 },
      axisLine: { lineStyle: { color: lineColor } },
      splitLine: { lineStyle: { color: lineColor, type: 'dashed' } },
    },
    yAxis: {
      type: 'category',
      data: barCategories.value,
      axisLabel: { color: inkColor, fontSize: 12, fontWeight: 500 },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    series: [
      {
        name: '岗位要求',
        type: 'bar',
        data: jdThresholds.value,
        barWidth: 10,
        itemStyle: {
          color: '#5b8def',
          borderRadius: [0, 4, 4, 0],
        },
      },
      {
        name: '当前能力',
        type: 'bar',
        data: currentScores.value,
        barWidth: 10,
        itemStyle: {
          color: '#6b75e0',
          borderRadius: [0, 4, 4, 0],
        },
      },
    ],
  }
}

function updateChart() {
  if (!chartInstance) return

  const option = canUseRadar.value
    ? buildRadarOption()
    : buildBarOption()

  chartInstance.setOption(option, true)
}

function cleanup() {
  resizeObserver?.disconnect()
  resizeObserver = null
  chartInstance?.dispose()
  chartInstance = null
}

onMounted(() => {
  initChart()
})

onUnmounted(() => {
  cleanup()
})

onActivated(() => {
  chartInstance?.resize()
})

onDeactivated(() => {
  cleanup()
})

watch(
  () => props.dimensions,
  () => {
    if (chartInstance) {
      updateChart()
    }
  },
  { deep: true },
)
</script>

<template>
  <section class="skills-radar" aria-label="技术栈与能力矩阵">
    <h3 class="skills-radar__title">
      {{ canUseRadar ? '技术栈与能力矩阵' : '技能对比' }}
    </h3>
    <div
      ref="chartRef"
      class="skills-radar__chart"
    />
    <p v-if="!canUseRadar && dimensions.length < MIN_RADAR_DIMENSIONS" class="skills-radar__hint">
      维度不足 3 项，暂以柱状图展示对比
    </p>
    <p v-else-if="dimensions.length > MAX_DIMENSIONS" class="skills-radar__hint">
      仅展示前 {{ MAX_DIMENSIONS }} 项维度，完整列表见下方评分详情
    </p>
  </section>
</template>

<style scoped>
.skills-radar {
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-xl);
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.skills-radar__title {
  margin: 0;
  font-size: var(--font-body-lg-size);
  font-weight: 600;
  color: var(--color-ink);
}

.skills-radar__chart {
  width: 100%;
  min-height: 280px;
  flex: 1;
}

.skills-radar__hint {
  margin: 0;
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
  text-align: center;
}

@media (max-width: 768px) {
  .skills-radar {
    padding: var(--space-md);
  }

  .skills-radar__chart {
    min-height: 240px;
  }
}
</style>
