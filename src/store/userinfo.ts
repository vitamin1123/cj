// // stores/userInfo.ts
// import { defineStore } from 'pinia'
// import { ref, computed } from 'vue'
// import apiClient from '@/plugins/axios'; 

// interface UserProfile {
//   id: number
//   nickname: string
//   phone: string
//   gender: string
//   birth_date: string
//   height: number
//   weight: number
//   region_code: string
//   occupation: string
//   education: string
//   income_level: string
//   religion: string
//   mbti: string
//   mem: string
//   mem_pri: string
//   avatar: string
//   avatar_url: string
//   photo: string
//   points: number
// }

// export const useUserInfoStore = defineStore('userInfo', () => {
//   const profile = ref<UserProfile | null>(null)
//   const isLoading = ref(false)
//   const error = ref<string | null>(null)

//   // 获取用户资料的action
//   const fetchUserProfile = async () => {
//     isLoading.value = true
//     error.value = null
//     try {
//       const response = await apiClient.get('/api/getprofile')
//       if (response.status === 200 && response.data) {
//         profile.value = response.data
//       }
//     } catch (err) {
//       error.value = '获取用户资料失败'
//       console.error('Failed to fetch user profile:', err)
//     } finally {
//       isLoading.value = false
//     }
//   }

//   // 计算属性：格式化生日日期对象
//   const birthDateObj = computed(() => {
//     if (!profile.value?.birth_date) return null
//     return new Date(profile.value.birth_date)
//   })

//   // 计算属性：格式化生日显示数组
//   const formattedBirthDate = computed(() => {
//     if (!birthDateObj.value) return null
//     return [
//       birthDateObj.value.getFullYear().toString(),
//       (birthDateObj.value.getMonth() + 1).toString(),
//       birthDateObj.value.getDate().toString()
//     ]
//   })

//   return {
//     profile,
//     isLoading,
//     error,
//     birthDateObj,
//     formattedBirthDate,
//     fetchUserProfile
//   }
// })

// 第二版
// stores/userInfo.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/plugins/axios'
import { NumberKeyboardTheme } from 'vant'

/* ---------- 类型定义 ---------- */
export interface UserProfile {
  id: number
  nickname: string
  phone: string
  gender: string
  birth_date: string
  height: number
  weight: number
  region_code: string
  occupation: string
  education: string
  income_level: number
  religion: string
  mbti: string
  mem: string
  mem_pri: string
  avatar: string
  avatar_url: string
  photo: string
  points: number
}

/* ---------- localStorage 读写 ---------- */
const LS_KEY = 'user_profile_cache' // 可换成你喜欢的名字

function readLocalProfile(): UserProfile | null {
  try {
    const raw = localStorage.getItem(LS_KEY)
    return raw ? (JSON.parse(raw) as UserProfile) : null
  } catch {
    return null
  }
}

function writeLocalProfile(data: UserProfile | null) {
  if (data) {
    localStorage.setItem(LS_KEY, JSON.stringify(data))
  } else {
    localStorage.removeItem(LS_KEY)
  }
}

/* ---------- store 主体 ---------- */
export const useUserInfoStore = defineStore('userInfo', () => {
  const profile = ref<UserProfile | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性：格式化生日日期对象
  const birthDateObj = computed(() => {
    if (!profile.value?.birth_date) return null
    return new Date(profile.value.birth_date)
  })

  // 计算属性：格式化生日显示数组
  const formattedBirthDate = computed(() => {
    if (!birthDateObj.value) return null
    return [
      birthDateObj.value.getFullYear().toString(),
      (birthDateObj.value.getMonth() + 1).toString(),
      birthDateObj.value.getDate().toString()
    ]
  })

  // 新增一个 action 用于更新 profile 并写入本地存储
  const updateProfileAndCache = (newProfile: UserProfile) => {
    profile.value = newProfile
    writeLocalProfile(newProfile)
  }

  // 拉取用户资料（含兜底逻辑）
  const fetchUserProfile = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.get('/api/getprofile')

      // ✅ 后端正常返回
      if (response.status === 200 && response.data) {
        updateProfileAndCache(response.data) // 使用新的 action
        return
      }

      // ⚠️ 后端 200 但空数据
      throw new Error('empty data')
    } catch (err) {
      // ❌ 网络/接口异常 或 空数据
      console.error('Failed to fetch user profile:', err)

      // 先去本地读一份旧档案
      const cached = readLocalProfile()
      if (cached) {
        profile.value = cached
        error.value = null // 用本地数据就不报错了
        return
      }

      // 本地也没有，才算真正的「获取失败」
      profile.value = null
      error.value = '获取用户资料失败'
    } finally {
      isLoading.value = false
    }
  }

  // 手动清空本地缓存（审核通过后可调用）
  const clearLocalProfile = () => {
    writeLocalProfile(null)
  }

  return {
    profile,
    isLoading,
    error,
    birthDateObj,
    formattedBirthDate,
    fetchUserProfile,
    clearLocalProfile,
    updateProfileAndCache // 导出新的 action
  }
})

export { writeLocalProfile }