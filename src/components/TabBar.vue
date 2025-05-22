<!-- components/TabBar.vue -->
<template>
    <van-tabbar :model-value="activeTab" class="custom-tabbar" :border="false">
      <van-tabbar-item 
        v-for="tab in tabs" 
        :key="tab.id" 
        :name="tab.id"
        :icon="activeTab === tab.id ? tab.iconSelected : tab.icon"
        @click="handleTabClick(tab)"
      >
        {{ tab.label }}
      </van-tabbar-item>
    </van-tabbar>
  </template>
  
  <script setup lang="ts">
  import { useRouter } from 'vue-router';
  import { Tabbar, TabbarItem } from 'vant';
  
  interface TabItem {
    id: string;
    label: string;
    icon: string;
    iconSelected: string;
    to?: string;
  }
  
  const props = defineProps<{
    activeTab: string;
    tabs: TabItem[];
  }>();
  
  const emit = defineEmits(['update:activeTab']);
  const router = useRouter();
  
  const handleTabClick = (tab: TabItem) => {
    emit('update:activeTab', tab.id);
    if (tab.to) {
      router.push(tab.to);
    }
  };
  </script>
  
  <style scoped>
  /* 保持原有样式不变 */
  .custom-tabbar {
    height: 100px;
    background-color: transparent;
    border-top: 1px solid #f0f0f0;
  }
  
  .custom-tabbar :deep(.van-tabbar-item) {
    color: #1e1e1e;
    font-family: "Microsoft YaHei", sans-serif;
    flex-direction: column;
    justify-content: center;
    padding: 0;
    background-color: transparent !important;
  }
  
  .custom-tabbar :deep(.van-tabbar-item__icon) {
    margin-bottom: 4px;
    font-size: 0;
  }
  
  .custom-tabbar :deep(.van-tabbar-item__icon img) {
    width: 24px;
    height: 24px;
    object-fit: contain;
  }
  
  .custom-tabbar :deep(.van-tabbar-item--active) {
    color: #D75670;
    font-weight: 500;
    background-color: transparent !important;
  }
  
  .custom-tabbar :deep(.van-tabbar-item__text) {
    font-size: 12px;
  }
  
  .custom-tabbar :deep(.van-tabbar-item:active),
  .custom-tabbar :deep(.van-tabbar-item--active:active) {
    background-color: transparent !important;
  }
  </style>