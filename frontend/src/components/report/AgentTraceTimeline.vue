<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { AgentNode } from '@/api/agentRuns'
import StatusBadge from '@/components/common/StatusBadge.vue'

const props = defineProps<{
  nodes: AgentNode[]
}>()

const COLLAPSED_COUNT = 5
const expanded = ref(false)

onMounted(() => {
  for (const node of props.nodes) {
    if (node.raw_jd || node.raw_resume) {
      console.warn(
        '[AgentTraceTimeline] raw_jd/raw_resume detected — these fields are desensitized and will not be rendered',
      )
    }
  }
})

const visibleNodes = computed(() => {
  if (expanded.value) return props.nodes
  return props.nodes.slice(0, COLLAPSED_COUNT)
})

const hasMore = computed(() => props.nodes.length > COLLAPSED_COUNT)

function toggle() {
  expanded.value = !expanded.value
}

function statusLabel(status: string) {
  switch (status) {
    case 'success':
      return '成功'
    case 'failed':
      return '失败'
    case 'running':
      return '进行中'
    default:
      return status
  }
}

function statusTone(status: string): 'risk-low' | 'risk-high' | 'info' {
  switch (status) {
    case 'success':
      return 'risk-low'
    case 'failed':
      return 'risk-high'
    case 'running':
      return 'info'
    default:
      return 'info'
  }
}

function formatDuration(ms: number) {
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(1)}s`
}
</script>

<template>
  <section class="agent-trace" aria-label="Agent 运行轨迹">
    <h3 class="agent-trace__title">Agent 运行轨迹</h3>

    <ul class="agent-trace__list">
      <li
        v-for="(node, i) in visibleNodes"
        :key="i"
        class="agent-trace__row"
      >
        <div class="agent-trace__row-header">
          <span class="agent-trace__node-name">{{ node.name }}</span>
          <div class="agent-trace__badges">
            <StatusBadge :tone="statusTone(node.status)">
              {{ statusLabel(node.status) }}
            </StatusBadge>
            <span class="agent-trace__duration">{{ formatDuration(node.duration) }}</span>
          </div>
        </div>

        <p class="agent-trace__summary">{{ node.summary }}</p>

        <div class="agent-trace__meta">
          <span v-if="node.length" class="agent-trace__meta-item">
            长度：{{ node.length }}
          </span>
          <span v-if="node.field_names?.length" class="agent-trace__meta-item">
            字段：{{ node.field_names.join(', ') }}
          </span>
        </div>

        <p v-if="node.error" class="agent-trace__error">
          错误：{{ node.error }}
        </p>
      </li>
    </ul>

    <button
      v-if="hasMore"
      type="button"
      class="agent-trace__toggle"
      @click="toggle"
    >
      {{ expanded ? '收起' : `展开全部 ${nodes.length} 个节点` }}
    </button>
  </section>
</template>

<style scoped>
.agent-trace {
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.agent-trace__title {
  margin: 0;
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
  line-height: var(--font-card-title-line);
}

.agent-trace__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.agent-trace__row {
  background-color: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-sm);
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-xxs);
}

.agent-trace__row-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-sm);
}

.agent-trace__node-name {
  font-size: var(--font-body-size);
  font-weight: 500;
  color: var(--color-ink);
}

.agent-trace__badges {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.agent-trace__duration {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

.agent-trace__summary {
  margin: 0;
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-muted);
  line-height: var(--font-body-sm-line);
}

.agent-trace__meta {
  display: flex;
  gap: var(--space-md);
  flex-wrap: wrap;
}

.agent-trace__meta-item {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

.agent-trace__error {
  margin: 0;
  font-size: var(--font-caption-size);
  color: var(--color-risk-high);
}

.agent-trace__toggle {
  align-self: flex-start;
  background: transparent;
  border: 1px solid var(--color-hairline);
  color: var(--color-ink-muted);
  font-size: var(--font-caption-size);
  padding: 4px 12px;
  border-radius: var(--rounded-sm);
  cursor: pointer;
  transition: background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.agent-trace__toggle:hover {
  background-color: var(--color-surface-2);
}
</style>
