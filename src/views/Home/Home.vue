<template>
  <div class="home-container">
    <!-- 页面内容 -->
    <div class="page-content">
      <!-- 搜索框 -->
      <div class="search-container">
        <div class="search-box">
          <t-icon name="search" class="search-icon" />
          <input type="text" placeholder="搜索" class="search-input" />
        </div>
      </div>

      <!-- 新闻板块 -->
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
            <div class="recommend-card">
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
    <div class="tab-bar">
      <div 
        v-for="tab in tabs" 
        :key="tab.id" 
        class="tab-item"
        :class="{ 'active': activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        <img 
          :src="activeTab === tab.id ? tab.iconSelected : tab.icon" 
          class="tab-icon" 
          :alt="tab.label"
        />
        <span class="tab-label">{{ tab.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

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

const tabs = [
  { 
    id: 'home', 
    label: '首页', 
    icon: homeIcon,
    iconSelected: homeSelectedIcon
  },
  { 
    id: 'explore', 
    label: '寻觅', 
    icon: compassIcon,
    iconSelected: compassSelectedIcon
  },
  { 
    id: 'likes', 
    label: '喜欢', 
    icon: likeIcon,
    iconSelected: likeSelectedIcon
  },
  { 
    id: 'profile', 
    label: '个人', 
    icon: smileIcon,
    iconSelected: smileSelectedIcon
  }
];
</script>

<style scoped>
.home-container {
  background-color: #F2EEE8;
  min-height: 100vh;
  padding: 16px;
  font-family: "Microsoft YaHei", sans-serif;
  display: flex;
  flex-direction: column;
}

.page-content {
  flex: 1;
  margin-bottom: 60px; /* 为底部TabBar留出空间 */
}

.search-container {
  margin-bottom: 16px;
}

.search-box {
  background-color: #EBE3D7;
  border-radius: 50px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  box-sizing: border-box;
}

.search-input {
  border: none;
  background: transparent;
  outline: none;
  width: 100%;
  font-family: "Microsoft YaHei", sans-serif;
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
  height: calc(224px - 16px);
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

/* 底部TabBar样式 */
.tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100px;
  background-color: transparent;
  display: flex;
  justify-content: space-around;
  align-items: center;
  border-top: 1px solid #f0f0f0;
  padding: 0 16px;
  box-sizing: border-box;
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  height: 100%;
  color: #1e1e1e;
  font-family: "Microsoft YaHei", sans-serif;
  cursor: pointer;
}

.tab-icon {
  width: 24px;
  height: 24px;
  margin-bottom: 4px;
  object-fit: contain;
}

.tab-label {
  font-size: 12px;
}

.tab-item.active {
  color: #D75670;
  font-weight: 500;
}
</style>