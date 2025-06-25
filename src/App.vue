<template>
  <router-view v-slot="{ Component, route }">
    <keep-alive v-if="route.meta.keepAlive">
      <component :is="Component" :key="route.fullPath" />
    </keep-alive>
    <component :is="Component" v-else :key="route.fullPath" />
  </router-view>
</template>

<script setup lang="ts">

</script>

<style>

</style>
