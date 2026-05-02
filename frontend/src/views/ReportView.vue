<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
const taskId = route.params.taskId
</script>

<template>
  <section class="view-placeholder" data-view="report">
    <h1>分析报告</h1>
    <p>任务 ID：{{ taskId }}</p>
    <p>占位 — T4 中接入证据链评分卡 + Next Best Action 头部</p>
  </section>
</template>
