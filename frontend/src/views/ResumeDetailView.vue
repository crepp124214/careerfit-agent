<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
const id = route.params.id
</script>

<template>
  <section class="view-placeholder" data-view="resume-detail">
    <h1>简历详情</h1>
    <p>简历 ID：{{ id }}</p>
    <p>占位 — T3 中接入简历编辑与版本对比入口</p>
  </section>
</template>
