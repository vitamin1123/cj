<template>
    <div class="user-center-container">
      <!-- 页面内容 -->
      <div class="page-content">
        <!-- 顶部卡片 -->
        <div class="profile-card">
          <div class="profile-content">
            <div class="avatar-wrapper">
              <div class="avatar"></div>
            </div>
            <div class="profile-info">
              <div class="nickname">昵称</div>
              <div class="stats">
                <div class="stat-item">
                  <div class="stat-number">0</div>
                  <div class="stat-label">我喜欢的</div>
                </div>
                <div class="stat-item">
                  <div class="stat-number">0</div>
                  <div class="stat-label">喜欢我的</div>
                </div>
                <div class="stat-item">
                  <div class="stat-number">0</div>
                  <div class="stat-label">最近来访</div>
                </div>
              </div>
            </div>
          </div>
        </div>
  
        <!-- 管理菜单卡片 -->
        <div class="menu-card">
          <h2 class="section-title">管理</h2>
          <div class="menu-items">
            <div class="menu-item" @click="router.push('/profile-setup')">资料维护</div>
            <div class="menu-item">菜单项2</div>
            <div class="menu-item">菜单项3</div>
          </div>
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
  
  // 导入图标
  import homeIcon from '@/assets/icons/home.svg';
  import homeSelectedIcon from '@/assets/icons/home-selected.svg';
  import compassIcon from '@/assets/icons/compass.svg';
  import compassSelectedIcon from '@/assets/icons/compass-selected.svg';
  import likeIcon from '@/assets/icons/like.svg';
  import likeSelectedIcon from '@/assets/icons/like-selected.svg';
  import smileIcon from '@/assets/icons/smile.svg';
  import smileSelectedIcon from '@/assets/icons/smile-selected.svg';
  import { useRouter } from 'vue-router';
  
  const activeTab = ref('profile');
  const router = useRouter();
  
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
  </script>
  
  <style scoped>
 .user-center-container {
  background-color: #F2EEE8;
  min-height: 100vh;
  padding: 16px;
  font-family: "Microsoft YaHei", sans-serif;
  display: flex;
  flex-direction: column;
}

.page-content {
  flex: 1;
  margin-bottom: 60px;
}

.profile-card {
  background-color: #FFFFFF;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
  border: 1px solid #D9D9D9;
}

.profile-content {
  display: flex;
  align-items: flex-start; /* 改为flex-start让内容顶部对齐 */
}

.avatar-wrapper {
  margin-right: 16px;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: #D9D9D9;
}

.profile-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.nickname {
  font-size: 20px;
  color: #333;
  font-weight: 500;
  margin-bottom: 16px; /* 增加与下方统计数据的间距 */
  align-self: flex-start; /* 昵称左对齐 */
}

.stats {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 60px;
}

.stat-number {
  font-size: 20px;
  color: #333;
  margin-bottom: 8px;
  font-weight: 700;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
}

.stat-label {
  font-size: 12px;
  color: #6A6A6A;
}
  
  .nickname {
    font-size: 20px; /* 加大字号与数字统一 */
    color: #333;
    font-weight: 500;
    align-self: center; /* 确保与头像水平对齐 */
    margin-left: auto; /* 向右靠齐 */
    padding-right: 16px; /* 增加右边距 */
  }
  
  .section-title {
    color: #6A6A6A;
    font-size: 16px;
    margin-bottom: 16px;
    font-weight: normal;
  }
  
  .menu-card {
    background-color: #FFFFFF;
    border-radius: 8px;
    padding: 16px;
    border: 1px solid #D9D9D9;
  }
  
  .menu-items {
    display: flex;
    flex-direction: column;
  }
  
  .menu-item {
    padding: 12px 0;
    font-size: 14px;
    color: #333;
    border-bottom: 1px solid #F0F0F0;
  }
  
  .menu-item:last-child {
    border-bottom: none;
  }
  </style>