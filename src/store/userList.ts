import { defineStore } from 'pinia';
import { ref, computed, watchEffect } from 'vue';
import apiClient from '@/plugins/axios';

interface User {
  avatar: string;
  birth_date: string;
  education: string;
  gender: string;
  height: number;
  id: number;
  income_level: string;
  mem: string;
  nickname: string;
  occupation: string;
  photo: string;
  region_code: string;
  weight: number;
}

interface UserListResponse {
  people: User[];
  lasttime: string;
}

export const useUserListStore = defineStore('userList', () => {
  const people = ref<User[]>([]);
  const lasttime = ref<string | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // 初始化时从本地存储加载数据
  const initializeStore = () => {
    const storedData = localStorage.getItem('userListStore');
    if (storedData) {
      const parsedData = JSON.parse(storedData);
      people.value = parsedData.people || [];
      lasttime.value = parsedData.lasttime || null;
    }
    checkLasttimeAndUpdate();
  };

  // 检查最新时间并更新数据
  const checkLasttimeAndUpdate = async () => {
    try {
      const response = await apiClient.get('/api/getlasttime');
      const serverLasttime = response.data as string;
      
      if (serverLasttime && (!lasttime.value || serverLasttime > lasttime.value)) {
        await fetchUserList();
      }
    } catch (err) {
      error.value = '检查更新时间失败';
      console.error('Failed to check lasttime:', err);
    }
  };

  // 获取用户列表的action
  const fetchUserList = async () => {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await apiClient.get<UserListResponse>('/api/explore_people');
      if (response.status === 200 && response.data) {
        people.value = response.data.people;
        lasttime.value = response.data.lasttime;
        saveToLocalStorage();
      }
    } catch (err) {
      error.value = '获取用户列表失败';
      console.error('Failed to fetch user list:', err);
    } finally {
      isLoading.value = false;
    }
  };

  // 保存数据到本地存储
  const saveToLocalStorage = () => {
    localStorage.setItem('userListStore', JSON.stringify({
      people: people.value,
      lasttime: lasttime.value
    }));
  };

  // 监听数据变化，自动保存到本地存储
  watchEffect(() => {
    saveToLocalStorage();
  });

  // 计算属性：格式化用户生日
  const formattedPeople = computed(() => {
    return people.value.map(person => ({
      ...person,
      formattedBirthDate: new Date(person.birth_date).toLocaleDateString()
    }));
  });

  return {
    people,
    lasttime,
    isLoading,
    error,
    formattedPeople,
    initializeStore,
    fetchUserList
  };
});  