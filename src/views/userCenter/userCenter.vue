<template>
  <div class="user-center-container">
    <!-- 页面内容 -->
    <div class="page-content">
      <!-- 顶部卡片 -->
      <div class="profile-card">
        <div class="profile-content">
          <div class="avatar-wrapper" @click="editAvatar">
            <div class="avatar" :style="{ backgroundImage: user.avatarUrl ? `url(${user.avatarUrl})` : 'none' }">
              <div v-if="!user.avatarUrl" class="avatar-placeholder">+</div>
            </div>
            <!-- <div class="edit-hint">点击编辑</div> -->
          </div>
          <div class="profile-info">
            <div class="nickname-container">
              <div v-if="!isEditingNickname" class="nickname" @click="editNickname">{{ user.nickname }}</div>
              <div v-else class="nickname-edit">
                <input 
                  v-model="tempNickname" 
                  @blur="saveNickname" 
                  @keyup.esc="cancelEdit"
                  maxlength="10"
                  class="nickname-input"
                  ref="nicknameInput"
                />
                <div class="char-count">{{ tempNickname.length }}/10</div>
              </div>
            </div>
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
            @click="item.route ? router.replace(item.route) : item.action && item.action()"
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
    
    <!-- 头像选择器 -->
    <input 
      ref="avatarInput" 
      type="file" 
      accept="image/*" 
      @change="handleAvatarChange" 
      style="display: none;"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted  } from 'vue';
import TabBar from '@/components/TabBar.vue';
import { useRouter } from 'vue-router';
import { Toast, showToast  } from 'vant';
import apiClient from '@/plugins/axios';
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
const avatarInput = ref<HTMLInputElement>();
const nicknameInput = ref<HTMLInputElement>();
const isEditingNickname = ref(false);
const tempNickname = ref('');

const user = ref<User>({
  nickname: '用户昵称',
  avatarUrl: '', // 初始为空或默认头像
  likesCount: 12,
  likedByCount: 5,
  recentVisitorsCount: 20,
});

onMounted(() => {
  fetchUserProfile();
});

// 编辑头像
const editAvatar = () => {
  avatarInput.value?.click();
};
// 请求示例 
// const response = await apiClient.post('/api/profile', profileData);

// 处理头像选择

// 编辑昵称
const editNickname = () => {
  isEditingNickname.value = true;
  tempNickname.value = user.value.nickname;
  nextTick(() => {
    nicknameInput.value?.focus();
  });
};

const fetchUserProfile = async () => {
  try {
    const response = await apiClient.get('/api/getprofile');
    const profileData = response.data;
    
    user.value = {
      ...user.value,
      nickname: profileData.nickname || '用户昵称',
      avatarUrl: profileData.avatar_url || '',
      likesCount: profileData.likesCount || 0,
      likedByCount: profileData.likedByCount || 0,
      recentVisitorsCount: profileData.recentVisitorsCount || 0,
    };
  } catch (error) {
    console.error('获取用户资料失败', error);
    showToast('获取用户资料失败');
  }
};

// 上传头像
const handleAvatarChange = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    // 检查文件大小（限制5MB）
    if (file.size > 5 * 1024 * 1024) {
      showToast('图片大小不能超过5MB');
      return;
    }
    
    // 检查文件类型
    if (!file.type.startsWith('image/')) {
      showToast('请选择图片文件');
      return;
    }
    
    // 创建预览URL
    const previewUrl = URL.createObjectURL(file);
    user.value.avatarUrl = previewUrl;
    
    try {
      // 创建FormData并上传文件
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiClient.post('/api/upload-avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      // 更新头像URL为服务器返回的URL
      user.value.avatarUrl = response.data.avatar_url;
      showToast('头像更新成功');
    } catch (error) {
      console.error('头像上传失败', error);
      showToast('头像上传失败');
    } finally {
      // 重置文件输入框
      target.value = '';
    }
  }
};

// 保存昵称
const saveNickname = async () => {
  if (tempNickname.value.trim()) {
    try {
      // 调用更新昵称API
      await apiClient.post('/api/update-nickname', {
        nickname: tempNickname.value.trim(),
      });
      
      user.value.nickname = tempNickname.value.trim();
      showToast('昵称更新成功');
    } catch (error) {
      console.error('昵称更新失败', error);
      showToast('昵称更新失败');
    } finally {
      isEditingNickname.value = false;
    }
  } else {
    isEditingNickname.value = false;
  }
};

// 取消编辑
const cancelEdit = () => {
  isEditingNickname.value = false;
  tempNickname.value = '';
};

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

  padding-bottom: 100px; /* 为底部TabBar留出空间，包含iOS安全区域 */
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
  position: relative;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.avatar-wrapper:hover {
  transform: scale(1.05);
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: #D9D9D9;
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.avatar-placeholder {
  font-size: 24px;
  color: white;
  font-weight: bold;
}

.edit-hint {
  position: absolute;
  bottom: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 10px;
  color: #666;
  white-space: nowrap;
}

.profile-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.nickname-container {
  text-align: right;
  margin-bottom: 8px;
}

.nickname {
  font-size: 20px;
  color: #333;
  font-weight: 500;
  margin-bottom: 16px;
  align-self: flex-start;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
  display: inline-block;
}

.nickname:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.nickname-edit {
  position: relative;
  display: inline-block;
}

.nickname-input {
  font-size: 20px;
  font-weight: 500;
  color: #333;
  border: 2px solid #D75670;
  border-radius: 4px;
  padding: 4px 8px;
  background: white;
  outline: none;
  text-align: right;
  min-width: 120px;
}

.char-count {
  position: absolute;
  top: -20px;
  right: 0;
  font-size: 10px;
  color: #666;
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