<script setup lang="ts">
import { usePreferencesStore, type Theme, type Density } from '@/stores/preferences'

const prefs = usePreferencesStore()

const themeOptions: { value: Theme; label: string; disabled?: boolean }[] = [
  { value: 'system', label: '跟随系统' },
  { value: 'dark', label: '暗色' },
  { value: 'light', label: '亮色', disabled: true },
]

const densityOptions: { value: Density; label: string }[] = [
  { value: 'compact', label: '紧凑' },
  { value: 'relaxed', label: '宽松' },
]
</script>

<template>
  <section class="settings-view" role="main" aria-label="设置">
    <h1 class="settings-view__title">设置</h1>

    <p class="settings-view__notice">
      本设置仅保存在你的浏览器，未来如果清空浏览器数据将恢复默认。
    </p>

    <div class="settings-view__section">
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

    <div class="settings-view__section">
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

    <div class="settings-view__section">
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
}

.settings-view__option--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.settings-view__option-label {
  font-size: var(--font-body-size);
  color: var(--color-ink);
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
  background-color: var(--color-surface-1);
  color: var(--color-ink);
  width: 80px;
}
</style>
