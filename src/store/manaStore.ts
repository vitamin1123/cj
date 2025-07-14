// 创建管理状态存储 manaStore.ts
import { defineStore } from 'pinia'
import apiClient from '@/plugins/axios'

export const useManaStore = defineStore('mana', {
  state: () => ({
    pendingAudit: 0,    // 待审核数量
    unreadMessages: 0   // 未读消息数量
  }),
  actions: {
    // 更新待审核数量
    setPendingAudit(count: number) {
      this.pendingAudit = count
    },
    // 更新未读消息数量
    setUnreadMessages(count: number) {
      this.unreadMessages = count
    },
    // 从API获取待审核数量
    async fetchPendingAudit() {
      try {
        const response = await apiClient.get('/api/getpendingaudit')
        this.setPendingAudit(response.data.count)
      } catch (error) {
        console.error('获取待审核数量失败:', error)
        this.setPendingAudit(0)
      }
    }
  }
})