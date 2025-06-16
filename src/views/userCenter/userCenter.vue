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
            <div class="nickname">{{ user.nickname }}</div>
            <div class="stats">
              <div class="stat-item">
                <div class="stat-number">{{ user.likesCount }}</div>
                <div class="stat-label">我喜欢的</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ user.likedByCount }}</div>
                <div class="stat-label">喜欢我的</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ user.recentVisitorsCount }}</div>
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
          <div 
            v-for="item in menuItems" 
            :key="item.id" 
            class="menu-item"
            @click="item.route ? router.push(item.route) : item.action && item.action()"
          >
            {{ item.label }}
          </div>
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
import { useRouter } from 'vue-router';

// 导入图标
import homeIcon from '@/assets/icons/home.svg';
import homeSelectedIcon from '@/assets/icons/home-selected.svg';
import compassIcon from '@/assets/icons/compass.svg';
import compassSelectedIcon from '@/assets/icons/compass-selected.svg';
import likeIcon from '@/assets/icons/like.svg';
import likeSelectedIcon from '@/assets/icons/like-selected.svg';
import smileIcon from '@/assets/icons/smile.svg';
import smileSelectedIcon from '@/assets/icons/smile-selected.svg';

// 定义 MenuItem 接口
interface MenuItem {
  id: string | number;
  label: string;
  action?: () => void; // 点击事件处理函数
  route?: string; // 路由路径
}

// 定义 User 接口
interface User {
  nickname: string; // 用户昵称
  avatarUrl?: string; // 可选的头像URL
  likesCount: number;
  likedByCount: number;
  recentVisitorsCount: number;
}

const activeTab = ref('profile');
const router = useRouter();

const user = ref<User>({
  nickname: '用户昵称',
  avatarUrl: '', // 初始为空或默认头像
  likesCount: 12,
  likedByCount: 5,
  recentVisitorsCount: 20,
});

const menuItems = ref<MenuItem[]>([
  { id: 'profile-maintenance', label: '资料维护', route: '/profile-setup' },
  { id: 'settings', label: '设置', action: () => console.log('Navigate to settings') }, // 示例action
  { id: 'logout', label: '退出登录', action: () => console.log('Logout') }, // 示例action
]);

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
  align-items: flex-start;
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
  margin-bottom: 16px;
  align-self: flex-start;
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
  cursor: pointer;
}

.menu-item:last-child {
  border-bottom: none;
}
</style>