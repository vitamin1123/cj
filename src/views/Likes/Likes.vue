<template>
  <div class="likes-container">
    <div class="page-content">
      <div class="header">
        <h1 class="page-title">喜欢</h1>
        <!-- 添加筛选标签 -->
        <div class="filter-tags">
          <span 
            v-for="filter in filters" 
            :key="filter.id" 
            class="filter-tag" 
            :class="{ active: filter.active }"
            @click="toggleFilter(filter)">
            {{ filter.label }}
          </span>
        </div>
      </div>

      <!-- 根据当前筛选显示不同内容 -->
      <div class="likes-list" v-if="activeFilter === 'liked' && likedPeople.length > 0">
        <!-- 我喜欢的列表 -->
        <div v-for="person in likedPeople" :key="person.id" class="person-card" @click="goToDetail(person.id)">
          <div class="card-image">
            <img :src="getPersonImage(person)" />
            <div class="person-id-badge" :class="{ 'male-bg': person.gender === 'male', 'female-bg': person.gender === 'female' }">
              {{ person.id }}
            </div>
          </div>
          <div class="card-content">
            <div class="name">{{ person.nickname || `用户${person.id}` }}</div>
            <div class="height-container">
              <div class="height">{{ person.height }}cm</div>
              <div class="heart-icon" @click.stop="confirmRemoveLike(person)">
                <van-icon name="like" class="liked" />
              </div>
            </div>
            <div class="desc">{{ formatDescription(person.mem) }}</div>
            <div class="like-time">{{ formatLikeTime(person.created_at) }}</div>
          </div>
        </div>
      </div>

      <div class="likes-list" v-if="activeFilter === 'likedBy' && likedByPeople.length > 0">
        <!-- 喜欢我的列表 -->
        <div v-for="person in likedByPeople" :key="person.id" class="person-card" @click="goToDetail(person.id)">
          <div class="card-image">
            <img :src="getPersonImage(person)"  />
            <div class="person-id-badge" :class="{ 'male-bg': person.gender === 'male', 'female-bg': person.gender === 'female' }">
              {{ person.id }}
            </div>
          </div>
          <div class="card-content">
            <div class="name">{{ person.nickname || `用户${person.id}` }}</div>
            <div class="height-container">
              <div class="height">{{ person.height }}cm</div>
              <!-- 喜欢我的列表不显示红心 -->
            </div>
            <div class="desc">{{ formatDescription(person.mem) }}</div>
            <div class="like-time">{{ formatLikeTime(person.created_at) }}</div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div class="empty-state" v-if="(activeFilter === 'liked' && likedPeople.length === 0) || (activeFilter === 'likedBy' && likedByPeople.length === 0)">
        <div class="empty-icon">
          <van-icon name="like" />
        </div>
        <p class="empty-text" v-if="activeFilter === 'liked'">还没有喜欢的人</p>
        <p class="empty-text" v-else>还没有人喜欢你</p>
        <p class="empty-desc">去寻觅页面看看吧</p>
        <van-button class="explore-btn" @click="goToExplore">去寻觅</van-button>
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
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { showConfirmDialog, showToast  } from 'vant';
import { useAuthStore } from '@/store/authStore';
import { useLikeStore } from '@/store/likeStore';
import { useUserListStore } from '@/store/userList';
import TabBar from '@/components/TabBar.vue';
import { likeUser } from '@/api/like';
// 导入图标
import { ALL_TABS, ICON_MAP, type TabItem, type IconType, type DynamicTabItem } from '@/config/tabs'

// 定义 LikedPerson 接口
interface LikedPerson {
  id: number;
  nickname?: string;
  gender: string;
  height: number;
  mem: string;
  created_at: string; // 点赞时间
  avatar?: string;
  photo?: string;
}

// 定义 Filter 接口
interface Filter {
  id: number;
  label: string;
  value: 'liked' | 'likedBy';
  active: boolean;
}

const router = useRouter();
const likeStore = useLikeStore();
const authStore = useAuthStore();
const userListStore = useUserListStore();
const activeTab = ref('likes');

// 添加筛选状态
const filters = ref<Filter[]>([
  { id: 1, label: '我喜欢的', value: 'liked', active: true },
  { id: 2, label: '喜欢我的', value: 'likedBy', active: false }
]);

const activeFilter = ref<'liked' | 'likedBy'>('liked');

// 获取用户字典（从userListStore中获取所有用户信息）
const userDict = computed(() => {
  const dict: Record<number, any> = {};
  // 使用peopleArray代替people
  userListStore.peopleArray.forEach(user => {
    dict[user.id] = user;
  });
  return dict;
});

// 计算我喜欢的列表
const likedPeople = computed<LikedPerson[]>(() => {
  return likeStore.ilikeIds().map(id => {
    const user = userDict.value[id] || {};
    const createdAt = likeStore.ilikeDict[id];
    
    return {
      id,
      nickname: user.nickname,
      gender: user.gender || 'unknown',
      height: user.height || 0,
      mem: user.mem || '',
      created_at: createdAt || '',
      avatar: user.avatar,
      photo: user.photo
    };
  });
});

// 计算喜欢我的列表
const likedByPeople = computed<LikedPerson[]>(() => {
  return likeStore.likemeIds().map(id => {
    const user = userDict.value[id] || {};
    const createdAt = likeStore.likemeDict[id];
    
    return {
      id,
      nickname: user.nickname,
      gender: user.gender || 'unknown',
      height: user.height || 0,
      mem: user.mem || '',
      created_at: createdAt || '',
      avatar: user.avatar,
      photo: user.photo
    };
  });
});

// 格式化描述（截取8个字）
const formatDescription = (text: string) => {
  if (!text) return '暂无简介';
  return text.length > 8 ? text.substring(0, 8) + '...' : text;
};

// 格式化点赞时间
const formatLikeTime = (dateStr: string) => {
  if (!dateStr) return '';
  
  const now = new Date();
  const date = new Date(dateStr);
  
  // 只比较年月日部分
  const isSameDay = 
    date.getFullYear() === now.getFullYear() &&
    date.getMonth() === now.getMonth() &&
    date.getDate() === now.getDate();
  
  if (isSameDay) return '今天';
  
  // 设置比较日期为前一天
  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  
  const isYesterday = 
    date.getFullYear() === yesterday.getFullYear() &&
    date.getMonth() === yesterday.getMonth() &&
    date.getDate() === yesterday.getDate();
  
  if (isYesterday) return '昨天';
  
  // 计算精确天数差
  const diffTime = Math.abs(now.getTime() - date.getTime());
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  
  return `${diffDays}天前`;
};  

// 获取人员图片URL
const getPersonImage = (person: LikedPerson): string => {
  if (person.photo) {
    const photos = person.photo.split(',');
    if (photos.length > 0 && photos[0].trim() !== '') {
      return '/avatars/' + photos[0].trim();
    }
  }
  return person.avatar ? '/avatars/' + person.avatar : '';
};

const toggleFilter = (filter: Filter) => {
  filters.value.forEach(f => f.active = false);
  filter.active = true;
  activeFilter.value = filter.value;
};

const confirmRemoveLike = (person: LikedPerson) => {
  showConfirmDialog({
    title: '确认取消喜欢',
    message: `确定不再喜欢${person.nickname || '该用户'}吗？`,
    confirmButtonColor: '#D75670',
  })
  .then(() => {
    removeLike(person);
  })
  .catch(() => {
    // 用户点击了取消
  });
};



const removeLike = async(person: LikedPerson) => {
  await likeUser(person.id, 'unlike');
  // 调用likeStore的removeLike方法
  likeStore.removeLike(person.id);
  
  // 显示操作成功提示
  showToast('已取消喜欢');
};

const goToDetail = (id: number) => {
  router.replace(`/detail/${id}`);
};

const goToExplore = () => {
  router.replace('/explore');
};

// 初始化数据
onMounted(async () => {
  // 确保点赞数据已加载
  await likeStore.fetchLikes();
  
  // 确保用户列表数据已加载
  if (userListStore.peopleArray.length === 0) {
    await userListStore.fetchUserList();
  }
});

const tabs = computed(() => [...ALL_TABS, ...authStore.menuItems]);
</script>

<style scoped>
/* 保持所有样式不变 */
.likes-container {
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
  background-color: #F2EEE8;
  min-height: calc(100vh - 92px);
}

.header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 500;
  color: #333;
  margin: 0;
}

.likes-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.person-card {
  background-color: #FFFFFF;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #D9D9D9;
  cursor: pointer;
  transition: transform 0.2s;
}

.person-card:active {
  transform: scale(0.98);
}

.card-image {
  width: 100%;
  height: 200px;
  background-color: #D9D9D9;
  position: relative;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.person-id-badge {
  position: absolute;
  top: 0;
  left: 0;
  background-color: rgba(0, 0, 0, 0.5);
  color: #fff;
  padding: 2px 6px;
  border-radius: 4px 0 2px 0;
  font-size: 10px;
  z-index: 1;
}

.male-bg {
  background-color: #6495ED;
}

.female-bg {
  background-color: #FF69B4;
}

.card-content {
  padding: 12px;
}

.name {
  font-size: 16px;
  color: #333;
  margin-bottom: 8px;
  font-weight: 500;
}

.height-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.height {
  font-size: 14px;
  color: #6A6A6A;
}

.heart-icon {
  font-size: 18px;
  transition: color 0.3s;
}

.heart-icon .liked {
  color: #ff4757;
}

.desc {
  font-size: 12px;
  color: #6A6A6A;
  line-height: 1.4;
  margin-bottom: 8px;
}

.like-time {
  font-size: 11px;
  color: #999;
}

/* 空状态样式 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  color: #D9D9D9;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 18px;
  color: #6A6A6A;
  margin: 0 0 8px 0;
}

.empty-desc {
  font-size: 14px;
  color: #999;
  margin: 0 0 24px 0;
}

.explore-btn {
  background-color: #D75670;
  color: white;
  border: none;
  border-radius: 20px;
  padding: 12px 24px;
  font-size: 14px;
}

.filter-tags {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  margin-bottom: 16px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.filter-tag {
  background-color: #EBE3D7;
  color: #6A6A6A;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.3s;
}

.filter-tag.active {
  background-color: #D75670;
  color: white;
}
</style>