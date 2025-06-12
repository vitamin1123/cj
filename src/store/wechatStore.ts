// src/store/wechatStore.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

interface WechatUser {
  openid: string
  unionid?: string
  subscribe: number
  language?: string
  subscribe_time?: number
  created_at: string
}

export const useWechatStore = defineStore('wechat', () => {
  const user = ref<WechatUser | null>(null)
  const token = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 初始化时尝试从本地存储加载
  function initializeFromStorage() {
    const storedToken = localStorage.getItem('wechat_token')
    if (storedToken) {
      token.value = storedToken
      axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
    }
  }

  // 调用初始化
  initializeFromStorage()

  // 设置token
  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('wechat_token', newToken)
    // 设置axios默认header
    axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
  }

  // 清除token
  function clearToken() {
    token.value = null
    localStorage.removeItem('wechat_token')
    delete axios.defaults.headers.common['Authorization']
  }

  // 设置用户信息
  function setUser(userInfo: WechatUser) {
    user.value = userInfo
  }

  // 新增：设置openid方法
  function setOpenid(openid: string) {
    if (user.value) {
      // 如果已有用户数据，更新openid
      user.value.openid = openid
    } else {
      // 创建基础用户对象
      user.value = {
        openid,
        subscribe: 0, // 默认值
        created_at: new Date().toISOString() // 当前时间
      }
    }
    
    // 单独存储openid以备其他用途
    localStorage.setItem('wechat_openid', openid)
  }

  // 清除用户信息
  function clearUser() {
    user.value = null
    localStorage.removeItem('wechat_openid')
  }

  // 从URL获取openid（微信网页授权后会在URL中）
  function getOpenidFromUrl(): string | null {
    const urlParams = new URLSearchParams(window.location.search)
    return urlParams.get('openid')
  }

  // 微信认证
  async function authenticate(openid: string) {
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.post('/api/wechat/auth', { openid })
      const { access_token } = response.data
      
      setToken(access_token)
      
      // 获取用户信息
      await fetchUserInfo()
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || '认证失败'
      clearToken()
      clearUser()
      return false
    } finally {
      loading.value = false
    }
  }

  // 获取用户信息
  async function fetchUserInfo() {
    if (!token.value) return false
    
    try {
      const response = await axios.get('/api/wechat/user/me')
      setUser(response.data)
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取用户信息失败'
      if (err.response?.status === 401) {
        clearToken()
        clearUser()
      }
      return false
    }
  }

  // 刷新用户信息
  async function refreshUserInfo() {
    if (!token.value) return false
    
    loading.value = true
    try {
      await axios.post('/api/wechat/user/refresh')
      await fetchUserInfo()
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || '刷新用户信息失败'
      return false
    } finally {
      loading.value = false
    }
  }

  // 初始化（检查token有效性）
  async function initialize() {
    if (token.value) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      const success = await fetchUserInfo()
      if (!success) {
        clearToken()
        clearUser()
      }
      return success
    }
    return false
  }

  // 登出
  function logout() {
    clearToken()
    clearUser()
  }

  return {
    user,
    token,
    loading,
    error,
    setToken,
    clearToken,
    setUser,
    setOpenid,
    clearUser,
    getOpenidFromUrl,
    authenticate,
    fetchUserInfo,
    refreshUserInfo,
    initialize,
    logout
  }
}, {
  persist: {
    enabled: true,
    strategies: [
      {
        key: 'wechat-store',
        storage: localStorage,
        paths: ['user']
      }
    ]
  }
})