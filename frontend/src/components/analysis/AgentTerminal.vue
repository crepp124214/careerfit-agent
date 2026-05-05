<script setup lang="ts">
import { ref, nextTick, watch, onMounted, computed } from 'vue'

export interface TerminalLine {
  id: number
  text: string
  type: 'info' | 'start' | 'success' | 'error' | 'summary' | 'blank' | 'connecting' | 'connected' | 'failed'
}

const props = defineProps<{
  lines: TerminalLine[]
  completed: boolean
}>()

const containerRef = ref<HTMLDivElement | null>(null)
const autoScroll = ref(true)

const displayLines = computed(() => props.lines)

function scrollToBottom() {
  nextTick(() => {
    if (containerRef.value) {
      containerRef.value.scrollTop = containerRef.value.scrollHeight
    }
  })
}

function onScroll() {
  if (!containerRef.value) return
  const { scrollTop, scrollHeight, clientHeight } = containerRef.value
  autoScroll.value = scrollHeight - scrollTop - clientHeight < 40
}

watch(
  () => props.lines.length,
  () => {
    if (autoScroll.value) {
      scrollToBottom()
    }
  },
)

onMounted(() => {
  scrollToBottom()
})
</script>

<template>
  <section class="agent-terminal" role="log" aria-label="Agent 运行终端" aria-live="polite">
    <header class="agent-terminal__header">
      <div class="agent-terminal__title-bar">
        <span class="agent-terminal__dot agent-terminal__dot--red" aria-hidden="true" />
        <span class="agent-terminal__dot agent-terminal__dot--yellow" aria-hidden="true" />
        <span class="agent-terminal__dot agent-terminal__dot--green" aria-hidden="true" />
        <span class="agent-terminal__title">Agent 运行终端</span>
      </div>
      <button
        v-if="!autoScroll"
        class="agent-terminal__scroll-btn"
        type="button"
        aria-label="滚动到底部"
        @click="scrollToBottom(); autoScroll = true"
      >
        ↓ 底部
      </button>
    </header>
    <div
      ref="containerRef"
      class="agent-terminal__body"
      @scroll="onScroll"
    >
      <div
        v-for="line in displayLines"
        :key="line.id"
        class="agent-terminal__line"
        :class="`agent-terminal__line--${line.type}`"
      >
        <span class="agent-terminal__text">{{ line.text }}</span>
      </div>
      <div v-if="!completed" class="agent-terminal__cursor" aria-hidden="true">
        <span class="agent-terminal__cursor-block" />
      </div>
    </div>
  </section>
</template>

<style scoped>
.agent-terminal {
  --term-bg: #0d1117;
  --term-fg: #c9d1d9;
  --term-green: #3fb950;
  --term-yellow: #d29922;
  --term-red: #f85149;
  --term-blue: #58a6ff;
  --term-cyan: #39d353;
  --term-purple: #bc8cff;
  --term-gray: #484f58;
  --term-dim: #6e7681;

  border-radius: 8px;
  overflow: hidden;
  background: var(--term-bg);
  border: 1px solid var(--term-gray);
  font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.agent-terminal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: #161b22;
  border-bottom: 1px solid var(--term-gray);
}

.agent-terminal__title-bar {
  display: flex;
  align-items: center;
  gap: 6px;
}

.agent-terminal__dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.agent-terminal__dot--red { background: #ff5f57; }
.agent-terminal__dot--yellow { background: #febc2e; }
.agent-terminal__dot--green { background: #28c840; }

.agent-terminal__title {
  margin-left: 8px;
  color: var(--term-dim);
  font-size: 12px;
  font-weight: 500;
}

.agent-terminal__scroll-btn {
  padding: 2px 8px;
  border: 1px solid var(--term-gray);
  border-radius: 4px;
  background: transparent;
  color: var(--term-dim);
  font-family: inherit;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.15s;
}

.agent-terminal__scroll-btn:hover {
  color: var(--term-fg);
  border-color: var(--term-dim);
}

.agent-terminal__body {
  padding: 12px 16px;
  max-height: 480px;
  overflow-y: auto;
  scroll-behavior: smooth;
}

.agent-terminal__body::-webkit-scrollbar {
  width: 6px;
}

.agent-terminal__body::-webkit-scrollbar-track {
  background: transparent;
}

.agent-terminal__body::-webkit-scrollbar-thumb {
  background: var(--term-gray);
  border-radius: 3px;
}

.agent-terminal__line {
  white-space: pre-wrap;
  word-break: break-all;
  min-height: 1.6em;
}

.agent-terminal__line--info .agent-terminal__text {
  color: var(--term-dim);
}

.agent-terminal__line--start .agent-terminal__text {
  color: var(--term-yellow);
}

.agent-terminal__line--success .agent-terminal__text {
  color: var(--term-green);
}

.agent-terminal__line--error .agent-terminal__text {
  color: var(--term-red);
}

.agent-terminal__line--summary .agent-terminal__text {
  color: var(--term-dim);
  padding-left: 1em;
}

.agent-terminal__line--blank {
  min-height: 0.6em;
}

.agent-terminal__line--connecting .agent-terminal__text {
  color: var(--term-yellow);
}

.agent-terminal__line--connected .agent-terminal__text {
  color: var(--term-cyan);
}

.agent-terminal__line--failed .agent-terminal__text {
  color: var(--term-red);
}

.agent-terminal__cursor {
  display: flex;
  align-items: center;
  height: 1.6em;
  margin-top: 2px;
}

.agent-terminal__cursor-block {
  display: inline-block;
  width: 8px;
  height: 16px;
  background: var(--term-green);
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

@media (max-width: 768px) {
  .agent-terminal {
    font-size: 11px;
  }

  .agent-terminal__body {
    max-height: 360px;
    padding: 8px 10px;
  }
}
</style>
