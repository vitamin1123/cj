<template>
  <div class="explore-container" @click="handlePageClick">
    <!-- 页面内容 -->
    <div class="page-content">
      <!-- 搜索框 - 优化后样式 -->
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
              @input="handleSearch"
            />
          </div>
          
          <div class="search-options" v-if="isSearchFocused">
            <div class="search-option-item">
              <div class="option-label">身高</div>
              <div class="option-input">
                <input type="text" placeholder="请输入身高" v-model="heightFilter" @input="handleSearch" />
                <van-icon name="clear" class="clear-icon" @click="heightFilter = ''; handleSearch()" />
              </div>
            </div>
            <div class="search-option-item">
              <div class="option-label">区域</div>
              <div class="option-input">
                <input type="text" placeholder="请输入区域" v-model="regionFilter" @input="handleSearch" />
                <van-icon name="clear" class="clear-icon" @click="regionFilter = ''; handleSearch()" />
              </div>
            </div>
          </div>
        </div>
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
          <div class="card-image">
            <div class="person-id-badge" :class="{ 'male-bg': person.gender === 'male', 'female-bg': person.gender === 'female' }">
              {{ person.id }}
            </div>
          </div>
          <div class="card-content">
            <div class="name" v-html="highlightText(person.nickname && person.nickname.length > 7 ? person.nickname.substring(0, 7) + '...' : person.nickname || `${person.id}`, searchKeyword)"></div>
            <div class="height-container">
              <div class="height">{{ person.birthYear }}年 {{ person.zodiac }}</div>
              <div class="heart-icon" @click.stop="toggleLike(person)">
                <van-icon name="like" :class="{ liked: person.liked }" />
              </div>
            </div>
            <div class="desc" v-html="highlightText(person.occupation || '未知职业', searchKeyword)"></div>
            <div class="region">{{ person.height }}cm</div>
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
import { ref, computed, onMounted } from 'vue';
import TabBar from '@/components/TabBar.vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { Toast,showFailToast,showSuccessToast } from 'vant';
import PinyinMatch from 'pinyin-match';
import apiClient from '@/plugins/axios';
import lunisolar from 'lunisolar';

// 定义 Person 接口
interface Person {
  id: number; // 或者 string，根据后端返回确定
  name: string;
  nickname?: string; // 新增昵称字段
  birthYear?: number; // 新增出生年份
  zodiac?: string; // 新增属相
  height: number;
  gender: 'male' | 'female' | string; // 根据实际情况调整
  region: string;
  occupation?: string;
  education?: string;
  mbti?: string;
  bio?: string;
  liked: boolean;
  isNew: boolean;
  // 其他可能的字段
  [key: string]: any; // 允许其他动态字段，但尽量明确
}

// 定义 Filter 接口
interface Filter {
  id: number;
  label: string;
  active: boolean;
  type: 'location' | 'gender' | 'newbie' | string; // 根据实际情况调整
  value?: string;
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

const activeTab = ref('explore');
const router = useRouter();
const isSearchFocused = ref(false);
const searchKeyword = ref('');
const heightFilter = ref('');
const regionFilter = ref('');

// 两个列表：全部数据和过滤后的数据
const allPeopleList = ref<Person[]>([]);
const filteredPeopleList = ref<Person[]>([]);

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

// 搜索处理函数
const handleSearch = () => {
  let filtered = [...allPeopleList.value];
  
  // 关键字搜索（使用pinyin-match）
  if (searchKeyword.value.trim()) {
    filtered = filtered.filter(person => {
      const searchFields = [
        person.name,
        person.bio || '',
        person.occupation || '',
        person.region || '',
        person.education || '',
        person.mbti || ''
      ].join(' ');
      
      // 确保 PinyinMatch.match 的参数类型正确
      return PinyinMatch.match(searchFields, searchKeyword.value.trim());
    });
  }
  
  // 身高筛选
  if (heightFilter.value.trim()) {
    const height = parseInt(heightFilter.value);
    if (!isNaN(height)) {
      filtered = filtered.filter(person => 
        Math.abs(person.height - height) <= 5 // 允许±5cm的误差
      );
    }
  }
  
  // 区域筛选
  if (regionFilter.value.trim()) {
    filtered = filtered.filter(person => 
    PinyinMatch.match(person.region || '', regionFilter.value.trim())
    );
  }
  
  // 应用其他筛选条件
  const activeGenderFilter = filters.value.find(f => f.type === 'gender' && f.active);
  if (activeGenderFilter) {
    filtered = filtered.filter(person => person.gender === activeGenderFilter.value);
  }
  
  const newbieFilter = filters.value.find(f => f.type === 'newbie');
  if (newbieFilter && newbieFilter.active) {
    filtered = filtered.filter(person => person.isNew);
  }
  
  filteredPeopleList.value = filtered;
};

// 高亮匹配文本
const highlightText = (text: string | undefined, keyword: string): string => {
  if (!text || !keyword.trim()) return text || '';
  
  const matchResult = PinyinMatch.match(text, keyword.trim());
  if (!matchResult) return text;
  
  // 简单的高亮实现
  // 注意: keyword 可能包含正则表达式特殊字符，需要转义，或者使用更安全的高亮库
  // 为简单起见，这里暂时不处理转义
  try {
    const regex = new RegExp(`(${keyword.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return text.replace(regex, '<span class="highlight">$1</span>');
  } catch (e) {
    console.warn('Error creating regex for highlight:', e);
    return text; // Fallback to original text if regex fails
  }
};

// 修改筛选标签 - 支持多选独立模式
const filters = ref<Filter[]>([
  { id: 1, label: '同城', active: false, type: 'location' },
  { id: 2, label: '只看男', active: false, type: 'gender', value: 'male' },
  { id: 3, label: '只看女', active: false, type: 'gender', value: 'female' },
  { id: 4, label: '新人', active: false, type: 'newbie' }
]);

// 性别筛选状态：0-取消选中，1-只看男，2-只看女
const genderFilterState = ref<0 | 1 | 2>(0);

const toggleFilter = (filter: Filter) => {
  if (filter.type === 'gender') {
    // 性别筛选的三状态循环逻辑
    if (filter.value === 'male') {
      if (genderFilterState.value === 1) {
        genderFilterState.value = 0;
        filters.value.forEach(f => {
          if (f.type === 'gender') f.active = false;
        });
      } else {
        genderFilterState.value = 1;
        filters.value.forEach(f => {
          if (f.type === 'gender') {
            f.active = f.value === 'male';
          }
        });
      }
    } else if (filter.value === 'female') {
      if (genderFilterState.value === 2) {
        genderFilterState.value = 0;
        filters.value.forEach(f => {
          if (f.type === 'gender') f.active = false;
        });
      } else {
        genderFilterState.value = 2;
        filters.value.forEach(f => {
          if (f.type === 'gender') {
            f.active = f.value === 'female';
          }
        });
      }
    }
  } else {
    filter.active = !filter.active;
  }
  
  // 重新应用筛选
  handleSearch();
};

// 加载用户数据
const loadUserProfiles = async () => {
  try {
    const response = await apiClient.get('/api/explore_people');
    
    // 直接使用后端返回的数据结构
    allPeopleList.value = response.data.people.map((profile: any) => {
      const birthDate = profile.birth_date ? new Date(profile.birth_date) : null;
      const birthYear = birthDate ? birthDate.getFullYear() : undefined;
      const zodiac = birthDate ? formatLunar(birthDate) : undefined;

      return {
        id: profile.id , // 如果没有ID，生成随机ID
        name: profile.name || "", // 假设后端返回name字段
        nickname: profile.nickname , // 使用name作为nickname，如果为空则显示编号
        birthYear: birthYear,
        zodiac: zodiac,
        height: profile.height || 0,
        gender: profile.gender || 'unknown',
        region: profile.region_code || '未知地区',
        occupation: profile.occupation || '未知职业',
        education: profile.education || '未知学历',
        mbti: profile.mbti || '未知性格',
        bio: profile.mbti ? `${profile.mbti}型人格` : '暂无简介', // 使用MBTI作为简介
        liked: false,
        isNew: false
      };
      // /root/miniconda3/envs/cj/bin/python
    });
    
    // 初始化过滤列表
    filteredPeopleList.value = [...allPeopleList.value];
    
  } catch (error: any) {
    console.error('加载用户数据失败:', error);
    
    // 解析FastAPI的错误响应
    let errorMessage = '加载数据失败';
    if (error.response && error.response.data && error.response.data.detail) {
      if (typeof error.response.data.detail === 'string') {
        errorMessage = error.response.data.detail;
      } else if (Array.isArray(error.response.data.detail)) {
        errorMessage = error.response.data.detail.map((d: any) => d.msg).join('; ');
      }
    }
    
    showFailToast(errorMessage);
  }
};

const formatLunar = (date: Date | null) => {
  if (!date) return '';
  return lunisolar(date).format('cZ'); // 只返回属相
};

const toggleLike = (person: Person) => {
  person.liked = !person.liked;
};

const goToDetail = (id: number | string) => {
  router.replace(`/detail/${id}`);
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

onMounted(() => {
  loadUserProfiles();
});
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

/* ================= 搜索框样式优化 ================= */
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
  /* 优化过渡效果：更慢更柔和 */
  transition: all 0.5s cubic-bezier(0.18, 0.89, 0.32, 1.28);
  position: relative;
  z-index: 10;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
  /* 解决iOS边框问题 */
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
  /* 添加过渡效果 */
  transition: all 0.3s ease;
}

.search-options {
  margin-top: 12px;
  /* 优化动画效果 */
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
  /* 添加过渡效果 */
  transition: all 0.3s ease;
}

.option-label {
  width: 60px;
  font-size: 14px;
  color: #6A6A6A;
  /* 添加过渡效果 */
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
  /* 添加过渡效果 */
  transition: all 0.3s ease;
}

.clear-icon {
  position: absolute;
  right: 8px;
  color: #ccc;
  font-size: 16px;
  /* 添加过渡效果 */
  transition: all 0.3s ease;
}
/* ================= 搜索框样式优化结束 ================= */

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
  background-color: #fff;
  border-radius: 0 12px 12px 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  position: relative;
}

.card-image {
  width: 100%;
  height: 180px; /* 示例高度 */
  background-color: #f0f0f0; /* 占位符颜色 */
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 24px;
  color: #999;
  position: relative; /* 使内部绝对定位的元素相对于它 */
}

.person-id-badge {
  position: absolute;
  top: 0;
  left: 0;
  background-color: rgba(0, 0, 0, 0.5); /* 默认背景 */
  color: #fff;
  padding: 2px 6px; /* 缩小内边距 */
  border-radius: 4px 0 2px 0; /* 仅左上角有弧度 */
  font-size: 10px; /* 缩小字体大小 */
  z-index: 1;
}

.male-bg {
  background-color: #6495ED; /* 男生蓝色 */
}

.female-bg {
  background-color: #FF69B4; /* 女生粉色 */
}

.card-content {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.height-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.height {
  font-size: 14px;
  color: #666;
}

.heart-icon .van-icon {
  font-size: 20px;
  color: #ccc;
  transition: color 0.2s ease;
}

.heart-icon .van-icon.liked {
  color: #ff4d4f; /* 红色 */
}

.desc {
  font-size: 13px;
  color: #888;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.region {
  font-size: 13px;
  color: #888;
}

.highlight {
  color: #FF4D4F;
  font-weight: bold;
}
</style>

