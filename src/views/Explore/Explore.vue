<template>
  <div class="explore-container">
    <!-- 页面内容 -->
    <div class="page-content">
      <!-- 搜索框 -->
      <div class="search-container">
        <div class="search-card" :class="{ focused: isSearchFocused }">
          <div class="search-box">
            <t-icon name="search" class="search-icon" />
            <input 
              type="text" 
              placeholder="搜索" 
              class="search-input" 
              @focus="handleSearchFocus"
            />
          </div>
          
          <div class="search-options" v-if="isSearchFocused">
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
          </div>
        </div>
        <!-- 遮罩层 -->
        <div class="search-mask" v-if="isSearchFocused" @click="closeSearch"></div>
      </div>

      <!-- 筛选标签 -->
      <div class="filter-section">
        <div class="filter-tags">
          <span v-for="filter in filters" :key="filter.id" 
                class="filter-tag" 
                :class="{ active: filter.active }"
                @click="toggleFilter(filter)">
            {{ filter.label }}
          </span>
        </div>
      </div>

      <!-- 人员卡片列表 -->
      <div class="people-grid">
        <div v-for="person in filteredPeopleList" :key="person.id" 
             class="person-card" 
             @click="goToDetail(person.id)">
          <div class="card-image"></div>
          <div class="card-content">
            <div class="name">{{ person.name }}</div>
            <div class="height-container">
              <div class="height">{{ person.height }}cm</div>
              <div class="heart-icon" @click.stop="toggleLike(person)">
                <van-icon name="like" :class="{ liked: person.liked }" />
              </div>
            </div>
            <div class="desc">{{ person.desc }}</div>
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
import { ref, computed } from 'vue';
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

const activeTab = ref('explore');
const router = useRouter();
const isSearchFocused = ref(false);

const handleSearchFocus = () => {
  isSearchFocused.value = true;
};

const closeSearch = () => {
  isSearchFocused.value = false;
};

// 修改筛选标签 - 支持多选独立模式
const filters = ref([
  { id: 1, label: '同城', active: false, type: 'location' },
  { id: 2, label: '只看男', active: false, type: 'gender', value: 'male' },
  { id: 3, label: '只看女', active: false, type: 'gender', value: 'female' },
  { id: 4, label: '新人', active: false, type: 'newbie' }
]);

// 性别筛选状态：0-取消选中，1-只看男，2-只看女
const genderFilterState = ref(0);

const toggleFilter = (filter: any) => {
  if (filter.type === 'gender') {
    // 性别筛选的三状态循环逻辑
    if (filter.value === 'male') {
      if (genderFilterState.value === 1) {
        // 当前是只看男，点击后取消选中
        genderFilterState.value = 0;
        filters.value.forEach(f => {
          if (f.type === 'gender') f.active = false;
        });
      } else {
        // 设置为只看男
        genderFilterState.value = 1;
        filters.value.forEach(f => {
          if (f.type === 'gender') {
            f.active = f.value === 'male';
          }
        });
      }
    } else if (filter.value === 'female') {
      if (genderFilterState.value === 2) {
        // 当前是只看女，点击后取消选中
        genderFilterState.value = 0;
        filters.value.forEach(f => {
          if (f.type === 'gender') f.active = false;
        });
      } else {
        // 设置为只看女
        genderFilterState.value = 2;
        filters.value.forEach(f => {
          if (f.type === 'gender') {
            f.active = f.value === 'female';
          }
        });
      }
    }
  } else {
    // 其他筛选项独立切换
    filter.active = !filter.active;
  }
};

// 人员列表数据 - 添加性别字段
const peopleList = ref([
  { id: 1, name: '小美', height: 165, desc: '喜欢旅行和摄影', liked: false, gender: 'female', isNew: false },
  { id: 2, name: '小雅', height: 168, desc: '热爱音乐和舞蹈', liked: true, gender: 'female', isNew: true },
  { id: 3, name: '小琳', height: 162, desc: '美食爱好者', liked: false, gender: 'female', isNew: false },
  { id: 4, name: '小明', height: 178, desc: '健身达人', liked: false, gender: 'male', isNew: false },
  { id: 5, name: '小强', height: 175, desc: '读书爱好者', liked: true, gender: 'male', isNew: true },
  { id: 6, name: '小刚', height: 180, desc: '艺术工作者', liked: false, gender: 'male', isNew: false }
]);

// 根据筛选条件过滤人员列表
const filteredPeopleList = computed(() => {
  let filtered = [...peopleList.value];
  
  // 性别筛选
  const activeGenderFilter = filters.value.find(f => f.type === 'gender' && f.active);
  if (activeGenderFilter) {
    filtered = filtered.filter(person => person.gender === activeGenderFilter.value);
  }
  
  // 新人筛选
  const newbieFilter = filters.value.find(f => f.type === 'newbie');
  if (newbieFilter && newbieFilter.active) {
    filtered = filtered.filter(person => person.isNew);
  }
  
  // 同城筛选（这里可以添加具体逻辑）
  const locationFilter = filters.value.find(f => f.type === 'location');
  if (locationFilter && locationFilter.active) {
    // 这里可以添加同城筛选逻辑
  }
  
  return filtered;
});

const toggleLike = (person: any) => {
  person.liked = !person.liked;
};

const goToDetail = (id: number) => {
  router.push(`/detail/${id}`);
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
    iconSelected: compassSelectedIcon
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
.explore-container {
  background-color: #F2EEE8;
  min-height: 100vh;
  padding: 16px;
  font-family: "Microsoft YaHei", sans-serif;
  display: flex;
  flex-direction: column;
  position: relative;
}

.page-content {
  flex: 1;
  margin-bottom: 60px;
  background-color: #F2EEE8;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  min-height: calc(100vh - 92px);
}

/* 搜索框样式 - 复用Home页面样式 */
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
  transition: all 0.3s ease;
  position: relative;
  z-index: 10;
}

.search-card.focused {
  border-radius: 12px;
  padding-bottom: 16px;
  position: absolute;
  width: calc(100% - 32px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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
}

.search-options {
  margin-top: 12px;
  animation: fadeIn 0.3s ease;
}

.search-option-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.option-label {
  width: 60px;
  font-size: 14px;
  color: #6A6A6A;
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
}

.clear-icon {
  position: absolute;
  right: 8px;
  color: #ccc;
  font-size: 16px;
}

.search-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 5;
}

/* 筛选标签 */
.filter-section {
  margin-bottom: 16px;
}

.filter-tags {
  display: flex;
  gap: 8px;
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

/* 人员卡片网格 */
.people-grid {
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
  color: #ccc;
  transition: color 0.3s;
}

.heart-icon .liked {
  color: #ff4757;
}

.desc {
  font-size: 12px;
  color: #6A6A6A;
  line-height: 1.4;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>