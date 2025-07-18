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
                <input type="number" 
                  placeholder="请输入身高" 
                  v-model="heightFilter" 
                  @input="handleSearch"
                />
                <van-icon name="clear" class="clear-icon" @click="heightFilter = ''; handleSearch()" />
              </div>
            </div>
            <div class="search-option-item">
              <div class="option-label">区域</div>
              <div class="option-input">
                <input 
                  type="text" 
                  placeholder="请选择区域" 
                  readonly 
                  :value="selectedAreaText"
                  @click="showAreaPicker = true"
                />
                <van-icon 
                  name="clear" 
                  class="clear-icon" 
                  @click.stop="clearAreaSelection" 
                />
              </div>
            </div>

            <div class="search-option-item">
              <div class="option-label">生日年份</div>
              <div class="option-input">
                <input 
                  type="text" 
                  placeholder="选择年份范围" 
                  readonly 
                  :value="birthYearDisplay"
                  @click="showBirthYearPicker = true"
                />
                <van-icon 
                  name="clear" 
                  class="clear-icon" 
                  @click.stop="clearBirthYearFilter" 
                />
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
      <div v-if="!isReady" class="skeleton-container">
        <div v-for="i in 6" :key="i" class="person-card skeleton">
          <div class="card-image skeleton-image"></div>
          <div class="card-content">
            <div class="skeleton-text skeleton-title"></div>
            <div class="skeleton-text skeleton-line"></div>
            <div class="skeleton-text skeleton-line short"></div>
          </div>
        </div>
      </div>
      <!-- 人员卡片列表 - 使用虚拟列表 -->
      <div v-else class="people-grid" v-bind="containerProps">
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
                <div class="name" v-html="person.nickname && person.nickname.length > 7 ? person.nickname.substring(0, 7) + '...' : person.nickname || `${person.id}`"></div>
                <div class="heart-icon" @click.stop="toggleLike(person)">
                  <van-icon name="like" :class="{ liked: person.liked }" />
                </div>
              </div>
              <div class="height-container">
                <div class="height">{{ person.birthYear }}年 {{ person.zodiac }}<img :src="getLevelIcon(person.points)" style="width:36px;height:20px;margin-left:2px;vertical-align:-4px;" /></div>
              </div>
              <div class="info-row">
                <div class="desc" v-html="person.occupation || '未知职业'"></div>
                <div class="region">{{ person.height }}cm</div>
              </div>
              <div class="mem" v-html="highlightMem(person.mem, person.id)"></div>
              <!-- <div class="mem">
                {{ person.mem.substring(0, 56)+'...' }}
              </div> -->
            </div>
          </div>
        </div>
      </div>
    </div>
    <van-popup 
      v-model:show="showAreaPicker" 
      position="bottom" 
      round
      teleport="body"
    >
      <van-area
        title="选择区域"
        :area-list="areaList"
        @confirm="confirmAreaSelection"
        @cancel="showAreaPicker = false"
        :columns-placeholder="['', '', '']"
      />
    </van-popup>


    <van-popup 
      v-model:show="showBirthYearPicker" 
      position="bottom" 
      round
      teleport="body"
    >
      <van-picker-group
        title="选择生日年份范围"
        :tabs="['起始年份', '结束年份']"
        @confirm="confirmBirthYearRange"
        @cancel="cancelBirthYearSelection"
      >
        <van-date-picker
          v-model="startYear"
          :columns-type="['year']"
          :min-date="minDate"
          :max-date="maxDate"
          :formatter="yearFormatter"
        />
        <van-date-picker
          v-model="endYear"
          :columns-type="['year']"
          :min-date="minDate"
          :max-date="maxDate"
          :formatter="yearFormatter"
        />
      </van-picker-group>
    </van-popup>
    <!-- 底部TabBar      -->
    <TabBar 
      :active-tab="activeTab" 
      @update:active-tab="activeTab = $event"
      :tabs="tabs"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onActivated, onDeactivated, nextTick, toRefs  } from 'vue';
import TabBar from '@/components/TabBar.vue';
import { useRouter } from 'vue-router';
import { Toast, showFailToast, showSuccessToast } from 'vant';
import PinyinMatch from 'pinyin-match';
import { useViewStateStore } from '@/store/viewState'; 
import { storeToRefs } from 'pinia';
import { useAuthStore } from '@/store/authStore';
import { likeUser } from '@/api/like';
// import apiClient from '@/plugins/axios';
import lunisolar from 'lunisolar';
import { Image as VanImage } from 'vant';
import { areaList } from '@vant/area-data';
import { useVirtualList, useScroll } from '@vueuse/core'; // 引入虚拟列表
import { useUserListStore } from '@/store/userList';
import { useUserInfoStore } from '@/store/userinfo';
import { useLikeStore } from '@/store/likeStore';
import { useExploreStore } from '@/store/exploreStore';
import { debounce } from 'lodash-es';
import { processInBatches } from '@/utils/batch'; 
import { getLevelIcon } from '@/utils/levelIcon';

const exploreStore = useExploreStore();

const {
  searchKeyword,
  heightFilter,
  selectedAreaCode,
  selectedAreaText,
  startYear,
  endYear,
  selectedZodiacs,
  genderFilterState,
  locationFilterActive
} = toRefs(exploreStore.state);


const isReady = ref(false);
const viewStateStore = useViewStateStore();
const { exploreScrollPosition } = storeToRefs(viewStateStore);
const { setExploreScrollPosition } = viewStateStore;
const authStore = useAuthStore();
const userStore = useUserInfoStore();
const likeStore = useLikeStore();
const currentUser = computed(() => userStore.profile);
const showAreaPicker = ref(false);
// 两个列表：全部数据和过滤后的数据
const allPeopleList = ref<Person[]>([]);
const filteredPeopleList = ref<Person[]>([]);
// 虚拟列表相关
// const container = ref<HTMLElement | null>(null);
const { list: virtualList, containerProps, wrapperProps } = useVirtualList(
  filteredPeopleList,
  {
    itemHeight: 260,
    overscan: 2
  }
);
const peopleGridRef = containerProps.ref;
// const scrollPosition = ref(0);

const showBirthYearPicker = ref(false);
const minDate = new Date(1950, 0, 1);
const maxDate = new Date(2025, 11, 31);
// 计算生日年份显示文本
const birthYearDisplay = computed(() => {
  if (startYear.value[0] && endYear.value[0]) {
    return `${startYear.value[0]} - ${endYear.value[0]}`;
  }
  return '选择年份范围';
});

// 修改筛选标签 - 支持多选独立模式
const filters = computed<Filter[]>(() => [
  { 
    id: 1, 
    label: '同城', 
    active: locationFilterActive.value, 
    type: 'location' 
  },
  { 
    id: 2, 
    label: '只看男', 
    active: genderFilterState.value === 1, 
    type: 'gender', 
    value: 'male' 
  },
  { 
    id: 3, 
    label: '只看女', 
    active: genderFilterState.value === 2, 
    type: 'gender', 
    value: 'female' 
  },
]);

const yearFormatter = (type: string, option: any) => {
  if (type === 'year') {
    option.text = option.text + '年';
  }
  return option;
};

// 区域选择确认处理
const confirmAreaSelection = ({ selectedOptions }: { selectedOptions: Array<{ text: string; value: string }> }) => {
  // 过滤掉无效的选项（text为空的）
  const validOptions = selectedOptions.filter(option => 
    option && option.text && option.text.trim() !== '' && option.value !== '000000'
  );
  
  if (validOptions.length > 0) {
    // 生成区域文本
    selectedAreaText.value = validOptions.map(option => option.text).join('-');
    
    // 获取最后一级的有效选项
    const lastValidOption = validOptions[validOptions.length - 1];
    
    // 根据选择的级别确定区域代码位数
    if (validOptions.length === 1) {
      // 只选择了省/直辖市：取前2位代码
      selectedAreaCode.value = lastValidOption.value.substring(0, 2);
    } else if (validOptions.length === 2) {
      // 选择了省和市：取前4位代码
      selectedAreaCode.value = lastValidOption.value.substring(0, 4);
    } else {
      // 选择了完整的省市区：取全部6位代码
      selectedAreaCode.value = lastValidOption.value.substring(0, 6);
    }
  } else {
    // 没有有效选择
    selectedAreaText.value = '';
    selectedAreaCode.value = '';
  }
  
  showAreaPicker.value = false;
  handleSearch();
};

// 清空区域选择
const clearAreaSelection = () => {
  selectedAreaCode.value = '';
  selectedAreaText.value = '';
  exploreStore.saveState();
  handleSearch();
};

// 确认生日年份范围
const confirmBirthYearRange = () => {
  showBirthYearPicker.value = false;
  exploreStore.saveState(); // 添加这行
  handleSearch();
};

// 取消选择
const cancelBirthYearSelection = () => {
  showBirthYearPicker.value = false;
};

// 清空生日年份筛选
const clearBirthYearFilter = () => {
  startYear.value = ['1980'];
  endYear.value = ['2000'];
  handleSearch();
};


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
  memMatch?: [number, number];
  points: number;
  // 其他可能的字段
  [key: string]: any; // 允许其他动态字段，但尽量明确
}


const memMatchMap = ref(new Map<number, [number, number]>());
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
import { ALL_TABS, ICON_MAP, type TabItem, type IconType, type DynamicTabItem } from '@/config/tabs'

const activeTab = ref('explore');
const router = useRouter();
const isSearchFocused = ref(false);

const regionFilter = ref('');
const isZodiacExpanded = ref(false);


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




// 获取人员图片URL
const getPersonImage = (person: Person): string => {
  // 优先使用 photo 第一张
  if (person.photo) {
    const photos = person.photo.split(',');
    const firstPhoto = photos[0]?.trim();
    if (firstPhoto) {
      return `photo/${firstPhoto}`;
    }
  }

  // 其次使用 avatar
  if (person.avatar) {
    return `avatars/${person.avatar}`;
  }

  // 否则根据性别返回默认头像
  const gender = person.gender === 'female' ? 'female' : 'male';
  return `avatars/${gender}_def.png`;
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
// 搜索处理函数
const handleSearch = () => {
  const keyword = searchKeyword.value.trim();
  const heightValue = heightFilter.value;
  const regionValue = regionFilter.value.trim();
  // 获取生日年份范围
  const startYearNum = parseInt(startYear.value[0]);
  const endYearNum = parseInt(endYear.value[0]);
  
  // 清空之前的匹配位置
  memMatchMap.value.clear();
  // 提前计算筛选条件，避免在循环中重复计算
  const hasZodiacFilter = selectedZodiacs.value.length > 0;
  const activeGenderFilter = filters.value.find(f => f.type === 'gender' && f.active);
  const hasLocationFilter = filters.value.find(f => f.type === 'location' && f.active) && currentUser.value?.region_code;
  const currentRegionPrefix = hasLocationFilter ? currentUser.value.region_code.substring(0, 4) : '';
  const areaCode = selectedAreaCode.value;
  console.log('selectedAreaCode-search:',areaCode)
  // 只遍历一次数组
  filteredPeopleList.value = allPeopleList.value.filter(person => {
    
    // 1. 生肖筛选
    if (hasZodiacFilter && !selectedZodiacs.value.includes(person.zodiac || '')) {
      return false;
    }
    
    // 2. 性别筛选
    if (activeGenderFilter && person.gender !== activeGenderFilter.value) {
      return false;
    }
    
    // 3. 同城筛选
    if (hasLocationFilter) {
      if (!person.region || person.region.substring(0, 4) !== currentRegionPrefix) {
        return false;
      }
    }
    
    // 4. 身高筛选
    if (heightValue) {
      const height = parseInt(heightValue);
      if (!isNaN(height) && person.height < height) {
        return false;
      }
    }
    
    // 5. 区域筛选
    if (areaCode) {
      // 检查用户区域代码是否以选择的区域代码为前缀
      if (!person.region || !person.region.startsWith(areaCode)) {
        return false;
      }
    }

    // 0. 生日年份筛选
    if (person.birthYear) {
      const birthYear = person.birthYear;
      if (birthYear < startYearNum || birthYear > endYearNum) {
        return false;
      }
    }
    
    // 6. 关键词搜索（只匹配mem字段）
    if (keyword) {
      const match = PinyinMatch.match(person.mem || '', keyword);
      const occ_match = PinyinMatch.match(person.occupation as string,keyword );
      const id_match = person.id.toString() === keyword
      if (match === false && occ_match === false && id_match === false) {
        return false;
      }
      
      // 存储匹配位置
      if (Array.isArray(match)) {
        memMatchMap.value.set(person.id, match);
      }
      return true;
    }
    exploreStore.saveState();
    // 如果所有条件都满足或者没有关键词搜索，则保留
    return true;
  });
};

const highlightMem = (text: string, id: number): string => {
  if (!text) return '';
  
  // 截断文本
  const truncatedText = text.length > 56 ? text.substring(0, 56) + '...' : text;
  
  // 获取匹配位置
  const match = memMatchMap.value.get(id);
  if (!match) return truncatedText;
  
  const [start, end] = match;
  
  // 确保匹配位置在截断范围内
  const safeEnd = Math.min(end, truncatedText.length - 1);
  if (start > safeEnd || start < 0) return truncatedText;
  
  // 分割文本并添加高亮
  const before = truncatedText.substring(0, start);
  const matched = truncatedText.substring(start, safeEnd + 1);
  const after = truncatedText.substring(safeEnd + 1);
  
  return `${before}<span class="highlight">${matched}</span>${after}`;
};




// 修改后的toggleFilter函数
const toggleFilter = (filter: Filter) => {
  if (filter.type === 'gender') {
    // 处理性别筛选的三状态逻辑
    if (filter.value === 'male') {
      exploreStore.state.genderFilterState = 
        exploreStore.state.genderFilterState === 1 ? 0 : 1;
    } else if (filter.value === 'female') {
      exploreStore.state.genderFilterState = 
        exploreStore.state.genderFilterState === 2 ? 0 : 2;
    }
  } else if (filter.type === 'location') {
    exploreStore.state.locationFilterActive = !exploreStore.state.locationFilterActive;
  }
  
  exploreStore.saveState();
  handleSearch();
};
const toggleFilter_bak = (filter: Filter) => {
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
  exploreStore.saveState();
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
    // 确保用户数据已加载
    if (userListStore.sortedIds.length === 0) {
      await userListStore.initializeStore();
    }
    
    // 使用有序的用户数据
    allPeopleList.value = userListStore.peopleArray.map(profile => {
      const birthYear = profile.birth_date 
        ? new Date(profile.birth_date).getFullYear() 
        : 0;
      
      let zodiac = '未知';
      try {
        if (profile.birth_date) {
          const zodiacRaw = lunisolar(new Date(profile.birth_date)).format('cZ');
          zodiac = zodiacMapping[zodiacRaw as Zodiac] || '未知';
        }
      } catch (error) {
        console.error('计算生肖失败:', error);
      }

      return {
        id: profile.id,
        nickname: profile.nickname,
        birthYear,
        zodiac,
        mem: profile.mem,
        height: profile.height,
        gender: profile.gender,
        region: profile.region_code,
        occupation: profile.occupation,
        education: profile.education,
        avatar: profile.avatar,
        photo: profile.photo,
        liked: likeStore.hasLiked(profile.id),
        isNew: false,
        points: profile.points,
      };
    });

    filteredPeopleList.value = [...allPeopleList.value];
    return true;
  } catch (error) {
    console.error('加载用户数据失败:', error);
    showFailToast('加载数据失败');
    return false;
  }
};



const toggleLike = async (person: Person) => {
  try {
    const action = person.liked ? 'unlike' : 'like';
    await likeUser(person.id, action);
    
    // 本地更新状态（避免重新请求）
    person.liked = !person.liked;
    if (person.liked) {
      likeStore.addLike(person.id);
    } else {
      likeStore.removeLike(person.id);
    }
    showSuccessToast(person.liked ? '已喜欢' : '已取消');
  } catch (error) {
    console.error('操作失败:', error);
    showFailToast('操作失败');
  }
};

const goToDetail = (id: number | string) => {
  router.replace(`/detail/${id}`);
};

const tabs = computed(() => [...ALL_TABS, ...authStore.menuItems]);
const { y: liveScrollPosition } = useScroll(peopleGridRef, { throttle: 100 });
onActivated(async () => {
  console.log('ExploreView activated. Restoring scroll position from Pinia:', exploreScrollPosition.value);
  
  await nextTick();
  
  if (peopleGridRef.value) {
    // 6. 从 Pinia state 恢复滚动位置
    peopleGridRef.value.scrollTop = exploreScrollPosition.value;
  }
});

onDeactivated(() => {
  // 7. 在组件失活时，调用 action 将当前位置存入 Pinia
  setExploreScrollPosition(liveScrollPosition.value);
  console.log(`ExploreView deactivated. Saved scroll position to Pinia: ${liveScrollPosition.value}`);
});

onMounted(async() => {
   const loaded = await loadUserProfiles();
   if (loaded) {
    if (exploreStore.state.genderFilterState === 0) {
      // 如果持久化状态是0，确保所有筛选标签都不激活
      filters.value.forEach(f => f.active = false);
    }
    handleSearch();
  }
  await nextTick();
  setTimeout(() => {
    isReady.value = true;
  }, 100);
  
  console.log('currentUser:', currentUser.value?.region_code.substring(0, 4),);
  console.log('onMounted triggered. peopleGridRef.value:', peopleGridRef.value);
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
  height: 185px;
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
  color: #666 !important;
}


.highlight {
  color: #FF4D4F;
  font-weight: bold;
}

:global(.highlight) {
  color: #FF4D4F !important;
  font-weight: bold !important;
  background-color: transparent !important;
}
</style>
