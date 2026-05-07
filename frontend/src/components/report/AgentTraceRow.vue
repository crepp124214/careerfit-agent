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

function executionModeLabel(mode?: string) {
  switch (mode) {
    case 'llm':
      return 'LLM'
    case 'rule':
      return '规则'
    case 'rag':
      return 'RAG'
    case 'deterministic':
      return '确定性'
    default:
      return mode || '未知'
  }
}
</script>

<template>
  <div class="agent-trace-row">
    <div class="agent-trace-row__header">
      <div class="agent-trace-row__title">
        <span class="agent-trace-row__name">{{ node.name }}</span>
        <span
          v-if="node.execution_meta?.execution_mode"
          class="agent-trace-row__mode-badge"
          :class="`agent-trace-row__mode-badge--${node.execution_meta.execution_mode}`"
        >
          {{ executionModeLabel(node.execution_meta.execution_mode) }}
        </span>
      </div>
      <div class="agent-trace-row__badges">
        <StatusBadge :tone="statusTone(node.status)">
          {{ statusLabel(node.status) }}
        </StatusBadge>
        <span class="agent-trace-row__duration">{{ formatDuration(node.duration) }}</span>
      </div>
    </div>

    <p class="agent-trace-row__summary">{{ node.summary }}</p>

    <div class="agent-trace-row__meta">
      <span v-if="node.execution_meta" class="agent-trace-row__meta-item">
        schema 校验：{{ node.execution_meta.schema_valid ? '通过' : '失败' }}
      </span>
      <span v-if="node.execution_meta?.retry_count !== undefined && node.execution_meta.retry_count > 0" class="agent-trace-row__meta-item">
        重试：{{ node.execution_meta.retry_count }} 次
      </span>
      <span v-if="node.execution_meta?.fallback_used" class="agent-trace-row__meta-item agent-trace-row__meta-item--warn">
        回退到规则引擎
      </span>
      <span v-if="node.execution_meta?.model_name" class="agent-trace-row__meta-item">
        {{ node.execution_meta.model_name }}
      </span>
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

.agent-trace-row__title {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.agent-trace-row__name {
  font-size: var(--font-body-size);
  font-weight: 500;
  color: var(--color-ink);
}

.agent-trace-row__mode-badge {
  font-size: var(--font-caption-size);
  padding: 1px 6px;
  border-radius: var(--rounded-sm);
  font-weight: 500;
}

.agent-trace-row__mode-badge--llm {
  background: #dbeafe;
  color: #1e40af;
}

.agent-trace-row__mode-badge--rule {
  background: #f3f4f6;
  color: #374151;
}

.agent-trace-row__mode-badge--rag {
  background: #d1fae5;
  color: #065f46;
}

.agent-trace-row__mode-badge--deterministic {
  background: #fef3c7;
  color: #92400e;
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

.agent-trace-row__meta-item--warn {
  color: var(--color-risk-medium, #b45309);
  font-weight: 500;
}

.agent-trace-row__error {
  margin: 0;
  font-size: var(--font-caption-size);
  color: var(--color-risk-high);
}

@media (prefers-color-scheme: dark) {
  .agent-trace-row__mode-badge--llm {
    background: #1e3a5f;
    color: #93c5fd;
  }

  .agent-trace-row__mode-badge--rule {
    background: #374151;
    color: #d1d5db;
  }

  .agent-trace-row__mode-badge--rag {
    background: #064e3b;
    color: #6ee7b7;
  }

  .agent-trace-row__mode-badge--deterministic {
    background: #78350f;
    color: #fcd34d;
  }
}
</style>
