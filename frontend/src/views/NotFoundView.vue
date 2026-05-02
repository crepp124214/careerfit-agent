<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <section class="view-placeholder" data-view="not-found">
    <h1>页面不存在</h1>
    <p>请求的路径未匹配任何路由。</p>
    <p>
      <RouterLink to="/">返回工作台</RouterLink>
    </p>
  </section>
</template>
