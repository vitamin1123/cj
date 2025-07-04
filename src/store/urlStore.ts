// src/stores/urlStore.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUrlStore = defineStore('url', () => {
  // 当前实际URL（Vue Router）
  const currentUrl = ref('')
  // iOS微信初始URL（特殊缓存）
  const iosWechatInitialUrl = ref('')

  // 更新当前URL（路由跳转时调用）
  const updateCurrentUrl = (url: string) => {
    currentUrl.value = url.split('#')[0]
  }

  // 设置iOS微信初始URL（仅首次调用有效）
  const setIosWechatInitialUrl = (url: string) => {
    if (!iosWechatInitialUrl.value) {
      iosWechatInitialUrl.value = url.split('#')[0]
      console.log('缓存iOS微信初始URL:', iosWechatInitialUrl.value)
    }
  }

  // 获取签名用URL（自动处理iOS微信特殊情况）
  const getSignatureUrl = (): string => {
    const isIOSWechat = /iphone|ipad|ipod/i.test(navigator.userAgent) && 
                       /MicroMessenger/i.test(navigator.userAgent)
    
    return isIOSWechat ? iosWechatInitialUrl.value : currentUrl.value
  }

  return { 
    currentUrl,
    iosWechatInitialUrl,
    updateCurrentUrl,
    setIosWechatInitialUrl,
    getSignatureUrl
  }
})