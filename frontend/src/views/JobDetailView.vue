<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
const id = route.params.id
</script>

<template>
  <section class="view-placeholder" data-view="job-detail">
    <h1>岗位详情</h1>
    <p>岗位 ID：{{ id }}</p>
    <p>占位 — T3 中接入岗位编辑与匹配触发</p>
  </section>
</template>
