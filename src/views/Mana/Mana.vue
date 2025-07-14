<template>
  <div class="mana-container">
    <van-floating-bubble
      v-model:offset="offset"
      axis="xy"
      magnetic="x"
      icon="revoke"
      :size="54"
      :gap="10"
      @click="goBack"
      style="--van-floating-bubble-background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);"
    />
    <!-- 搜索和过滤栏（固定在顶部） -->
    <div class="sticky-header" ref="headerRef">
      <!-- 搜索框 -->
      <div class="search-container">
        <van-search
          v-model="searchKeyword"
          placeholder="搜索用户"
          shape="round"
          background="#F2EEE8"
          @search="onSearch"
        />
      </div>
      <!-- 过滤标签 -->
      <div class="filter-tabs">
        <span 
          class="filter-tab" 
          :class="{ active: activeTab === 'all' }"
          @click="setActiveTab('all')"
        >
          全部用户
        </span>
        <span 
          class="filter-tab" 
          :class="{ active: activeTab === 'male' }"
          @click="setActiveTab('male')"
        >
          男生
        </span>
        <span 
          class="filter-tab" 
          :class="{ active: activeTab === 'female' }"
          @click="setActiveTab('female')"
        >
          女生
        </span>
        <!-- <span 
          class="filter-tab" 
          :class="{ active: activeTab === 'top' }"
          @click="setActiveTab('top')"
        >
          已置顶
        </span> -->
      </div>
    </div>

    <!-- 用户列表 - 使用Vant List组件 -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
      >
        <div 
          v-for="user in list" 
          :key="user.id" 
          class="user-card"
          
        >
          <div class="card-header" @click="goToProfile(user.id)">
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
              <div class="name" v-if="user.nickname">{{ user.id +' ' + user.nickname }}</div>
              <div class="name" v-else>{{ user.id }}</div>
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
            <!-- 到期时间 -->
            <div class="expire">
              {{ formatExpireDate(user.expire_at) }}
            </div>
            <div class="actions">
              <!-- 置顶按钮 -->
              <van-switch 
                @click.stop
                :model-value="user.is_top"
                :loading="user.topping"
                size="24px"
                active-color="#FFA940"
                inactive-color="#EBE3D7"
                @change="toggleTopStatus(user, $event)"
              >
                <template #node>
                  <div class="icon-wrapper">
                    <van-icon 
                      :name="user.is_top ? 'back-top' : 'minus'" 
                      :color="user.is_top ? '#FFA940' : '#999'" 
                    />
                  </div>
                </template>
              </van-switch>
              
              <!-- 状态开关（使用图标） -->
              <van-switch 
                :model-value="user.state === 1"
                :loading="user.updating"
                size="24px"
                active-color="#D75670"
                inactive-color="#EBE3D7"
                @change="updateUserStatus(user, $event)"
              >
                <template #node>
                  <div class="icon-wrapper">
                    <van-icon 
                      :name="user.state === 1 ? 'success' : 'cross'" 
                      :color="user.state === 1 ? '#D75670' : '#999'" 
                    />
                  </div>
                </template>
              </van-switch>
            </div>
          </div>
        </div>
      </van-list>
    </van-pull-refresh>

    <!-- 无数据提示 -->
    <div v-if="!loading && list.length === 0 && finished" class="no-data">
      <van-icon name="user-o" size="48" color="#EBE3D7" />
      <p>暂无用户数据</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getPreviousRoute } from '@/utils/routeHistory';
import { 
  Image as VanImage, 
  Switch, 
  Loading, 
  Toast,
  showToast,
  showFailToast, 
  showSuccessToast, 
  Icon,
  Lazyload,
  Search as VanSearch,
  List as VanList,
  PullRefresh as VanPullRefresh
} from 'vant';
import { 
  getUsersWithLikes, 
  updateUserActiveStatus, 
  toggleUserTopStatus,
  type AdminUser 
} from '@/api/admin'
import type { RouteLocationNormalized } from 'vue-router';

type LocalAdminUser = AdminUser & {
  updating?: boolean;
  topping?: boolean;
}
const router = useRouter();
// 分页相关状态
const list = ref<LocalAdminUser[]>([]); // 当前列表数据
const loading = ref(false);             // 加载状态
const finished = ref(false);            // 是否加载完成
const refreshing = ref(false);          // 是否正在刷新
const currentPage = ref(1);             // 当前页码
const pageSize = ref(20);               // 每页数量

const activeTab = ref<'all' | 'male' | 'female' | 'top'>('all')
const searchKeyword = ref('');
const offset = ref({ x: 0.05 * window.innerWidth, y: 0.03 * window.innerHeight });

const goToProfile = (id: number) => {
  router.replace(`/profile/${id}`);
};

const goBack = () => {
  //const previousRoute = getPreviousRoute();
  //if (previousRoute) {
  //  router.replace({ path: previousRoute.path, query: previousRoute.query, params: previousRoute.params });
  //} else {
    router.replace('/manacenter');
  //}
};


// 格式化到期时间
const formatExpireDate = (dateStr: string | null) => {
  if (!dateStr) return '永久';
  const date = new Date(dateStr);
  return date.toISOString().split('T')[0]+'到期';
};

// 获取用户头像URL
const getAvatarUrl = (avatar: string) => {
  return avatar ? `avatars/${avatar}` : '';
};

// 设置激活标签
const setActiveTab = (tab: 'all' | 'male' | 'female' | 'top') => {
  activeTab.value = tab;
  onRefresh();
}

// 搜索处理
const onSearch = () => {
  onRefresh();
}

// 下拉刷新
const onRefresh = () => {
  // 清空列表数据
  list.value = [];
  currentPage.value = 1;
  finished.value = false;
  
  // 重新加载数据
  loading.value = true;
  onLoad();
};

// 加载更多数据
const onLoad = async () => {
  if (refreshing.value) {
    refreshing.value = false;
  }

  try {
    // 调用API获取数据
    const data = await getUsersWithLikes({
      gender: activeTab.value === 'all' ? undefined : 
              activeTab.value === 'top' ? undefined : activeTab.value,
      isTop: activeTab.value === 'top' ? true : undefined,
      keyword: searchKeyword.value || undefined,
      page: currentPage.value,
      pageSize: pageSize.value
    });

    // 处理返回数据
    const users = data.map(user => ({
      ...user,
      updating: false,
      topping: false
    }));

    // 添加到列表
    list.value = [...list.value, ...users];
    
    // 更新加载状态
    loading.value = false;

    // 检查是否已加载所有数据
    if (users.length < pageSize.value) {
      finished.value = true;
    } else {
      currentPage.value++;
    }
  } catch (error) {
    console.error('加载用户数据失败:', error);
    showFailToast('加载数据失败');
    loading.value = false;
    finished.value = true;
  }
};

// 更新用户状态
const updateUserStatus = async (user: LocalAdminUser, newState: boolean) => {
  try {
    user.updating = true;
    await updateUserActiveStatus(user.id, newState);
    user.state = newState ? 1 : 0;
    showSuccessToast(`用户已${newState ? '启用' : '冻结'}`);
  } catch (error) {
    console.error('更新用户状态失败:', error);
    showFailToast('操作失败');
  } finally {
    user.updating = false;
  }
};

// 切换置顶状态
const toggleTopStatus = async (user: LocalAdminUser, isTop: boolean) => {
  try {
    user.topping = true;
    await toggleUserTopStatus(user.id, isTop);
    user.is_top = isTop;
    showSuccessToast(isTop ? '已置顶' : '已取消置顶');
  } catch (error) {
    console.error('置顶操作失败:', error);
    showFailToast('操作失败');
  } finally {
    user.topping = false;
  }
};

// 初始化加载数据
onMounted(() => {
  onLoad();
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
  overflow: hidden;
}

.sticky-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: #F2EEE8;
  padding-bottom: 12px;
}

/* 优化搜索框样式 */
.search-container {
  margin-bottom: 12px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
}

.user-card {
  height: 140px;
  background-color: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
}

.user-card:active {
  transform: scale(0.98); /* 点击时轻微缩小 */
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1); /* 点击时阴影减小 */
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

.expire {
  font-size: 12px;
  color: #888;
}

.actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.icon-wrapper .van-icon {
  font-size: 16px;
  line-height: 1;
}

.icon-wrapper .van-icon-success {
  color: #fff;
}

.icon-wrapper .van-icon-cross {
  color: #fff;
}

.icon-wrapper .van-icon-back-top {
  color: #fff;
}

.icon-wrapper .van-icon-minus {
  color: #fff;
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