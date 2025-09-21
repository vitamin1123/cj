import { defineStore } from 'pinia'
import { ref, computed, watchEffect, toRaw } from 'vue'
import apiClient from '@/plugins/axios'
import localforage from 'localforage'

// 配置 localForage
const userListStorage = localforage.createInstance({
  name: 'userListDB',
  storeName: 'userListStore',
  description: 'Storage for user list data'
})

// 类型定义
interface User {
  avatar: string
  birth_date: string
  education: string
  gender: string
  height: number
  id: number
  income_level: number
  mem: string
  nickname: string
  occupation: string
  photo: string
  region_code: string
  weight: number
  updated_at?: string
  tip: number
  istop: number
  married: number
  child: number
  points: number
}

interface UserListResponse {
  people: Record<string, User>
  lasttime: string
}

interface StoredUserListData {
  usersById: Record<number, User>;
  lasttime: string | null;
  sortedIds: number[]; // 新增：有序ID数组
}

// 创建自定义持久化存储
const createPersistStorage = () => ({
  getItem: (key: string): string | null => {
    try {
      const data = localStorage.getItem(key);
      return data || null;
    } catch (err) {
      console.error('Failed to read from localStorage:', err);
      return null;
    }
  },
  setItem: (key: string, value: string): void => {
    localStorage.setItem(key, value);
  },
  removeItem: (key: string): void => {
    localStorage.removeItem(key);
  }
});

// 排序函数：根据istop和points排序
const sortUserIds = (users: Record<number, User>): number[] => {
  return Object.values(users)
    .sort((a, b) => {
      if (a.istop !== b.istop) return b.istop - a.istop;
      return b.points - a.points;
    })
    .map(user => user.id);
};

export const useUserListStore = defineStore(
  'userList',
  () => {
    const usersById = ref<Record<number, User>>({});
    const sortedIds = ref<number[]>([]); // 新增：有序ID数组
    const lasttime = ref<string | null>(null);
    const isLoading = ref(false);
    const error = ref<string | null>(null);

    // 计算属性：获取按排序后的用户数组
    const peopleArray = computed(() => {
      return sortedIds.value.map(id => usersById.value[id]).filter(Boolean);
    });

    // 计算属性：获取用户Map（保持不变，用于快速查找）
    const usersMap = computed(() => usersById.value);

    // Actions
    const checkLasttimeAndUpdate = async (): Promise<void> => {
      try {
        const response = await apiClient.get('/api/getlasttime')
        const serverLasttime = response.data.lasttime as string
        
        const hasLocalData = sortedIds.value.length > 0
        const hasLastTime = !!lasttime.value
        
        if (!hasLocalData || !hasLastTime) {
          await fetchUserList()
          return
        }
        
        if (serverLasttime && lasttime.value && serverLasttime > lasttime.value) {
          await fetchIncrementalUserList(lasttime.value)
        }
      } catch (err) {
        error.value = '检查更新时间失败'
        console.error('Failed to check lasttime:', err)
        await fetchUserList()
      }
    }

    const fetchUserList = async (): Promise<void> => {
      isLoading.value = true;
      error.value = null;
      try {
        const response = await apiClient.get<UserListResponse>('/api/explore_people_dic');
        if (response.status === 200 && response.data) {
          const rawData = response.data.people;
          
          // 转换键为数字类型
          const processedDict: Record<number, User> = {};
          Object.entries(rawData).forEach(([key, user]) => {
            const userId = parseInt(key, 10);
            if (!isNaN(userId)) {
              processedDict[userId] = user;
            }
          });

          usersById.value = processedDict;
          sortedIds.value = sortUserIds(processedDict); // 更新有序ID数组
          lasttime.value = response.data.lasttime;
          
          console.log(`成功加载 ${sortedIds.value.length} 条用户数据`);
        }
      } catch (err) {
        error.value = '获取用户列表失败';
        console.error('Failed to fetch user list:', err);
      } finally {
        isLoading.value = false;
      }
    };

    const fetchIncrementalUserList = async (since: string): Promise<void> => {
      isLoading.value = true;
      error.value = null;

      try {
        const response = await apiClient.post<{
          updates: Record<number, User>;
          removed: number[];
          serverLasttime: string;
        }>(`/api/explore_people_updated_dic`, {since});

        const { updates, removed, serverLasttime } = response.data;

        // ✅ 1. 合并更新/新增（含被启用用户）
        Object.entries(updates).forEach(([idStr, user]) => {
          const id = parseInt(idStr, 10);
          usersById.value[id] = user;
        });

        // ✅ 2. 移除过期/禁用用户
        removed.forEach((id) => {
          delete usersById.value[id];
        });

        // ✅ 3. 重新排序
        sortedIds.value = sortUserIds(usersById.value);
        lasttime.value = serverLasttime;

        console.log(`增量更新：${Object.keys(updates).length} 条新增/更新，${removed.length} 条移除`);
      } catch (err) {
        error.value = '获取增量更新失败';
        console.error(err);
      } finally {
        isLoading.value = false;
      }
    };

    // const fetchIncrementalUserList = async (since: string): Promise<void> => {
    //   isLoading.value = true;
    //   error.value = null;
    //   try {
    //     const response = await apiClient.get<UserListResponse>(
    //       `/api/explore_people_updated_dic?since=${since}`
    //     );
        
    //     if (response.status === 200 && response.data) {
    //       const rawData = response.data.people;
          
    //       // 合并/更新现有用户数据
    //       Object.entries(rawData).forEach(([key, user]) => {
    //         const userId = parseInt(key, 10);
    //         if (!isNaN(userId)) {
    //           usersById.value[userId] = user;
    //         }
    //       });
          
    //       // 重新排序并更新有序ID数组
    //       sortedIds.value = sortUserIds(usersById.value);
    //       lasttime.value = response.data.lasttime;
          
    //       console.log(`成功更新 ${Object.keys(rawData).length} 条用户数据`);
    //     }
    //   } catch (err) {
    //     error.value = '获取增量用户列表失败';
    //     console.error('Failed to fetch incremental user list:', err);
    //   } finally {
    //     isLoading.value = false;
    //   }
    // };
    
    const initializeStore = async (): Promise<void> => {
      try {
        const storedData = await userListStorage.getItem<StoredUserListData>('userListData');
        
        if (storedData) {
          usersById.value = storedData.usersById;
          sortedIds.value = storedData.sortedIds || sortUserIds(storedData.usersById); // 兼容旧数据
          lasttime.value = storedData.lasttime;
          console.log(`从存储加载 ${sortedIds.value.length} 条用户数据`);
        }
      } catch (err) {
        console.error('初始化存储失败:', err);
        await userListStorage.removeItem('userListData');
      }
      
      await checkLasttimeAndUpdate();
    }

    const saveToStorage = async (): Promise<void> => {
      try {
        const rawUsersById = toRaw(usersById.value);
        const rawSortedIds = toRaw(sortedIds.value);
        const rawLasttime = lasttime.value;
        
        const dataToStore: StoredUserListData = {
          usersById: rawUsersById,
          sortedIds: rawSortedIds,
          lasttime: rawLasttime
        };
        
        await userListStorage.setItem('userListData', dataToStore);
      } catch (err) {
        console.error('保存数据失败:', err);
        if ((err as Error).name === 'QuotaExceededError') {
          console.warn('存储空间不足，尝试清理旧数据...');
          const allIds = Object.keys(usersById.value);
          if (allIds.length > 100) {
            const idsToRemove = allIds
              .slice(0, allIds.length - 100)
              .map(id => parseInt(id, 10));
            
            idsToRemove.forEach(id => {
              delete usersById.value[id];
            });
            
            // 重新排序
            sortedIds.value = sortUserIds(usersById.value);
            console.log(`清理了 ${idsToRemove.length} 条旧数据`);
            await saveToStorage();
          }
        }
      }
    }

    // 计算属性：格式化用户信息（保持不变）
    const formattedPeople = computed(() => {
      return peopleArray.value.map(person => ({
        ...person,
        formattedBirthDate: person.birth_date 
          ? new Date(person.birth_date).toLocaleDateString() 
          : '未知'
      }));
    });

    // 自动保存
    watchEffect(() => {
      const hasUsers = sortedIds.value.length > 0;
      if (hasUsers || lasttime.value) {
        saveToStorage();
      }
    })

    return {
      usersById,
      sortedIds, // 暴露有序ID数组
      lasttime,
      isLoading,
      error,
      
      formattedPeople,
      peopleArray,
      usersMap,
      
      initializeStore,
      fetchUserList,
      checkLasttimeAndUpdate
    }
  },
  {
    persist: {
      key: 'userListStore',
      storage: createPersistStorage(),
      serializer: {
        serialize: JSON.stringify,
        deserialize: JSON.parse
      }
    }
  }
)