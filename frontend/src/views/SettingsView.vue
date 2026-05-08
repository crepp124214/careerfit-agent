<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { usePreferencesStore, type Theme, type Density } from '@/stores/preferences'
import { fetchLLMStatus, type LLMStatus } from '@/api/llm'
import { requestJson } from '@/api/client'

const prefs = usePreferencesStore()

const themeOptions: { value: Theme; label: string; disabled?: boolean }[] = [
  { value: 'system', label: '跟随系统' },
  { value: 'dark', label: '暗色' },
  { value: 'light', label: '亮色' },
]

const densityOptions: { value: Density; label: string }[] = [
  { value: 'compact', label: '紧凑' },
  { value: 'relaxed', label: '宽松' },
]

const llmStatus = ref<LLMStatus | null>(null)
const llmLoading = ref(false)
const llmError = ref<string | null>(null)

async function quickCheckLLM() {
  llmLoading.value = true
  llmError.value = null
  const res = await fetchLLMStatus()
  if (res.ok) {
    llmStatus.value = res.status
  } else {
    llmError.value = res.error
  }
  llmLoading.value = false
}

async function testLLMConnection() {
  llmLoading.value = true
  llmError.value = null
  const res = await requestJson<LLMStatus>('/llm/status')
  if (res.ok) {
    llmStatus.value = res.data
  } else {
    llmError.value = res.message
  }
  llmLoading.value = false
}

onMounted(() => {
  quickCheckLLM()
})
</script>

<template>
  <section class="settings-view" role="main" aria-label="设置">
    <h1 class="settings-view__title animate-in">设置</h1>

    <p class="settings-view__notice animate-in animate-in-stagger-1">
      本设置仅保存在你的浏览器，未来如果清空浏览器数据将恢复默认。
    </p>

    <div class="settings-view__section animate-in animate-in-stagger-2">
      <h2 class="settings-view__section-title">主题</h2>
      <div class="settings-view__options">
        <label
          v-for="opt in themeOptions"
          :key="opt.value"
          class="settings-view__option"
          :class="{ 'settings-view__option--disabled': opt.disabled }"
        >
          <input
            type="radio"
            name="theme"
            :value="opt.value"
            :disabled="opt.disabled"
            :checked="prefs.theme === opt.value"
            :data-testid="`theme-${opt.value}`"
            @change="prefs.theme = opt.value"
          />
          <span class="settings-view__option-label">{{ opt.label }}</span>
          <span v-if="opt.disabled" class="settings-view__phase-tag">Phase 2 启用</span>
        </label>
      </div>
    </div>

    <div class="settings-view__section animate-in animate-in-stagger-3">
      <h2 class="settings-view__section-title">布局密度</h2>
      <div class="settings-view__options">
        <label
          v-for="opt in densityOptions"
          :key="opt.value"
          class="settings-view__option"
        >
          <input
            type="radio"
            name="density"
            :value="opt.value"
            :checked="prefs.density === opt.value"
            @change="prefs.density = opt.value"
          />
          <span class="settings-view__option-label">{{ opt.label }}</span>
        </label>
      </div>
    </div>

    <div class="settings-view__section animate-in animate-in-stagger-4">
      <h2 class="settings-view__section-title">最近打开历史长度</h2>
      <label class="settings-view__field">
        <span class="settings-view__field-label">保留条数</span>
        <input
          type="number"
          class="settings-view__number-input"
          :value="prefs.recentLimit"
          min="1"
          max="50"
          @input="prefs.recentLimit = Math.max(1, Math.min(50, Number(($event.target as HTMLInputElement).value)))"
        />
      </label>
    </div>

    <div class="settings-view__section animate-in animate-in-stagger-5">
      <h2 class="settings-view__section-title">大模型配置</h2>
      <p class="settings-view__section-desc">
        大模型用于生成简历优化建议、面试题和学习计划。配置信息由后端管理，此处仅显示连接状态。
      </p>

      <div v-if="llmLoading" class="settings-view__llm-loading">
        <span class="settings-view__spinner" aria-hidden="true" />
        <span>检查连接状态...</span>
      </div>

      <div v-else-if="llmError" class="settings-view__llm-error">
        <span class="settings-view__status-icon settings-view__status-icon--error" aria-hidden="true">✕</span>
        <span>无法检查大模型状态: {{ llmError }}</span>
      </div>

      <div v-else-if="llmStatus" class="settings-view__llm-status">
        <div class="settings-view__llm-item">
          <span class="settings-view__llm-label">状态</span>
          <span class="settings-view__llm-value">
            <span
              class="settings-view__status-dot"
              :class="{
                'settings-view__status-dot--disabled': !llmStatus.enabled,
                'settings-view__status-dot--unconfigured': llmStatus.enabled && !llmStatus.configured,
                'settings-view__status-dot--connected': llmStatus.connected,
                'settings-view__status-dot--failed': llmStatus.configured && !llmStatus.connected,
              }"
              aria-hidden="true"
            />
            <span v-if="!llmStatus.enabled">未启用</span>
            <span v-else-if="!llmStatus.configured">未配置</span>
            <span v-else-if="llmStatus.connected">已连接</span>
            <span v-else>连接失败</span>
          </span>
        </div>

        <div v-if="llmStatus.model_name" class="settings-view__llm-item">
          <span class="settings-view__llm-label">模型</span>
          <span class="settings-view__llm-value settings-view__llm-value--mono">{{ llmStatus.model_name }}</span>
        </div>

        <div v-if="llmStatus.response_time_ms !== null" class="settings-view__llm-item">
          <span class="settings-view__llm-label">响应时间</span>
          <span class="settings-view__llm-value">{{ llmStatus.response_time_ms }}ms</span>
        </div>

        <div v-if="llmStatus.error" class="settings-view__llm-item">
          <span class="settings-view__llm-label">错误</span>
          <span class="settings-view__llm-value settings-view__llm-value--error">{{ llmStatus.error }}</span>
        </div>

        <button
          class="settings-view__test-btn"
          type="button"
          :disabled="llmLoading"
          @click="testLLMConnection"
        >
          {{ llmLoading ? '测试中...' : '测试连接' }}
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.settings-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  max-width: 640px;
}

.settings-view__title {
  margin: 0;
  font-size: var(--font-headline-size);
  font-weight: var(--font-headline-weight);
  line-height: var(--font-headline-line);
}

.settings-view__notice {
  margin: 0;
  padding: var(--space-md);
  background-color: var(--color-surface-2);
  border-radius: var(--rounded-md);
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-subtle);
  line-height: var(--font-body-sm-line);
}

.settings-view__section {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  padding: var(--space-lg);
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-lg);
  box-shadow: var(--shadow-sm);
}

.settings-view__section-title {
  margin: 0;
  font-size: var(--font-card-title-size);
  font-weight: var(--font-card-title-weight);
  line-height: var(--font-card-title-line);
}

.settings-view__options {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.settings-view__option {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  cursor: pointer;
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--rounded-md);
  transition: background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.settings-view__option:hover {
  background-color: var(--color-surface-2);
}

.settings-view__option--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.settings-view__option--disabled:hover {
  background-color: transparent;
}

/* 视觉隐藏原生 radio，保留 data-testid 供测试 */
.settings-view__option input[type="radio"] {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* 自定义 radio 指示器 */
.settings-view__option-label {
  font-size: var(--font-body-size);
  color: var(--color-ink);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.settings-view__option-label::before {
  content: '';
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: var(--rounded-full);
  border: 2px solid var(--color-hairline-tertiary);
  flex-shrink: 0;
  transition:
    border-color var(--motion-duration-fast) var(--motion-easing-standard),
    background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.settings-view__option input[type="radio"]:checked + .settings-view__option-label::before {
  border-color: var(--color-primary);
  background-color: var(--color-primary);
  box-shadow: inset 0 0 0 3px var(--color-surface-1);
}

.settings-view__option input[type="radio"]:focus-visible + .settings-view__option-label::before {
  outline: var(--focus-ring-width) solid var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
}

.settings-view__phase-tag {
  font-size: var(--font-caption-size);
  color: var(--color-ink-muted);
  background-color: var(--color-surface-2);
  padding: 2px 6px;
  border-radius: var(--rounded-xs);
}

.settings-view__field {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.settings-view__field-label {
  font-size: var(--font-body-size);
  color: var(--color-ink-subtle);
}

.settings-view__number-input {
  font-family: var(--font-family-sans);
  font-size: var(--font-body-size);
  padding: var(--space-xs) var(--space-sm);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-md);
  background-color: var(--color-surface-2);
  color: var(--color-ink);
  width: 80px;
  transition:
    border-color var(--motion-duration-fast) var(--motion-easing-standard),
    background-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.settings-view__number-input:focus {
  outline: none;
  border-color: var(--color-primary);
  background-color: var(--color-surface-2);
}

.settings-view__section-desc {
  margin: 0 0 var(--space-md);
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-subtle);
  line-height: var(--font-body-sm-line);
}

.settings-view__llm-loading,
.settings-view__llm-error {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md);
  background-color: var(--color-surface-2);
  border-radius: var(--rounded-md);
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-subtle);
}

.settings-view__spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-ink-tertiary);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.settings-view__status-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  font-size: 10px;
  font-weight: bold;
}

.settings-view__status-icon--error {
  background-color: var(--color-risk-high);
  color: var(--color-surface-0);
}

.settings-view__llm-status {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.settings-view__llm-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-sm) 0;
  border-bottom: 1px solid var(--color-hairline);
}

.settings-view__llm-item:last-of-type {
  border-bottom: none;
}

.settings-view__llm-label {
  font-size: var(--font-body-sm-size);
  color: var(--color-ink-muted);
  min-width: 60px;
}

.settings-view__llm-value {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-size: var(--font-body-size);
  color: var(--color-ink);
}

.settings-view__llm-value--mono {
  font-family: var(--font-mono);
  font-size: var(--font-body-sm-size);
  padding: 2px 6px;
  background-color: var(--color-surface-2);
  border-radius: var(--rounded-xs);
}

.settings-view__llm-value--error {
  color: var(--color-risk-high);
  font-size: var(--font-body-sm-size);
}

.settings-view__status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-ink-tertiary);
}

.settings-view__status-dot--disabled {
  background-color: var(--color-ink-tertiary);
}

.settings-view__status-dot--unconfigured {
  background-color: var(--color-risk-medium);
}

.settings-view__status-dot--connected {
  background-color: var(--color-risk-low);
}

.settings-view__status-dot--failed {
  background-color: var(--color-risk-high);
}

.settings-view__test-btn {
  align-self: flex-start;
  padding: var(--space-sm) var(--space-lg);
  border: 1px solid var(--color-primary);
  border-radius: var(--rounded-md);
  background-color: var(--color-surface-1);
  color: var(--color-primary);
  font-size: var(--font-body-sm-size);
  font-weight: var(--font-body-weight);
  cursor: pointer;
  transition:
    background-color var(--motion-duration-fast) var(--motion-easing-standard),
    border-color var(--motion-duration-fast) var(--motion-easing-standard);
}

.settings-view__test-btn:hover:not(:disabled) {
  background-color: var(--color-primary);
  color: var(--color-surface-0);
}

.settings-view__test-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
