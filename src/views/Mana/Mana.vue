<template>
  <div class="mana-container">
    <!-- 标题栏 -->
    <div class="header">
      <h1 class="title">用户管理</h1>
      <div class="filter-tabs">
        <span 
          class="filter-tab" 
          :class="{ active: activeTab === 'all' }"
          @click="activeTab = 'all'"
        >
          全部用户
        </span>
        <span 
          class="filter-tab" 
          :class="{ active: activeTab === 'male' }"
          @click="activeTab = 'male'"
        >
          男生
        </span>
        <span 
          class="filter-tab" 
          :class="{ active: activeTab === 'female' }"
          @click="activeTab = 'female'"
        >
          女生
        </span>
      </div>
    </div>

    <!-- 用户列表 -->
    <div 
      class="user-grid" 
      v-bind="containerProps" 
      :style="{ height: listHeight + 'px' }"
    >
      <div v-bind="wrapperProps">
        <div 
          v-for="{ index, data: user } in virtualList" 
          :key="index" 
          class="user-card"
        >
          <div class="card-header">
            <div class="avatar-container">
              <van-image
                width="48"
                height="48"
                :src="getAvatarUrl(user.avatar)"
                round
                fit="cover"
                lazy-load
              >
                <template v-slot:loading>
                  <div class="avatar-placeholder">
                    <van-icon name="user-circle-o" size="24" />
                  </div>
                </template>
                <template v-slot:error>
                  <div class="avatar-placeholder">
                    <van-icon name="user-circle-o" size="24" />
                  </div>
                </template>
              </van-image>
            </div>
            <div class="user-info">
              <div class="name">{{ user.id +' ' +user.nickname }}</div>
              <div class="meta">
                <span class="gender" :class="user.gender">{{ 
                  user.gender === 'male' ? '♂' : '♀' 
                }}</span>
                <span class="likes">
                  <van-icon name="like" color="#D75670" /> {{ user.like_count }}
                </span>
                <span class="top-badge" v-if="user.is_top">
                  <van-icon name="fire" color="#FFA940" /> 置顶
                </span>
              </div>
            </div>
          </div>
          
          <div class="card-footer">
            <div class="status">
              <span class="status-badge" :class="{ 
                active: user.state===1, 
                inactive: user.state!=1 
              }">
                {{ user.state===1 ? '启用' : '禁用' }}
              </span>
            </div>
            <van-switch 
              v-model="user.state" 
              size="24px"
              :loading="user.updating"
              active-color="#D75670"
              inactive-color="#EBE3D7"
              @change="updateUserStatus(user)"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <van-loading type="spinner" color="#D75670" size="24px" />
      <span>加载中...</span>
    </div>

    <!-- 无数据提示 -->
    <div v-if="!loading && filteredUsers.length === 0" class="no-data">
      <van-icon name="user-o" size="48" color="#EBE3D7" />
      <p>暂无用户数据</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useVirtualList } from '@vueuse/core';
import { 
  Image as VanImage, 
  Switch, 
  Loading, 
  Toast,
  showToast,
  showFailToast, 
  showSuccessToast, 
  Icon,
  Lazyload 
} from 'vant';
import { 
  getUsersWithLikes, 
  updateUserActiveStatus, 
  type AdminUser 
} from '@/api/admin'

type LocalAdminUser = AdminUser & {
  updating?: boolean
}
const activeTab = ref<'all' | 'male' | 'female'>('all')
const users = ref<LocalAdminUser[]>([])
const loading = ref(true);

// 计算列表高度（根据视口高度减去标题高度）
const listHeight = computed(() => {
  return window.innerHeight - 80; // 根据实际标题高度调整
});


// 获取用户头像URL
const getAvatarUrl = (avatar: string) => {
  return avatar ? `avatars/${avatar}` : '';
};

// 过滤用户
const filteredUsers = computed(() => {
  if (activeTab.value === 'all') return users.value;
  return users.value.filter(u => u.gender === activeTab.value);
});

// 按点赞数排序
const sortedUsers = computed(() => {
  return [...filteredUsers.value].sort((a, b) => b.like_count - a.like_count);
});

// 虚拟列表
const { list: virtualList, containerProps, wrapperProps } = useVirtualList(
  sortedUsers,
  {
    itemHeight: 140, // 固定卡片高度
    overscan: 10
  }
);

// 更新用户状态
const updateUserStatus = async (user: LocalAdminUser) => {
  try {
    // 设置更新状态
    const originalStatus = user.is_active;
    user.updating = true;
    
    // 调用API更新状态
    await updateUserActiveStatus(user.id, user.is_active);
    
    showSuccessToast(`用户已${user.is_active ? '启用' : '冻结'}`);
  } catch (error) {
    console.error('更新用户状态失败:', error);
    showFailToast('操作失败');
    // 回退状态
    user.is_active = !user.is_active;
  } finally {
    user.updating = false;
  }
};

// 加载用户数据
const loadUsers = async () => {
  try {
    loading.value = true;
    const data = await getUsersWithLikes();
    // 添加更新状态字段
    users.value = data.map(user => ({
      ...user,
      updating: false
    }));
  } catch (error) {
    console.error('加载用户数据失败:', error);
    showFailToast('加载数据失败');
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadUsers();
});
</script>

<style scoped>
.mana-container {
  background-color: #F2EEE8;
  min-height: 100vh;
  padding: 16px;
  font-family: "Microsoft YaHei", sans-serif;
  display: flex;
  flex-direction: column;
}

.header {
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #EBE3D7;
}

.title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 16px;
}

.filter-tabs {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: thin;
  scrollbar-color: #D75670 #EBE3D7;
}

.filter-tabs::-webkit-scrollbar {
  height: 4px;
}

.filter-tabs::-webkit-scrollbar-track {
  background: #EBE3D7;
  border-radius: 2px;
}

.filter-tabs::-webkit-scrollbar-thumb {
  background-color: #D75670;
  border-radius: 2px;
}

.filter-tab {
  background-color: #EBE3D7;
  color: #6A6A6A;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.3s;
  flex-shrink: 0;
}

.filter-tab.active {
  background-color: #D75670;
  color: white;
}

.user-grid {
  flex: 1;
  position: relative;
  overflow: auto;
}

.user-card {
  height: 140px;
  background-color: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.avatar-container {
  margin-right: 12px;
}

.avatar-placeholder {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #f0f0f0;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #999;
}

.user-info {
  flex: 1;
}

.name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

.meta {
  display: flex;
  gap: 12px;
  font-size: 14px;
  color: #888;
  flex-wrap: wrap;
}

.gender.male {
  color: #6495ED;
}

.gender.female {
  color: #FF69B4;
}

.likes, .top-badge {
  display: flex;
  align-items: center;
  gap: 4px;
}

.top-badge {
  background-color: #FFF7E6;
  color: #FA8C16;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f5f5f5;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.status-badge.active {
  background-color: rgba(215, 86, 112, 0.1);
  color: #D75670;
}

.status-badge.inactive {
  background-color: rgba(107, 114, 128, 0.1);
  color: #6B7280;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: #888;
}

.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #888;
  text-align: center;
}

.no-data p {
  margin-top: 16px;
  font-size: 14px;
}
</style>