import { defineStore } from 'pinia';
import { ref, reactive } from 'vue';

// 定义Filter类型
interface FilterState {
  id: number;
  active: boolean;
}

const currentYear = new Date().getFullYear();
const defaultEndYear = currentYear - 0;

export const useExploreStore = defineStore('explore', () => {
  // 持久化状态
  const state = reactive({
    searchKeyword: '',
    heightFilter: '',
    selectedAreaCode: '',
    selectedAreaText: '',
    startYear: ['1950'],
    endYear: [defaultEndYear.toString()],
    activeFilters: {} as Record<number, boolean>, // 存储filter的激活状态
    selectedZodiacs: [] as string[],
    // 新增：存储filters的激活状态
    genderFilterState: 0 as 0 | 1 | 2, // 0-取消选中，1-只看男，2-只看女
    locationFilterActive: false,
    marriedFilter: '',
    childFilter :''
  });

  // 非持久化状态
  const filteredPeopleList = ref<any[]>([]);

  // 初始化从localStorage加载
  const loadState = () => {
    const saved = localStorage.getItem('exploreFilters');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        Object.assign(state, parsed);
      } catch (e) {
        console.error('加载筛选状态失败', e);
      }
    }
  };

  // 保存到localStorage
  const saveState = () => {
    localStorage.setItem('exploreFilters', JSON.stringify(state));
  };

  // 初始化加载
  loadState();

  return {
    state,
    filteredPeopleList,
    loadState,
    saveState,
  };
});