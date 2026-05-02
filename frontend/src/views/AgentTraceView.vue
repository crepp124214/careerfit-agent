<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
const taskId = route.params.taskId
</script>

<template>
  <section class="view-placeholder" data-view="agent-trace">
    <h1>Agent 运行轨迹</h1>
    <p>任务 ID：{{ taskId }}</p>
    <p>占位 — T5 中接入折叠摘要 + 节点展开（脱敏）</p>
  </section>
</template>
