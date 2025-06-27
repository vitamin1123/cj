// stores/likeStore.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Ref } from 'vue'
import apiClient from '@/plugins/axios' // 导入您封装的apiClient

interface LikeRecord {
  user_id: number;
  created_at: string;
}

export const useLikeStore = defineStore('likes', () => {
  // 使用字典存储数据
  const ilikeDict: Ref<Record<number, string>> = ref({}) // 键：用户ID，值：点赞时间字符串
  const likemeDict: Ref<Record<number, string>> = ref({}) // 键：用户ID，值：点赞时间字符串
  
  // 获取点赞数据
  const fetchLikes = async (): Promise<boolean> => {
    try {
      const response = await apiClient.get('/api/get-likes')
      
      // 重置字典
      ilikeDict.value = {}
      likemeDict.value = {}
      
      // 将数组转换为字典
      const ilikeList: LikeRecord[] = response.data.ilike || []
      ilikeList.forEach(item => {
        ilikeDict.value[item.user_id] = item.created_at
      })
      
      const likemeList: LikeRecord[] = response.data.likeme || []
      likemeList.forEach(item => {
        likemeDict.value[item.user_id] = item.created_at
      })
      
      return true
    } catch (error) {
      console.error('获取点赞数据失败:', error)
      return false
    }
  }
  
  // 检查是否喜欢某个用户
  const hasLiked = (userId: number): boolean => {
    return userId in ilikeDict.value
  }
  
  // 检查是否被某个用户喜欢
  const hasBeenLikedBy = (userId: number): boolean => {
    return userId in likemeDict.value
  }
  
  // 添加新的点赞（本地更新）
  const addLike = (userId: number): void => {
    ilikeDict.value[userId] = new Date().toISOString()
  }
  
  // 移除点赞（本地更新）
  const removeLike = (userId: number): void => {
    delete ilikeDict.value[userId]
  }
  
  // 获取我喜欢的用户ID列表
  const ilikeIds = (): number[] => {
    return Object.keys(ilikeDict.value).map(id => parseInt(id))
  }
  
  // 获取喜欢我的用户ID列表
  const likemeIds = (): number[] => {
    return Object.keys(likemeDict.value).map(id => parseInt(id))
  }
  
  // 获取我喜欢的用户数量
  const ilikeCount = (): number => {
    return Object.keys(ilikeDict.value).length
  }
  
  // 获取喜欢我的用户数量
  const likemeCount = (): number => {
    return Object.keys(likemeDict.value).length
  }
  
  return {
    ilikeDict,
    likemeDict,
    fetchLikes,
    hasLiked,
    hasBeenLikedBy,
    addLike,
    removeLike,
    ilikeIds,
    likemeIds,
    ilikeCount,
    likemeCount
  }
})