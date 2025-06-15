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
      <div class="likes-list" v-if="activeFilter === 'liked'">
        <!-- 我喜欢的列表 -->
        <div v-for="person in likedPeople" :key="person.id" class="person-card">
          <div class="card-image"></div>
          <div class="card-content">
            <div class="name">{{ person.name }}</div>
            <div class="height-container">
              <div class="height">{{ person.height }}cm</div>
              <div class="heart-icon" @click.stop="removeLike(person)">
                <van-icon name="like" class="liked" />
              </div>
            </div>
            <div class="desc">{{ person.desc }}</div>
            <div class="like-time">{{ person.likeTime }}</div>
          </div>
        </div>
      </div>

      <div class="likes-list" v-if="activeFilter === 'likedBy'">
        <!-- 喜欢我的列表 -->
        <div v-for="person in likedByPeople" :key="person.id" class="person-card">
          <div class="card-image"></div>
          <div class="card-content">
            <div class="name">{{ person.name }}</div>
            <div class="height-container">
              <div class="height">{{ person.height }}cm</div>
              <div class="heart-icon" @click.stop="removeLike(person)">
                <van-icon name="like" class="liked" />
              </div>
            </div>
            <div class="desc">{{ person.desc }}</div>
            <div class="like-time">{{ person.likeTime }}</div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div class="empty-state" v-else>
        <div class="empty-icon">
          <van-icon name="like" />
        </div>
        <p class="empty-text">还没有喜欢的人</p>
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
import { ref } from 'vue';
import TabBar from '@/components/TabBar.vue';
import { useRouter } from 'vue-router';

// 定义 LikedPerson 接口
interface LikedPerson {
  id: number;
  name: string;
  height: number;
  desc: string;
  likeTime: string;
  // 可以添加更多字段，如头像等
}

// 定义 Filter 接口
interface Filter {
  id: number;
  label: string;
  value: 'liked' | 'likedBy';
  active: boolean;
}

// 导入图标
import homeIcon from '@/assets/icons/home.svg';
import homeSelectedIcon from '@/assets/icons/home-selected.svg';
import compassIcon from '@/assets/icons/compass.svg';
import compassSelectedIcon from '@/assets/icons/compass-selected.svg';
import likeIcon from '@/assets/icons/like.svg';
import likeSelectedIcon from '@/assets/icons/like-selected.svg';
import smileIcon from '@/assets/icons/smile.svg';
import smileSelectedIcon from '@/assets/icons/smile-selected.svg';

const activeTab = ref('likes');
const router = useRouter();

// 添加筛选状态
const filters = ref<Filter[]>([
  { id: 1, label: '我喜欢的', value: 'liked', active: true },
  { id: 2, label: '喜欢我的', value: 'likedBy', active: false }
]);

const activeFilter = ref<'liked' | 'likedBy'>('liked');

const toggleFilter = (filter: Filter) => {
  filters.value.forEach(f => f.active = false);
  filter.active = true;
  activeFilter.value = filter.value;
};

// 我喜欢的列表数据
const likedPeople = ref<LikedPerson[]>([
  { 
    id: 2, 
    name: '小雅', 
    height: 168, 
    desc: '热爱音乐和舞蹈', 
    likeTime: '2天前'
  },
  { 
    id: 5, 
    name: '小娜', 
    height: 166, 
    desc: '读书爱好者', 
    likeTime: '1周前'
  }
]);

// 添加喜欢我的列表数据
const likedByPeople = ref<LikedPerson[]>([
  { id: 7, name: '小明', height: 178, desc: '喜欢运动', likeTime: '1天前' },
  { id: 8, name: '小强', height: 175, desc: '程序员', likeTime: '3天前' }
]);

const removeLike = (person: LikedPerson) => {
  // 根据 activeFilter 决定从哪个列表移除
  if (activeFilter.value === 'liked') {
    const index = likedPeople.value.findIndex(p => p.id === person.id);
    if (index > -1) {
      likedPeople.value.splice(index, 1);
    }
  } else if (activeFilter.value === 'likedBy') {
    const index = likedByPeople.value.findIndex(p => p.id === person.id);
    if (index > -1) {
      likedByPeople.value.splice(index, 1);
    }
  }
};

const goToDetail = (id: number) => {
  router.push(`/detail/${id}`);
};

const goToExplore = () => {
  router.push('/explore');
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
    iconSelected: likeSelectedIcon
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