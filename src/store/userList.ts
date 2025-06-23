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
  people: string
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
        const serverLasttime = response.data.lasttime as string
        
        // 判断是否是首次加载（本地没有lasttime或没有用户数据）
        const isFirstLoad = !lasttime.value || people.value.length === 0
        
        // 如果有本地数据且服务器时间更新
        if (!isFirstLoad && serverLasttime && lasttime.value && serverLasttime > lasttime.value) {
          await fetchIncrementalUserList(lasttime.value) // 这里确保 lasttime.value 不为 null
        }
        // 如果是首次加载
        else if (isFirstLoad) {
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
          const parsedPeople = JSON.parse(response.data.people) as User[]
          people.value = parsedPeople
          lasttime.value = response.data.lasttime
        }
      } catch (err) {
        error.value = '获取用户列表失败'
        console.error('Failed to fetch user list:', err)
      } finally {
        isLoading.value = false
      }
    }
// 获取增量数据
const fetchIncrementalUserList = async (since: string): Promise<void> => {
      isLoading.value = true
      error.value = null
      try {
        const response = await apiClient.get<{ 
          people: User[]; 
          lasttime: string 
        }>(`/api/explore_people_updated?since=${since}`)
        
        if (response.status === 200 && response.data) {
          const newPeople = response.data.people
          
          // 如果没有新数据，直接返回
          if (newPeople.length === 0) {
            console.log('没有新的用户数据')
            return
          }
          
          // 创建现有用户的ID映射
          const existingPeopleMap = new Map<number, User>()
          people.value.forEach(user => existingPeopleMap.set(user.id, user))
          
          // 合并新数据
          newPeople.forEach(newUser => {
            existingPeopleMap.set(newUser.id, newUser)
          })
          
          // 更新状态
          people.value = Array.from(existingPeopleMap.values())
          lasttime.value = response.data.lasttime
          
          console.log(`成功合并 ${newPeople.length} 条增量用户数据`)
        }
      } catch (err) {
        error.value = '获取增量用户列表失败'
        console.error('Failed to fetch incremental user list:', err)
        
        // 如果增量更新失败，回退到全量更新
        await fetchUserList()
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
        
        // 无论是否有存储数据，都检查更新
        await checkLasttimeAndUpdate()
      } catch (err) {
        console.error('Failed to initialize store:', err)
        // 初始化失败时尝试获取全量数据
        await fetchUserList()
      }
    }

    const saveToStorage = async (): Promise<void> => {
      try {
        // 修改保存数据的部分
        const dataToStore: StoredUserListData = {
          people: JSON.parse(JSON.stringify(people.value)), // 深度克隆
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