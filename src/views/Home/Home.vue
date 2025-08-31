<template>
  <div class="home-container">
    <!-- 骨架屏 - 完全使用 Vant4 Skeleton 重构 -->
    <div v-if="isLoading || !isReady" class="skeleton-container">
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
    <div v-else class="page-content">
      <!-- 滚动标语 - 替换原搜索框 -->
      <div class="notice-container">
        <van-notice-bar
          left-icon="volume-o"
          background="#EBE3D7"
          color="#6A6A6A"
          scrollable
          class="notice-bar"
        >
          {{ slogan }}
        </van-notice-bar>
      </div>

      <!-- 三个功能卡片 -->
      <div class="action-cards">
        <div class="action-card" @click="goToChat">
          <div class="action-icon">
            <van-icon name="service" size="24" color="#6A6A6A" />
          </div>
          <div class="action-title">联系陈姐</div>
        </div>

        <div ref="qrTriggerRef" class="action-card" @click="showQR = true">
          <div class="action-icon">
            <van-icon name="contact" size="24" color="#6A6A6A" />
          </div>
          <div class="action-title">抖音/微信</div>
          <van-popover
  v-model:show="showQR"
  :reference="qrTriggerRef"
  placement="bottom"
  :offset="[0, 12]"
  class="qr-popover"
>
  <div class="qr-panel">
    <van-swipe
      :loop="false"
      :autoplay="0"
      indicator-color="transparent"
      style="width: 220px"
    >
      <van-swipe-item class="qr-item">
        <img class="qr-img" :src="douyinQr" />
        <span class="qr-label">抖音：天顺婚介</span>
      </van-swipe-item>

      <van-swipe-item class="qr-item">
        <img class="qr-img" :src="wechatQr" />
        <span class="qr-label">微信：陈姐</span>
      </van-swipe-item>
    </van-swipe>
  </div>
</van-popover>
        </div>

        <div class="action-card" @click="handleAction('reward')">
          <div class="action-icon">
            <van-icon name="point-gift
" size="24" color="#6A6A6A" />
          </div>
          <div class="action-title">打赏</div>
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
                  <div class="heart-icon" :class="{ liked: likeStore.hasLiked(user.id) }">
                    <van-icon name="like" />
                  </div>
                </div>
                <div class="info-line">
                  <div class="info-value">{{ getBirthYear(user.birth_date)+'年' }}<img :src="getLevelIcon(user.points)" style="width:36px;height:20px;margin-left:2px;vertical-align:-4px;" /></div>
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
  <RewardPopup v-model="showRewardPopup" />
</template>

<script setup lang="ts">
import { ref, onMounted , computed} from 'vue';
import { useExploreStore } from '@/store/exploreStore';
import TabBar from '@/components/TabBar.vue';
import { Skeleton, NoticeBar } from 'vant';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authStore';
import { useUserInfoStore } from '@/store/userinfo'
import { useUserListStore } from '@/store/userList'
import apiClient from '@/plugins/axios';
import { useLikeStore } from '@/store/likeStore';
import { usePaymentStore } from '@/store/paymentStore'; 
import { triggerWechatLogin } from '@/utils/authUtils'; 
import douyinQr from '@/assets/images/douyin_qr.png';
import wechatQr from '@/assets/images/wechat_qr.png';
import RewardPopup from '@/components/RewardPopup.vue';
import { ALL_TABS, ICON_MAP, type TabItem, type IconType, type DynamicTabItem } from '@/config/tabs'
import { getLevelIcon } from '@/utils/levelIcon';


const showRewardPopup = ref(false);
const showQR   = ref(false);
const qrTriggerRef = ref<HTMLElement | null>(null);
const slogan = ref("欢迎来到天顺，祝您早日找到心仪的另一半！❤️");
const exploreStore = useExploreStore();
const userStore = useUserInfoStore()
const userListStore = useUserListStore()
const paymentStore = usePaymentStore();
const activeTab = ref('home');
const router = useRouter();
const isLoading = ref(true);
const authError = ref<string | null>(null);
const authStore = useAuthStore();
const likeStore = useLikeStore();
const newcomers = ref<any[]>([]);
const isNewcomersLoading = ref(true); 
const recommendedUsers = ref<any[]>([]);
const isReady = ref(false); 

const filteredRecommendedUsers_old = computed(() => {
  if (!recommendedUsers.value.length) return [];
  
const currentUserGender = userStore.profile?.gender;
  if (!currentUserGender) return recommendedUsers.value;
  
  return recommendedUsers.value.filter(user => 
    currentUserGender === 'male' ? user.gender === 'female' : user.gender === 'male'
  );
});

const filteredRecommendedUsers = computed(() => {
  if (!recommendedUsers.value.length) return [];

  const currentUserGender = userStore.profile?.gender;
  if (currentUserGender === undefined) return []; // ✅ 等待 gender 加载完成

  return recommendedUsers.value.filter(user =>
    currentUserGender === 'male' ? user.gender === 'female' : user.gender === 'male'
  );
});

const fetchSlogan = async () => {
  try {
    const res = await apiClient.get('/api/slogan-latest');
    slogan.value = res.data.slogan;
  } catch (error) {
    console.error('获取标语失败:', error);
  }
};

// 新增方法：从生日获取年份
const getBirthYear = (birthDate: string) => {
  return birthDate ? new Date(birthDate).getFullYear() : '未知';
};

// 新增方法：截断过长的简介
const truncateMemo = (text: string, maxLength: number) => {
  if (!text) return '';
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
};

const goToChat = () => {
  router.replace('/chat');
};

const checkAuth = async () => {
  isLoading.value = true;
  authError.value = null;
  try {
    console.log('看看首页的token：',authStore.token);
    if(!authStore.token) {
      triggerWechatLogin();
    }
  } catch (error: any) {
    console.error('Authentication check failed:', error);
    authError.value = error.message || '认证检查失败，请稍后重试。';
  } finally {
    isLoading.value = false;
  }
};

const checkFirstTimeUser = async () => {
  try {
    const res = await apiClient.get('/api/check/user_first');
    if (res.data.result === 0) {
      // 首次使用，跳转到登记页
      router.replace('/profile-setup');
    }
  } catch (error) {
    console.error('检查用户首次状态失败:', error);
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

const initializeUserData = async () => {
  if (!paymentStore.isPaid) return;
  
  try {
    await userListStore.initializeStore();
    await userStore.fetchUserProfile();
    // await likeStore.fetchLikes();
  } catch (error) {
    console.error('用户数据初始化失败:', error);
  }
};

const fetchDynamicMenu = async () => {
  try {
    if (!authStore.token) return [];
    
    const response = await apiClient.get('/api/menu');
    return response.data.menuItems.map((item: any) => ({
      id: item.id,
      label: item.label,
      iconType: item.iconType, // 保留类型标识
      to: item.to,
      requiredPermission: item.requiredPermission || null
    }));
  } catch (error) {
    console.error('获取动态菜单失败:', error);
    return [];
  }
}

// onMounted(async() => {
  
//   exploreStore.loadState();
//   await checkAuth();
//   console.log('首页加载',authStore.token)
//   if (authStore.token) {
//     await checkFirstTimeUser(); // 👈 加在这里
//   }
//   await fetchSlogan(); // ✅ 获取标语
//   await fetchNewcomers();
//   await fetchInter()
//   // console.log('authStore.token: ',authStore.token)
//   if (authStore.token) {
//     const dynamicTabs = await fetchDynamicMenu()
//     authStore.setMenuItems(dynamicTabs)
//     // 检查支付状态（如果尚未加载）
//     if (!paymentStore.isPaid && !paymentStore.loading) {
//       try {
//         await paymentStore.checkPaymentStatus();
//       } catch (error) {
//         console.error('支付状态检查失败:', error);
//       }
//     }
//     console.log('tabs: ',tabs.value)

//     // 如果已支付，立即初始化用户数据
//     if (paymentStore.isPaid) {
//       await initializeUserData();
//     }
//   }
// });

onMounted(async () => {
  isLoading.value = true;
  isReady.value = false;

  try {
    await fetchSlogan();
    exploreStore.loadState();
    await checkAuth();

    if (authStore.token) {
      await checkFirstTimeUser(); // 跳转 profile-setup

      // 并行加载所有必要数据
      await Promise.all([
        userStore.fetchUserProfile(), // 获取 gender
        fetchInter(), // 获取推荐用户
        fetchNewcomers(),
        fetchDynamicMenu().then(authStore.setMenuItems),
        paymentStore.checkPaymentStatus(),
      ]);

      if (paymentStore.isPaid) {
        await initializeUserData();
      }
    }

    isReady.value = true;
  } catch (error) {
    console.error('页面初始化失败:', error);
  } finally {
    isLoading.value = false;
  }
});

// 处理功能卡片点击
const handleAction = (type: string) => {
  switch (type) {
    case 'contact':
      // 联系红娘逻辑
      console.log('联系红娘');
      break;
    case 'link':
      // 外部链接逻辑
      console.log('打开外部链接');
      break;
    case 'reward':
      // 打赏逻辑
      showRewardPopup.value = true;
      console.log('打赏');
      break;
  }
};

const tabs = computed(() => [...ALL_TABS, ...authStore.menuItems]);

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

/* 滚动标语容器 */
.notice-container {
  margin-bottom: 16px;
  border-radius: 50px;
  overflow: hidden;
  background-color: #EBE3D7;
}

.notice-bar {
  border-radius: 50px;
  padding: 12px 16px;
}

/* 功能卡片容器 */
.action-cards {
  display: flex;
  justify-content: space-between;
  margin-bottom: 24px;
}

.action-card {
  background-color: #fff;
  border-radius: 8px;
  border: 1px solid #D9D9D9;
  width: calc(33.333% - 10px);
  height: 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #F2EEE8;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.action-title {
  font-size: 14px;
  color: #6A6A6A;
  font-weight: 500;
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

.recommend-card .heart-icon {
  font-size: 20px;
  color: #ccc; /* 默认灰色 */
  transition: color 0.3s;
}

.recommend-card .heart-icon.liked {
  color: #ff4757; /* 喜欢时变为红色 */
}

.card-image-container {
  width: 100%;
  height: 243px; /* 调整为正方形比例 */
  overflow: hidden;
  position: relative;
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.level-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #FFD700, #FFA500);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  z-index: 2;
}

.level-badge img {
  width: 24px;
  height: 24px;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3));
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

/* 滚动条样式调整 */
:deep(.van-notice-bar__wrap) {
  height: 100%;
  display: flex;
  align-items: center;
}

:deep(.van-notice-bar__content) {
  font-size: 14px;
  font-weight: 500;
  color: #6A6A6A;
}

/* Popover 外壳颜色、圆角与首页卡片一致 */
.qr-popover {
  --van-popover-background: #FFFFFF;
  --van-popover-border-radius: 8px;
  --van-popover-padding: 0;
}

.qr-popover.van-popover--bottom {
  /* 保证水平居中 */
  left: 50% !important;
  transform: translateX(-50%) !important;
  margin-top: 12px;            /* 与触发按钮的距离 */
}

/* 面板 */
.qr-panel {
  width: 260px;
  padding: 20px;
  background: #FFFFFF;
  border-radius: 12px;
}

/* 每个 Swipe 项 */
.qr-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.qr-img {
  width: 200px;
  height: 300px;
  border-radius: 8px;
  object-fit: cover;
}
.qr-label {
  display: block;
  margin-top: 10px;
  font-size: 15px;
  color: #6A6A6A;
  text-align: center;
}
</style>