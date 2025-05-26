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
/* 调整后的样式：上方10%高度有轻微模糊渐变，下方完全不透明 */
.custom-tabbar {
  height: 100px;
  background: linear-gradient(to top, 
    rgba(242, 238, 232, 0.3) 0%,     /* 顶部70%透明 */
    rgba(242, 238, 232, 0.6) 50%,    /* 中间40%透明 */
    rgba(242, 238, 232, 1) 100%
);
  border-top: 1px solid #f0f0f0;
  backdrop-filter: blur(6px);
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