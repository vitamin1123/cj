<template>
  <div class="home-container">
    <!-- 骨架屏 -->
    <div v-if="isLoading" class="skeleton-container">
      <div class="skeleton-search"></div>
      <div class="skeleton-news"></div>
      <div class="skeleton-section">
        <div class="skeleton-title"></div>
        <div class="skeleton-cards">
          <div v-for="i in 3" :key="i" class="skeleton-card"></div>
        </div>
      </div>
      <div class="skeleton-section">
        <div class="skeleton-title"></div>
        <div class="skeleton-cards">
          <div v-for="i in 2" :key="i" class="skeleton-recommend-card"></div>
        </div>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-else-if="authError" class="error-container">
      <div class="error-icon">⚠️</div>
      <div class="error-title">认证失败</div>
      <div class="error-message">{{ authError }}</div>
      <button class="retry-button" @click="retryAuth">重试</button>
    </div>

    <!-- 页面内容 -->
    <div v-else class="page-content">
      <!-- 搜索框 -->
      <div class="search-container">
        <div class="search-card" :class="{ focused: isSearchFocused }">
          <div class="search-box">
            <t-icon name="search" class="search-icon" />
            <input 
              type="text" 
              placeholder="搜索" 
              class="search-input" 
              @focus="handleSearchFocus"
            />
          </div>
          
          <div class="search-options" v-if="isSearchFocused">
            <div class="search-option-item">
              <div class="option-label">身高</div>
              <div class="option-input">
                <input type="text" placeholder="请输入身高" />
                <van-icon name="clear" class="clear-icon" />
              </div>
            </div>
            <div class="search-option-item">
              <div class="option-label">区域</div>
              <div class="option-input">
                <input type="text" placeholder="请输入区域" />
                <van-icon name="clear" class="clear-icon" />
              </div>
            </div>
          </div>
        </div>
        <!-- 遮罩层 -->
        <div class="search-mask" v-if="isSearchFocused" @click="closeSearch"></div>
      </div>

      <!-- 其他原有内容保持不变 -->
      <div class="news-section">
        <div class="news-card">
          <div class="news-image"></div>
          <p class="news-title">新人新闻</p>
        </div>
      </div>

      <!-- 新人展示 -->
      <div class="newcomer-section">
        <h2 class="section-title">天顺新面孔</h2>
        <van-swipe class="newcomer-swipe" :loop="true" :width="180" :height="80" :autoplay="5000" indicator-color="transparent">
          <van-swipe-item v-for="i in 4" :key="i">
            <div class="newcomer-card">
              <div class="avatar"></div>
              <div class="info">
                <div class="title">标题</div>
                <div class="subtitle">副标题</div>
              </div>
            </div>
          </van-swipe-item>
        </van-swipe>
      </div>

      <!-- 推荐板块 -->
      <div class="recommend-section">
        <h2 class="section-title">可能感兴趣</h2>
        <van-swipe class="recommend-swipe" :loop="true" :width="240" :height="366" indicator-color="transparent">
          <van-swipe-item v-for="i in 4" :key="i">
            <!-- 在推荐卡片上添加点击事件 -->
            <div class="recommend-card" @click="goToDetail(i)">
              <div class="card-image"></div>
              <div class="card-content">
                <div class="name">姓名</div>
                <div class="height-container">
                  <div class="height">身高</div>
                  <div class="heart-icon">
                    <van-icon name="like" />
                  </div>
                </div>
                <div class="desc">简介</div>
              </div>
            </div>
          </van-swipe-item>
        </van-swipe>
      </div>
    </div>

    <!-- 底部TabBar -->
    <TabBar 
      :active-tab="activeTab" 
      @update:active-tab="activeTab = $event"
      :tabs="tabs"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import TabBar from '@/components/TabBar.vue';
import { useRouter } from 'vue-router'

// 导入图标
import homeIcon from '@/assets/icons/home.svg';
import homeSelectedIcon from '@/assets/icons/home-selected.svg';
import compassIcon from '@/assets/icons/compass.svg';
import compassSelectedIcon from '@/assets/icons/compass-selected.svg';
import likeIcon from '@/assets/icons/like.svg';
import likeSelectedIcon from '@/assets/icons/like-selected.svg';
import smileIcon from '@/assets/icons/smile.svg';
import smileSelectedIcon from '@/assets/icons/smile-selected.svg';

const activeTab = ref('home');
const router = useRouter()
const isSearchFocused = ref(false);

const handleSearchFocus = () => {
  isSearchFocused.value = true;
};

const closeSearch = () => {
  isSearchFocused.value = false;
};

const tabs = [
  { 
    id: 'home', 
    label: '首页', 
    icon: homeIcon,
    iconSelected: homeSelectedIcon,
    to: '/home'
  },
  { 
    id: 'explore', 
    label: '寻觅', 
    icon: compassIcon,
    iconSelected: compassSelectedIcon,
    to: '/explore'
  },
  { 
    id: 'likes', 
    label: '喜欢', 
    icon: likeIcon,
    iconSelected: likeSelectedIcon,
    to: '/likes'
  },
  { 
    id: 'profile', 
    label: '个人', 
    icon: smileIcon,
    iconSelected: smileSelectedIcon,
    to: '/userCenter'
  }
];

const handleTabClick = (tab: any) => {
  if (tab.to) {
    router.push(tab.to);
  }
};

const goToDetail = (id: number) => {
  router.push(`/detail/${id}`);
};
</script>

<style scoped>
.home-container {
  background-color: #F2EEE8;
  min-height: 100vh;
  padding: 16px;
  font-family: "Microsoft YaHei", sans-serif;
  display: flex;
  flex-direction: column;
  position: relative;
}

/* 骨架屏样式 */
.skeleton-container {
  flex: 1;
  margin-bottom: 60px;
}

.skeleton-search {
  height: 48px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 24px;
  margin-bottom: 16px;
}

.skeleton-news {
  height: 150px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 8px;
  margin-bottom: 24px;
}

.skeleton-section {
  margin-bottom: 24px;
}

.skeleton-title {
  height: 20px;
  width: 120px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 16px;
}

.skeleton-cards {
  display: flex;
  gap: 8px;
  overflow-x: hidden;
}

.skeleton-card {
  width: 172px;
  height: 80px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 8px;
  flex-shrink: 0;
}

.skeleton-recommend-card {
  width: 224px;
  height: 366px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 8px;
  flex-shrink: 0;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* 错误容器样式 */
.error-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px 20px;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.error-message {
  font-size: 14px;
  color: #666;
  margin-bottom: 24px;
  line-height: 1.5;
}

.retry-button {
  background-color: #007AFF;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.retry-button:hover {
  background-color: #0056CC;
}

.retry-button:active {
  background-color: #004499;
}

.page-content {
  flex: 1;
  margin-bottom: 60px;
  background-color: #F2EEE8;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  min-height: calc(100vh - 92px);
}

.search-container {
  margin-bottom: 16px;
  position: relative;
  z-index: 10;
  background-color: #F2EEE8;
}

.search-card {
  background-color: #EBE3D7;
  border-radius: 50px;
  padding: 12px 16px;
  transition: all 0.3s ease;
  position: relative;
  z-index: 10;
}

.search-card.focused {
  border-radius: 12px;
  padding-bottom: 16px;
  position: absolute;
  width: calc(100% - 32px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-input {
  border: none;
  background: transparent;
  outline: none;
  width: 100%;
  font-family: "Microsoft YaHei", sans-serif;
  font-size: 14px;
}

.search-options {
  margin-top: 12px;
  animation: fadeIn 0.3s ease;
}

.search-option-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.option-label {
  width: 60px;
  font-size: 14px;
  color: #6A6A6A;
}

.option-input {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.option-input input {
  width: 100%;
  background: #fff;
  border: none;
  border-radius: 16px;
  padding: 8px 32px 8px 12px;
  font-size: 14px;
  outline: none;
}

.clear-icon {
  position: absolute;
  right: 8px;
  color: #ccc;
  font-size: 16px;
}

.search-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 5;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.news-section {
  margin-bottom: 24px;
}

.news-card {
  background-color: #D9D9D9;
  border-radius: 8px;
  padding: 16px;
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #D9D9D9;
  width: 100%;
  box-sizing: border-box;
}

.news-title {
  color: #6A6A6A;
  font-size: 16px;
}

.section-title {
  color: #6A6A6A;
  font-size: 16px;
  margin-bottom: 16px;
  font-weight: normal;
}

.newcomer-section {
  margin-bottom: 24px;
}

.newcomer-swipe {
  padding-left: 0;
}

.newcomer-card {
  background-color: #FFFFFF;
  border-radius: 8px;
  width: 172px;
  height: 80px;
  display: flex;
  padding: 8px;
  box-sizing: border-box;
  border: 1px solid #D9D9D9;
  margin-right: 8px;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #D9D9D9;
  margin-right: 12px;
  align-self: center;
}

.info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.title {
  font-size: 14px;
  color: #333;
  margin-bottom: 4px;
}

.subtitle {
  font-size: 12px;
  color: #6A6A6A;
}

.recommend-section {
  margin-bottom: 24px;
}

.recommend-swipe {
  padding-left: 0;
}

.recommend-card {
  background-color: #FFFFFF;
  border-radius: 8px;
  width: 224px;
  height: 366px;
  margin-right: 8px;
  position: relative;
  overflow: hidden;
  border: 1px solid #D9D9D9;
}

.card-image {
  width: calc(100% - 16px);
  height: 260px;
  background-color: #D9D9D9;
  margin: 8px;
  border-radius: 4px;
}

.card-content {
  padding: 0 16px 16px;
}

.name {
  font-size: 14px;
  color: #333;
  margin-bottom: 8px;
}

.height-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-bottom: 8px;
}

.height {
  font-size: 12px;
  color: #6A6A6A;
}

.desc {
  font-size: 12px;
  color: #6A6A6A;
  line-height: 1.4;
}

.heart-icon {
  font-size: 20px;
  display: flex;
  align-items: center;
  color: #ff4757;
}
</style>