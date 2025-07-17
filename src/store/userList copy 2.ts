import { defineStore } from 'pinia'
import { ref, computed, watchEffect, toRaw  } from 'vue'
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
  income_level: string
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
  people: Record<string, User>  // 后端返回的是字符串化的对象
  lasttime: string
}

interface StoredUserListData {
  usersById: Record<number, User>;
  lasttime: string | null;
}

// 自定义存储适配器类型
interface CustomPersistStorage {
  getItem: (key: string) => Promise<string | null>
  setItem: (key: string, value: string) => Promise<void>
  removeItem?: (key: string) => Promise<void>
}

function sortUsersRecord(record: Record<number, User>): Record<number, User> {
  const entries = Object.entries(record).map(([idStr, user]) => [
    Number(idStr),
    user,
  ]) as [number, User][];

  entries.sort(([, a], [, b]) => {
    if (a.istop !== b.istop) return b.istop - a.istop;
    return b.points - a.points;
  });

  // 重新组装成对象（保持插入顺序）
  const sorted: Record<number, User> = {};
  entries.forEach(([id, user]) => {
    sorted[id] = user;
  });
  return sorted;
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

export const useUserListStore = defineStore(
  'userList',
  () => {
    // 使用对象存储
    const usersById = ref<Record<number, User>>({});
    const lasttime = ref<string | null>(null);
    const isLoading = ref(false);
    const error = ref<string | null>(null);

    // 计算属性：获取用户数组
    const peopleArray = computed(() => Object.values(usersById.value));
    
    // Actions
    const checkLasttimeAndUpdate = async (): Promise<void> => {
      try {
        const response = await apiClient.get('/api/getlasttime')
        const serverLasttime = response.data.lasttime as string
        
        // 改进首次加载判断逻辑
        const hasLocalData = Object.keys(usersById.value).length > 0
        const hasLastTime = !!lasttime.value
        
        // 首次加载：无本地数据或没有lasttime
        if (!hasLocalData || !hasLastTime) {
          await fetchUserList()
          return
        }
        
        // 服务器有更新时获取增量数据
        if (serverLasttime && lasttime.value && serverLasttime > lasttime.value) {
          await fetchIncrementalUserList(lasttime.value)
        }
      } catch (err) {
        error.value = '检查更新时间失败'
        console.error('Failed to check lasttime:', err)
        // 回退到全量更新
        await fetchUserList()
      }
    }

    // 优化后的fetchUserList - 直接处理对象格式
    const fetchUserList = async (): Promise<void> => {
      isLoading.value = true;
      error.value = null;
      try {
        const response = await apiClient.get<UserListResponse>('/api/explore_people_dic');
        if (response.status === 200 && response.data) {
          // 直接处理API返回的对象格式
          const rawData = response.data.people;
          
          // 转换键为数字类型
          const processedDict: Record<number, User> = {};
          
          Object.entries(rawData).forEach(([key, user]) => {
            const userId = parseInt(key, 10);
            if (!isNaN(userId)) {
              processedDict[userId] = user;
            } else {
              console.warn(`Invalid user ID: ${key}`);
            }
          });

          usersById.value = processedDict;
          lasttime.value = response.data.lasttime;
          console.log(`成功加载 ${Object.keys(processedDict).length} 条用户数据`);
        }
      } catch (err) {
        error.value = '获取用户列表失败';
        console.error('Failed to fetch user list:', err);
        
        // 更详细的错误日志
        if (err instanceof SyntaxError) {
          console.error('JSON解析错误，原始数据:', err);
        }
      } finally {
        isLoading.value = false;
      }
    };

    // 优化增量数据获取
    const fetchIncrementalUserList = async (since: string): Promise<void> => {
      isLoading.value = true;
      error.value = null;
      try {
        const response = await apiClient.get<UserListResponse>(
          `/api/explore_people_updated_dic?since=${since}`
        );
        
        if (response.status === 200 && response.data) {
          const rawData = response.data.people;
          
          // 处理增量数据
          Object.entries(rawData).forEach(([key, user]) => {
            const userId = parseInt(key, 10);
            if (!isNaN(userId)) {
              // 合并/更新现有用户数据
              usersById.value[userId] = user;
            }
          });
          
          lasttime.value = response.data.lasttime;
          console.log(`成功更新 ${Object.keys(rawData).length} 条用户数据`);
        }
      } catch (err) {
        error.value = '获取增量用户列表失败';
        console.error('Failed to fetch incremental user list:', err);
      } finally {
        isLoading.value = false;
      }
    };
    
    // 初始化方法
    const initializeStore = async (): Promise<void> => {
      try {
        const storedData = await userListStorage.getItem<StoredUserListData>('userListData');
        
        if (storedData) {
          // 直接使用存储的数据
          usersById.value = storedData.usersById;
          lasttime.value = storedData.lasttime;
          console.log(`从存储加载 ${Object.keys(storedData.usersById).length} 条用户数据`);
        }
      } catch (err) {
        console.error('初始化存储失败:', err);
        // 清除问题数据
        await userListStorage.removeItem('userListData');
      }
      
      // 无论是否有本地数据都检查更新
      await checkLasttimeAndUpdate();
    }

    const saveToStorage = async (): Promise<void> => {
      try {
        // 使用 toRaw 获取非响应式原始数据
        const rawUsersById = toRaw(usersById.value);
        const rawLasttime = lasttime.value; // 基本类型不需要转换
        
        const dataToStore: StoredUserListData = {
          usersById: rawUsersById,
          lasttime: rawLasttime
        };
        
        await userListStorage.setItem('userListData', dataToStore);
      } catch (err) {
        console.error('保存数据失败:', err);
        if ((err as Error).name === 'QuotaExceededError') {
          console.warn('存储空间不足，尝试清理旧数据...');
          // 清理策略：保留最近的100个用户
          const allIds = Object.keys(usersById.value);
          if (allIds.length > 100) {
            const idsToRemove = allIds
              .slice(0, allIds.length - 100)
              .map(id => parseInt(id, 10));
            
            idsToRemove.forEach(id => {
              delete usersById.value[id];
            });
            
            console.log(`清理了 ${idsToRemove.length} 条旧数据`);
            // 重试保存
            await saveToStorage();
          }
        }
      }
    }

    // Computed
    const formattedPeople = computed(() => {
      return peopleArray.value.map(person => ({
        ...person,
        formattedBirthDate: person.birth_date 
          ? new Date(person.birth_date).toLocaleDateString() 
          : '未知'
      }));
    });

    // Auto-save when data changes
    watchEffect(() => {
      const hasUsers = Object.keys(usersById.value).length > 0;
      
      if (hasUsers || lasttime.value) {
        saveToStorage();
      }
    })

    return {
      // State
      usersById,
      lasttime,
      isLoading,
      error,
      
      // Computed
      formattedPeople,
      peopleArray, // 暴露计算属性
      
      // Actions
      initializeStore,
      fetchUserList,
      checkLasttimeAndUpdate // 暴露给外部调用
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