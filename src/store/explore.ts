// src/store/explore.ts
import { defineStore } from 'pinia';
interface Filter {
  id: number;
  label: string;
  active: boolean;
  type: string;
  value?: string;
}

export const useExploreStore = defineStore('explore', {
  state: () => ({
    searchKeyword: '',
    heightFilter: '',
    selectedAreaCode: '',
    selectedAreaText: '',
    startYear: '1980',
    endYear: '2020',
    selectedZodiacs: [] as string[],
    filters: [
      { id: 1, label: '同城', active: false, type: 'location' },
      { id: 2, label: '只看男', active: false, type: 'gender', value: 'male' },
      { id: 3, label: '只看女', active: false, type: 'gender', value: 'female' }
    ] as Filter[],
    isSearchFocused: false,
    showAreaPicker: false,
    showBirthYearPicker: false,
    isZodiacExpanded: false,
    // 存储滚动位置
    scrollPosition: 0
  }),
  persist: true // 启用持久化存储，刷新页面也能保留状态
});