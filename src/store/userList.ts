import { defineStore } from 'pinia'
import { ref, computed, watchEffect } from 'vue'
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
  updated_at?:string
}

interface UserListResponse {
  people: User[]
  lasttime: string
}

interface StoredUserListData {
  people: User[]
  lasttime: string | null
}

// 自定义存储适配器类型
interface CustomPersistStorage {
  getItem: (key: string) => Promise<string | null>
  setItem: (key: string, value: string) => Promise<void>
  removeItem?: (key: string) => Promise<void>
}

// 创建自定义持久化存储
const createPersistStorage = () => ({
  getItem: (key: string): string | null => {
    // 注意：这里使用了同步的localforage.getItemSync（需要localforage 1.10+）
    // 或者使用同步的localStorage作为fallback
    try {
      const data = localStorage.getItem(key); // 同步读取
      return data || null;
    } catch (err) {
      console.error('Failed to read from localStorage:', err);
      return null;
    }
  },
  setItem: (key: string, value: string): void => {
    localStorage.setItem(key, value); // 同步写入
  },
  removeItem: (key: string): void => {
    localStorage.removeItem(key); // 同步删除
  }
});

export const useUserListStore = defineStore(
  'userList',
  () => {
    // State
    const people = ref<User[]>([])
    const lasttime = ref<string | null>(null)
    const isLoading = ref(false)
    const error = ref<string | null>(null)

    // Actions
    const checkLasttimeAndUpdate = async (): Promise<void> => {
      try {
        const response = await apiClient.get('/api/getlasttime')
        const serverLasttime = response.data as string
        
        if (serverLasttime && (!lasttime.value || serverLasttime > lasttime.value)) {
          await fetchUserList()
        }
      } catch (err) {
        error.value = '检查更新时间失败'
        console.error('Failed to check lasttime:', err)
      }
    }

    const fetchUserList = async (): Promise<void> => {
      isLoading.value = true
      error.value = null
      try {
        const response = await apiClient.get<UserListResponse>('/api/explore_people')
        if (response.status === 200 && response.data) {
          people.value = response.data.people
          lasttime.value = response.data.lasttime
        }
      } catch (err) {
        error.value = '获取用户列表失败'
        console.error('Failed to fetch user list:', err)
      } finally {
        isLoading.value = false
      }
    }

    

    const initializeStore = async (): Promise<void> => {
      try {
        const storedData = await userListStorage.getItem<StoredUserListData>('userListData')
        if (storedData) {
          people.value = storedData.people || []
          lasttime.value = storedData.lasttime || null
        }
        await checkLasttimeAndUpdate()
      } catch (err) {
        console.error('Failed to initialize store:', err)
      }
    }

    const saveToStorage = async (): Promise<void> => {
      try {
        const dataToStore: StoredUserListData = {
          people: people.value,
          lasttime: lasttime.value
        }
        await userListStorage.setItem('userListData', dataToStore)
      } catch (err) {
        console.error('Failed to save data:', err)
        if ((err as Error).name === 'QuotaExceededError') {
          console.warn('存储空间不足，尝试清理旧数据...')
        }
      }
    }

    // Computed
    const formattedPeople = computed(() => {
      return people.value.map(person => ({
        ...person,
        formattedBirthDate: person.birth_date 
          ? new Date(person.birth_date).toLocaleDateString() 
          : '未知'
      }))
    })

    // Auto-save when data changes
    watchEffect(() => {
      if (people.value.length > 0 || lasttime.value) {
        saveToStorage()
      }
    })

    

    return {
      // State
      people,
      lasttime,
      isLoading,
      error,
      
      // Computed
      formattedPeople,
      
      // Actions
      initializeStore,
      fetchUserList
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