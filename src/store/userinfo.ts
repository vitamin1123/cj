// stores/userInfo.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/plugins/axios'; 

interface UserProfile {
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
  income_level: string
  religion: string
  mbti: string
  mem: string
  mem_pri: string
  avatar: string
  avatar_url: string
  photo: string
}

export const useUserInfoStore = defineStore('userInfo', () => {
  const profile = ref<UserProfile | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 获取用户资料的action
  const fetchUserProfile = async () => {
    isLoading.value = true
    error.value = null
    try {
      const response = await apiClient.get('/api/getprofile')
      if (response.status === 200 && response.data) {
        profile.value = response.data
      }
    } catch (err) {
      error.value = '获取用户资料失败'
      console.error('Failed to fetch user profile:', err)
    } finally {
      isLoading.value = false
    }
  }

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

  return {
    profile,
    isLoading,
    error,
    birthDateObj,
    formattedBirthDate,
    fetchUserProfile
  }
})