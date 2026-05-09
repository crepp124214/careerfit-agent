<script setup lang="ts">
import { RouterLink } from 'vue-router'

interface BreadcrumbItem {
  label: string
  to?: string
}

defineProps<{
  items: BreadcrumbItem[]
}>()
</script>

<template>
  <nav class="breadcrumb" aria-label="面包屑导航">
    <ol class="breadcrumb__list">
      <li v-for="(item, i) in items" :key="i" class="breadcrumb__item">
        <span v-if="i > 0" class="breadcrumb__sep" aria-hidden="true">/</span>
        <RouterLink v-if="item.to" :to="item.to" class="breadcrumb__link">
          {{ item.label }}
        </RouterLink>
        <span v-else class="breadcrumb__current" aria-current="page">{{ item.label }}</span>
      </li>
    </ol>
  </nav>
</template>

<style scoped>
.breadcrumb__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-size: var(--font-body-sm-size);
}

.breadcrumb__item {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.breadcrumb__sep {
  color: var(--color-ink-tertiary);
}

.breadcrumb__link {
  color: var(--color-ink-subtle);
  text-decoration: none;
}

.breadcrumb__link:hover {
  color: var(--color-primary);
}

.breadcrumb__current {
  color: var(--color-ink);
  font-weight: 500;
}
</style>
