<template>
  <div class="home-container">
    <!-- 骨架屏 - 完全使用 Vant4 Skeleton 重构 -->
    <div v-if="isLoading" class="skeleton-container">
      <!-- 搜索框骨架 -->
      <van-skeleton 
        :row="1" 
        :row-width="['100%']" 
        :row-height="48"
        class="skeleton-search"
      />
      
      <!-- 新闻卡片骨架 -->
      <van-skeleton 
        :row="0"
        class="skeleton-news"
        style="height: 150px; border-radius: 8px;"
      />
      
      <!-- 新人展示骨架 -->
      <div class="skeleton-section">
        <van-skeleton 
          title 
          title-width="120px" 
          :row="0"
          class="skeleton-title"
        />
        <div class="skeleton-cards">
          <van-skeleton 
            class="skeleton-card"
            avatar
            avatar-size="48px"
            avatar-shape="round"
            :row="2"
            :row-width="['70%', '50%']"
          />
        </div>
      </div>
      
      <!-- 推荐板块骨架 -->
      <div class="skeleton-section">
        <van-skeleton 
          title 
          title-width="120px" 
          :row="0"
          class="skeleton-title"
        />
        <div class="skeleton-cards">
          <van-skeleton 
            class="skeleton-recommend-card"
            style="height: 320px; width: 200px;"
          />
        </div>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-else-if="authError" class="error-container">
      <div class="error-icon">⚠️</div>
      <div class="error-title">认证失败</div>
      <div class="error-message">{{ authError }}</div>
      <button class="retry-button">重试</button>
    </div>

    <!-- 页面内容 -->
    <div v-else class="page-content" @click="handlePageClick">
      <!-- 搜索框 -->
      <div class="search-container" @click.stop>
        <div class="search-card" :class="{ focused: isSearchFocused }">
          <div class="search-box">
            <t-icon name="search" class="search-icon" />
            <input 
              type="text" 
              placeholder="搜索" 
              class="search-input" 
              v-model="searchKeyword"
              @focus="handleSearchFocus"
              @keyup.enter="handleSearch"
            />
          </div>
          
          <!-- <div class="search-options" v-if="isSearchFocused">
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
          </div> -->
        </div>
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
        <div v-if="isNewcomersLoading" class="newcomer-skeleton">
          <van-skeleton 
            v-for="i in 1" 
            :key="'skeleton'+i" 
            class="skeleton-card" 
            :row="2" 
            :row-width="['60%', '40%']" 
            avatar
            avatar-size="48px"
            avatar-shape="round"
            title
            title-width="40%"
          />
        </div>
        <van-swipe 
          v-else
          class="newcomer-swipe" 
          :loop="true" 
          :width="180" 
          :height="80" 
          :autoplay="5000" 
          indicator-color="transparent"
        >
          <van-swipe-item v-for="(user, index) in newcomers" :key="index">
            <div class="newcomer-card" @click="goToDetail(user.id)">
              <div class="avatar">
                <img 
                  :src="user.avatarUrl" 
                  alt="头像"
                  style="width: 48px; height: 48px; border-radius: 50%; object-fit: cover;"
                />
              </div>
              <div class="info">
                <div class="title">{{ user.displayTitle }}</div>
                <div class="subtitle">{{ user.displaySubtitle }}</div>
              </div>
            </div>
          </van-swipe-item>
        </van-swipe>
      </div>

      <!-- 推荐板块 -->
      <div class="recommend-section">
        <h2 class="section-title">可能感兴趣</h2>
        <van-swipe class="recommend-swipe" :loop="true" :width="210" :height="330" indicator-color="transparent">
          <van-swipe-item v-for="user in filteredRecommendedUsers" :key="user.id">
            <div class="recommend-card" @click="goToDetail(user.id)">
              <div class="card-image-container">
                <img 
                  :src="user.first_photo ? '/photo/' + user.first_photo : (user.gender === 'female' ? '/avatars/female_def.png' : '/avatars/male_def.png')" 
                  alt="照片"
                  class="card-image"
                />
              </div>
              <div class="card-content">
                <div class="user-header">
                  <div class="user-id">编号{{ user.id }}</div>
                  <div class="heart-icon">
                    <van-icon name="like" />
                  </div>
                </div>
                <div class="info-line">
                  <div class="info-value">{{ getBirthYear(user.birth_date)+'年' }}</div>
                </div>
                <div class="desc">{{ truncateMemo(user.mem, 36) }}</div>
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
import { ref, onMounted , computed} from 'vue';
import { useExploreStore } from '@/store/exploreStore';
import TabBar from '@/components/TabBar.vue';
import { Skeleton } from 'vant';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authStore';
import { useUserInfoStore } from '@/store/userinfo'
import { useUserListStore } from '@/store/userList'
import apiClient from '@/plugins/axios';
import { useLikeStore } from '@/store/likeStore';
// 导入图标
import homeIcon from '@/assets/icons/home.svg';
import homeSelectedIcon from '@/assets/icons/home-selected.svg';
import compassIcon from '@/assets/icons/compass.svg';
import compassSelectedIcon from '@/assets/icons/compass-selected.svg';
import likeIcon from '@/assets/icons/like.svg';
import likeSelectedIcon from '@/assets/icons/like-selected.svg';
import smileIcon from '@/assets/icons/smile.svg';
import smileSelectedIcon from '@/assets/icons/smile-selected.svg';

const exploreStore = useExploreStore();
const userStore = useUserInfoStore()
const userListStore = useUserListStore()
const activeTab = ref('home');
const router = useRouter();
const isSearchFocused = ref(false);
const isLoading = ref(true);
const authError = ref<string | null>(null);
const authStore = useAuthStore();
const likeStore = useLikeStore();
const newcomers = ref<any[]>([]);
const isNewcomersLoading = ref(true); 
const recommendedUsers = ref<any[]>([]);
const searchKeyword = computed({
  get: () => exploreStore.state.searchKeyword,
  set: (value) => exploreStore.state.searchKeyword = value
});

const filteredRecommendedUsers = computed(() => {
  if (!recommendedUsers.value.length) return [];
  
const currentUserGender = userStore.profile?.gender;
  if (!currentUserGender) return recommendedUsers.value;
  
  return recommendedUsers.value.filter(user => 
    currentUserGender === 'male' ? user.gender === 'female' : user.gender === 'male'
  );
});

// 新增方法：从生日获取年份
const getBirthYear = (birthDate: string) => {
  return birthDate ? new Date(birthDate).getFullYear() : '未知';
};

// 新增方法：截断过长的简介
const truncateMemo = (text: string, maxLength: number) => {
  if (!text) return '';
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
};

const checkAuth = async () => {
  isLoading.value = true;
  authError.value = null;
  try {
    console.log('看看首页的token：',authStore.token);
  } catch (error: any) {
    console.error('Authentication check failed:', error);
    authError.value = error.message || '认证检查失败，请稍后重试。';
  } finally {
    isLoading.value = false;
  }
};

// 获取新人数据的方法
const fetchNewcomers = async () => {
  try {
    const response = await apiClient.get('/api/newcomers');
    newcomers.value = response.data.newcomers.map((user: any, index: number) => ({
      ...user,
      // 格式化显示标题和副标题
      displayTitle: `编号${user.id}`,
      displaySubtitle: user.birth_date ? new Date(user.birth_date).getFullYear() + '年' : '未知',
      // 处理头像URL
      avatarUrl: user.first_photo 
        ? `/photo/${user.first_photo}` 
        : `/avatars/${user.gender === 'female' ? 'female_def.png' : 'male_def.png'}`
    }));
  } catch (error) {
    console.error('获取新人数据失败:', error);
  }finally {
    isNewcomersLoading.value = false; // 结束加载
  }
};

const fetchInter = async()=> {
  try {
    const response = await apiClient.get('/api/interested');
    recommendedUsers.value = response.data;
  } catch (error) {
    console.error('获取感兴趣数据失败:', error);
  }finally {
     // 结束加载
  }
}

const retryAuth = () => {
  checkAuth();
};

const handleSearch = () => {
  // 保存状态到本地存储
  exploreStore.saveState();
  
  // 跳转到探索页面
  router.replace('/explore');
  
  // 关闭搜索框
  closeSearch();
};

onMounted(async() => {
  exploreStore.loadState();
  await checkAuth();
  await userListStore.initializeStore();
  await userStore.fetchUserProfile();
  await likeStore.fetchLikes()
  await fetchNewcomers();
  await fetchInter()
});

const handleSearchFocus = () => {
  isSearchFocused.value = true;
};

const closeSearch = () => {
  isSearchFocused.value = false;
};

// 点击页面其他区域关闭搜索框
const handlePageClick = () => {
  if (isSearchFocused.value) {
    closeSearch();
  }
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
    router.replace(tab.to);
  }
};

const goToDetail = (id: number) => {
  router.replace(`/detail/${id}`);
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

/* 骨架屏样式 - 更新为Vant Skeleton */
.skeleton-container {
  flex: 1;
  margin-bottom: 60px;
  padding: 0 8px;
}

.skeleton-search {
  height: 48px;
  border-radius: 24px;
  margin-bottom: 16px;
  overflow: hidden;
}

.skeleton-news {
  height: 150px;
  border-radius: 8px;
  margin-bottom: 24px;
  overflow: hidden;
}

.skeleton-section {
  margin-bottom: 24px;
}

.skeleton-title {
  margin-bottom: 16px;
  overflow: hidden;
}

.skeleton-cards {
  display: flex;
  gap: 8px;
}

.skeleton-card {
  width: 172px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
}

.skeleton-recommend-card {
  width: 200px;
  height: 320px;
  border-radius: 8px;
  overflow: hidden;
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

/* 搜索容器 */
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
  transition: all 0.5s cubic-bezier(0.18, 0.89, 0.32, 1.28);
  position: relative;
  z-index: 10;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  transform: translate3d(0, 0, 0);
}

.search-card.focused {
  border-radius: 12px;
  padding-bottom: 16px;
  position: relative;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  max-height: 300px;
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
  transition: all 0.3s ease;
}

.search-options {
  margin-top: 12px;
  animation: slideDown 0.4s cubic-bezier(0.18, 0.89, 0.32, 1.28) forwards;
  opacity: 0;
  transform-origin: top;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.search-option-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  transition: all 0.3s ease;
}

.option-label {
  width: 60px;
  font-size: 14px;
  color: #6A6A6A;
  transition: all 0.3s ease;
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
  transition: all 0.3s ease;
}

.clear-icon {
  position: absolute;
  right: 8px;
  color: #ccc;
  font-size: 16px;
  transition: all 0.3s ease;
}

/* 其他样式保持不变 */
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

/* 更新推荐卡片样式 */
.recommend-card {
  background-color: #FFFFFF;
  border-radius: 8px;
  width: 200px; /* 缩小卡片宽度 */
  height: 320px; /* 缩小卡片高度 */
  margin-right: 8px;
  position: relative;
  overflow: hidden;
  border: 1px solid #D9D9D9;
  display: flex;
  flex-direction: column;
}

.card-image-container {
  width: 100%;
  height: 243px; /* 调整为正方形比例 */
  overflow: hidden;
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-content {
  padding: 12px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.user-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.user-id {
  font-size: 14px;
  font-weight: bold;
  color: #6A6A6A; /* 改为灰色 */
}

.heart-icon {
  font-size: 20px;
  color: #ff4757;
}

.info-line {
  display: flex;
  margin-bottom: 8px;
}

.info-value {
  font-size: 12px; /* 统一字体大小 */
  color: #6A6A6A; /* 统一字体颜色 */
}

.desc {
  font-size: 12px;
  color: #666;
  line-height: 1.5;
  flex: 1;
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 4; /* 限制显示4行 */
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

/* 新增骨架屏样式 */
.newcomer-skeleton {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
}

/* 调整 Vant 骨架屏内部样式 */
:deep(.van-skeleton__avatar) {
  margin-right: 12px;
  background-color: #f0f0f0;
}

:deep(.van-skeleton__row) {
  background-color: #f0f0f0;
  border-radius: 4px;
  height: 16px;
  margin-top: 8px;
}
</style>