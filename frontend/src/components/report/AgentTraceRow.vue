<script setup lang="ts">
import type { AgentNode } from '@/api/agentRuns'
import StatusBadge from '@/components/common/StatusBadge.vue'

defineProps<{
  node: AgentNode
}>()

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
  <div class="agent-trace-row">
    <div class="agent-trace-row__header">
      <span class="agent-trace-row__name">{{ node.name }}</span>
      <div class="agent-trace-row__badges">
        <StatusBadge :tone="statusTone(node.status)">
          {{ statusLabel(node.status) }}
        </StatusBadge>
        <span class="agent-trace-row__duration">{{ formatDuration(node.duration) }}</span>
      </div>
    </div>

    <p class="agent-trace-row__summary">{{ node.summary }}</p>

    <div class="agent-trace-row__meta">
      <span v-if="node.length" class="agent-trace-row__meta-item">
        长度：{{ node.length }}
      </span>
      <span v-if="node.field_names?.length" class="agent-trace-row__meta-item">
        字段：{{ node.field_names.join(', ') }}
      </span>
    </div>

    <p v-if="node.error" class="agent-trace-row__error">
      错误：{{ node.error }}
    </p>
  </div>
</template>

<style scoped>
.agent-trace-row {
  background-color: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-sm);
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-xxs);
}

.agent-trace-row__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-sm);
}

.agent-trace-row__name {
  font-size: var(--font-body-size);
  font-weight: 500;
  color: var(--color-ink);
}

.agent-trace-row__badges {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.agent-trace-row__duration {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

.agent-trace-row__summary {
  margin: 0;
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-muted);
  line-height: var(--font-body-sm-line);
}

.agent-trace-row__meta {
  display: flex;
  gap: var(--space-md);
  flex-wrap: wrap;
}

.agent-trace-row__meta-item {
  font-size: var(--font-caption-size);
  color: var(--color-ink-subtle);
}

.agent-trace-row__error {
  margin: 0;
  font-size: var(--font-caption-size);
  color: var(--color-risk-high);
}
</style>
