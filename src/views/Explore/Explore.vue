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
              type="search" 
              placeholder="搜索" 
              class="search-input" 
              v-model="searchKeyword"
              @focus="handleSearchFocus"
              @keyup.enter="handleSearch"
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
          <!-- 生肖筛选标签 -->
          <span class="filter-tag" 
                :class="{ active: isZodiacExpanded || selectedZodiacs.length > 0 }"
                @click.stop="toggleZodiacDropdown">
            生肖{{ selectedZodiacs.length > 0 ? '('+selectedZodiacs.length+')' : '' }}
            <van-icon name="arrow-down" class="dropdown-icon" :class="{ rotated: isZodiacExpanded }" />
          </span>
        </div>
        
        <!-- 生肖下拉菜单 -->
        <div class="zodiac-dropdown" v-if="isZodiacExpanded" @click.stop>
          <div class="zodiac-grid">
            <span v-for="zodiac in zodiacOptions" 
                  :key="zodiac.value"
                  class="zodiac-item"
                  :class="{ selected: selectedZodiacs.includes(zodiac.value) }"
                  @click="toggleZodiacSelection(zodiac.value)">
              {{ zodiac.label }}
            </span>
          </div>
          <div class="zodiac-actions">
            <van-button size="small" @click="clearZodiacSelection">清空</van-button>
            <van-button size="small" type="primary" @click="applyZodiacFilter">确定</van-button>
          </div>
        </div>
      </div>

      <!-- 人员卡片列表 - 使用虚拟列表 -->
      <div class="people-grid"  v-bind="containerProps">
        <div v-bind="wrapperProps">
          <div v-for="{ index, data: person } in virtualList" :key="index" 
               class="person-card" 
               @click="goToDetail(person.id)">
            <div class="card-image">
              <van-image
                width="100%"
                height="100%"
                :src="getPersonImage(person)"
                lazy-load
                fit="cover"
              >
                <template v-slot:loading>
                  <div class="image-placeholder">
                    <van-icon name="photo" size="24" />
                  </div>
                </template>
                <template v-slot:error>
                  <div class="image-placeholder">
                    <van-icon name="photo-fail" size="24" />
                  </div>
                </template>
              </van-image>
              <div class="person-id-badge" :class="{ 'male-bg': person.gender === 'male', 'female-bg': person.gender === 'female' }">
                {{ person.id }}
              </div>
            </div>
            <div class="card-content">
              <div class="name-container">
                <div class="name" v-html="highlightText(person.nickname && person.nickname.length > 7 ? person.nickname.substring(0, 7) + '...' : person.nickname || `${person.id}`, searchKeyword)"></div>
                <div class="heart-icon" @click.stop="toggleLike(person)">
                  <van-icon name="like" :class="{ liked: person.liked }" />
                </div>
              </div>
              <div class="height-container">
                <div class="height">{{ person.birthYear }}年 {{ person.zodiac }}</div>
              </div>
              <div class="info-row">
                <div class="desc" v-html="highlightText(person.occupation || '未知职业', searchKeyword)"></div>
                <div class="region">{{ person.height }}cm</div>
              </div>
              <div class="mem">
                {{ person.mem.substring(0, 56)+'...' }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部TabBar      -->
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
import { Toast, showFailToast, showSuccessToast } from 'vant';
import PinyinMatch from 'pinyin-match';


// 移除不再需要的引入
// import apiClient from '@/plugins/axios';
import lunisolar from 'lunisolar';
import { Image as VanImage } from 'vant';
import { useVirtualList } from '@vueuse/core'; // 引入虚拟列表
import { useUserListStore } from '@/store/userList';
import { useUserInfoStore } from '@/store/userinfo';


const userStore = useUserInfoStore();
const currentUser = computed(() => userStore.profile);

lunisolar.config({
  locale: 'cn' // 指定简体中文
});
// 定义 Person 接口
interface Person {
  id: number; // 或者 string，根据后端返回确定
  name?: string;
  nickname?: string; // 新增昵称字段
  birthYear?: number; // 新增出生年份
  zodiac?: string; // 新增属相
  height: number;
  gender: 'male' | 'female' | string; // 根据实际情况调整
  region: string;
  occupation?: string;
  education?: string;
  mbti?: string;
  mem: string;
  bio?: string;
  liked: boolean;
  isNew: boolean;
  avatar?: string;
  photo?: string;
  // 其他可能的字段
  [key: string]: any; // 允许其他动态字段，但尽量明确
}

// 定义 Filter 接口
// 移除冗余的Person接口定义
// interface Person {
//   id: number;
//   name: string;
//   nickname?: string;
//   ...
// }

// 保留必要的类型定义
interface Filter {
  id: number;
  label: string;
  active: boolean;
  type: 'location' | 'gender' | 'zodiac' | string;
  value?: string;
}

interface ZodiacOption {
  label: string;
  value: string;
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
const isZodiacExpanded = ref(false);
const selectedZodiacs = ref<string[]>([]);

// 生肖选项
const zodiacOptions: ZodiacOption[] = [
  { label: '鼠', value: '鼠' },
  { label: '牛', value: '牛' },
  { label: '虎', value: '虎' },
  { label: '兔', value: '兔' },
  { label: '龙', value: '龙' },
  { label: '蛇', value: '蛇' },
  { label: '马', value: '马' },
  { label: '羊', value: '羊' },
  { label: '猴', value: '猴' },
  { label: '鸡', value: '鸡' },
  { label: '狗', value: '狗' },
  { label: '猪', value: '猪' }
];

// 两个列表：全部数据和过滤后的数据
const allPeopleList = ref<Person[]>([]);
const filteredPeopleList = ref<Person[]>([]);
// 虚拟列表相关
const container = ref<HTMLElement | null>(null);
const { list: virtualList, containerProps, wrapperProps } = useVirtualList(
  filteredPeopleList,
  {
    itemHeight: 260, // 每项高度（卡片高度 + 间距）
    overscan: 5, // 预渲染的额外项数
  }
);

// 获取人员图片URL
const getPersonImage = (person: Person): string => {
  
  if (person.photo) {
    const photos = person.photo.split(',');
    if (photos.length > 0 && photos[0].trim() !== '') {
      return 'avatars/'+photos[0].trim();
    }
  }
  return 'avatars/'+person.avatar || '';
};

const handleSearchFocus = () => {
  isSearchFocused.value = true;
};

const closeSearch = () => {
  isSearchFocused.value = false;
};

// 点击页面其他区域关闭搜索框
const handlePageClick = () => {
  if (isZodiacExpanded.value) {
    isZodiacExpanded.value = false;
  }
  if (isSearchFocused.value) {
    closeSearch();
  }
};

// 搜索处理函数
const handleSearch = () => {
  // 从完整列表开始筛选
  let filtered = [...allPeopleList.value];
  
  // 1. 生肖筛选（优先级最高）
  if (selectedZodiacs.value.length > 0) {
    filtered = filtered.filter(person => 
      selectedZodiacs.value.includes(person.zodiac || '')
    );
  }

  // 2. 性别筛选
  const activeGenderFilter = filters.value.find(f => f.type === 'gender' && f.active);
  if (activeGenderFilter) {
    filtered = filtered.filter(person => person.gender === activeGenderFilter.value);
  }

  // 3. 同城筛选（基于当前用户位置）
  if (filters.value.find(f => f.type === 'location' && f.active) && currentUser.value?.region_code) {
    const currentRegionPrefix = currentUser.value.region_code.substring(0, 4);
    filtered = filtered.filter(person => 
      person.region && person.region.substring(0, 4) === currentRegionPrefix
    );
  }

  // 4. 身高筛选
  if (heightFilter.value.trim()) {
    const height = parseInt(heightFilter.value);
    if (!isNaN(height)) {
      filtered = filtered.filter(person => 
        Math.abs(person.height - height) <= 5 // 允许±5cm误差
      );
    }
  }

  // 5. 区域筛选（基于输入值）
  if (regionFilter.value.trim()) {
    filtered = filtered.filter(person => {
      const currentRegionCode = person.regionCode || '';
      const filterRegionCode = regionFilter.value.trim();
      return currentRegionCode.substring(0, 4) === filterRegionCode.substring(0, 4);
    });
  }

  // 6. 关键词搜索（最后执行，只匹配mem字段）
  const keyword = searchKeyword.value.trim();
  if (keyword) {
    filtered = filtered.filter(person => {
      // 仅匹配mem字段
      return PinyinMatch.match(person.mem || '', keyword) !== false;
    });
  }
  
  // 更新最终结果
  filteredPeopleList.value = filtered;
};

const handleSearch_bak = () => {
  let filtered = [...allPeopleList.value];
  
  // 关键字搜索（使用pinyin-match）
  console.log('searchKeyword',searchKeyword.value,PinyinMatch.match('张三', 'zs'))
  const keyword = searchKeyword.value.trim();
  if (!keyword) {
    filteredPeopleList.value = [...allPeopleList.value];
    return;
  }

  filteredPeopleList.value = allPeopleList.value.filter(person => {
    // 确保每个字段都是字符串，然后放入数组
    const searchFields = [
      String(person.occupation || ''),
      String(person.mem || '')
    ];
    console.log('搜索字段内容:', searchFields);
    // 检查每个字段是否匹配
    return searchFields.some(text => {
      return PinyinMatch.match(text, keyword) !== false;
    });
  });
  
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
              filtered = filtered.filter(person => {
                // 同城判断：比较地区code前4位
                const currentRegionCode = person.regionCode || '';
                const filterRegionCode = regionFilter.value.trim();
                return currentRegionCode.substring(0, 4) === filterRegionCode.substring(0, 4);
              });
            }
  // 同城筛选
  if (filters.value.find(f => f.type === 'location' && f.active) && currentUser.value?.region_code) {
    const currentRegionPrefix = currentUser.value.region_code.substring(0, 4);
    filtered = filtered.filter(person => 
      person.region && person.region.substring(0, 4) === currentRegionPrefix
    );
  }
  
  // 生肖筛选
  if (selectedZodiacs.value.length > 0) {
    filtered = filtered.filter(person => 
      selectedZodiacs.value.includes(person.zodiac || '')
    );
  }
  
  // 应用其他筛选条件
  const activeGenderFilter = filters.value.find(f => f.type === 'gender' && f.active);
  if (activeGenderFilter) {
    filtered = filtered.filter(person => person.gender === activeGenderFilter.value);
  }
  
  
  
  filteredPeopleList.value = filtered;
};

// 高亮匹配文本
const highlightText = (text: string = '', keyword: string = ''): string => {
  if (!text || !keyword.trim()) return text;
  
  // 简单高效的匹配和高亮实现
  const keywordLower = keyword.trim().toLowerCase();
  const textLower = text.toLowerCase();
  
  // 直接文本匹配
  const index = textLower.indexOf(keywordLower);
  if (index === -1) return text;
  
  // 高亮匹配部分
  const matchedText = text.substring(index, index + keyword.length);
  return (
    text.substring(0, index) +
    `<span class="highlight">${matchedText}</span>` +
    text.substring(index + keyword.length)
  );
};
const highlightText_bak = (text: string | undefined, keyword: string): string => {
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
  // { id: 4, label: '新人', active: false, type: 'newbie' }
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

// 切换生肖下拉菜单
const toggleZodiacDropdown = () => {
  isZodiacExpanded.value = !isZodiacExpanded.value;
};

// 切换生肖选择
const toggleZodiacSelection = (zodiac: string) => {
  const index = selectedZodiacs.value.indexOf(zodiac);
  if (index === -1) {
    selectedZodiacs.value.push(zodiac);
  } else {
    selectedZodiacs.value.splice(index, 1);
  }
};

// 清空生肖选择
const clearZodiacSelection = () => {
  selectedZodiacs.value = [];
};

// 应用生肖筛选
const applyZodiacFilter = () => {
  isZodiacExpanded.value = false;
  handleSearch();
};

type Zodiac = '鼠' | '牛' | '虎' | '兔' | '龍' | '蛇' | '馬' | '羊' | '猴' | '雞' | '狗' | '豬';
const zodiacMapping: Record<Zodiac, string> = {
  '鼠': '鼠', 
  '牛': '牛',
  '虎': '虎',
  '兔': '兔',
  '龍': '龙',
  '蛇': '蛇',
  '馬': '马',
  '羊': '羊',
  '猴': '猴',
  '雞': '鸡',
  '狗': '狗',
  '豬': '猪'
};
const formatLunar = (date: Date | null): Zodiac => {
  if (!date) return '鼠';
  const zodiac = lunisolar(date).format('cZ');
  
  // 运行时验证
  if (Object.keys(zodiacMapping).includes(zodiac)) {
    return zodiac as Zodiac;
  }
  
  // 处理意外情况
  console.error(`Invalid zodiac: ${zodiac}`);
  return '鼠';
};
// 加载用户数据
const loadUserProfiles = async () => {
  const userListStore = useUserListStore();
  try {
    // await userListStore.fetchUserList();
    
    allPeopleList.value = userListStore.formattedPeople.map(profile => ({
      id: profile.id,
      nickname: profile.nickname,
      birthYear: new Date(profile.birth_date).getFullYear(),
      zodiac: zodiacMapping[formatLunar(new Date(profile.birth_date))],
      mem: profile.mem,
      height: profile.height,
      gender: profile.gender,
      region: profile.region_code,
      occupation: profile.occupation,
      education: profile.education,
      avatar: profile.avatar,
      photo: profile.photo,
      liked: false,
      isNew: false
    }));
    
    filteredPeopleList.value = [...allPeopleList.value];
    
  } catch (error) {
    console.error('加载用户数据失败:', error);
    showFailToast('加载数据失败');
  }
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
  console.log('currentUser:', currentUser.value?.region_code.substring(0, 4))
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
  position: relative;
}

.filter-tags {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
  /* 添加滚动条样式 */
  scrollbar-width: thin;
  scrollbar-color: #D75670 #EBE3D7;
}

/* 自定义滚动条样式 */
.filter-tags::-webkit-scrollbar {
  height: 4px;
}

.filter-tags::-webkit-scrollbar-track {
  background: #EBE3D7;
  border-radius: 2px;
}

.filter-tags::-webkit-scrollbar-thumb {
  background-color: #D75670;
  border-radius: 2px;
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
  flex-shrink: 0; /* 防止标签被压缩 */
  display: flex;
  align-items: center;
  gap: 4px;
  position: relative;
}

.filter-tag.active {
  background-color: #D75670;
  color: white;
}

.dropdown-icon {
  transition: transform 0.3s ease;
  font-size: 12px;
}

.dropdown-icon.rotated {
  transform: rotate(180deg);
}

.selected-count {
  position: absolute;
  top: -6px;
  right: -6px;
  background-color: #D75670;
  color: white;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 生肖下拉菜单 */
.zodiac-dropdown {
  background-color: white;
  border-radius: 8px;
  padding: 12px;
  margin-top: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  animation: slideDown 0.3s ease-out;
  z-index: 20;
}

.zodiac-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}

.zodiac-item {
  padding: 8px;
  text-align: center;
  border-radius: 16px;
  background-color: #EBE3D7;
  cursor: pointer;
  transition: all 0.2s;
}

.zodiac-item.selected {
  background-color: #D75670;
  color: white;
}

.zodiac-actions {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

/* 人员卡片网格 */
.people-grid {
  height: calc(100vh - 100px); /* 根据实际布局调整高度 */
  overflow: auto; /* 启用滚动 */
  position: relative; /* 虚拟列表需要相对定位 */
}

.person-card {
  background-color: #fff;
  border-radius: 4px 12px 12px 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  position: relative;
  margin-bottom: 16px; /* 增加卡片间距 */
}

.card-image {
  height: 180px;
  width: 120px; /* 固定图片宽度 */
  position: relative;
  flex-shrink: 0; /* 防止图片被压缩 */
  overflow: hidden; /* 添加这行防止图片溢出 */
}

.van-image {
  display: block;
  height: 100%;
  width: 100%;
}

/* 修复van-image可能的内置样式 */
:deep(.van-image__img) {
  height: 100% !important;
  width: 100% !important;
  object-fit: cover;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  background-color: #f0f0f0;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #999;
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
  flex: 1; /* 填充剩余空间 */
  position: relative;
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

.name-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  flex: 1; /* 占据剩余空间 */
  margin-right: 8px; /* 添加右边距 */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.heart-icon {
  flex-shrink: 0; /* 防止被压缩 */
}

.heart-icon .van-icon {
  font-size: 20px;
  color: #ccc;
  transition: color 0.2s ease;
}

.heart-icon .van-icon.liked {
  color: #ff4d4f; /* 红色 */
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  white-space: nowrap;
  overflow: hidden;
}

.desc {
  font-size: 13px;
  color: #888;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1; /* 占据剩余空间 */
  margin-right: 8px; /* 添加右边距 */
}

.region {
  font-size: 13px;
  color: #888;
  flex-shrink: 0; /* 防止压缩 */
}

/* 新增的mem样式 */
.mem {
  font-size: 14px;
  color: #666;
  margin-top: 4px; /* 与上一行拉开距离 */
}


.highlight {
  color: #FF4D4F;
  font-weight: bold;
}
</style>