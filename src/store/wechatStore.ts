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
  const token = ref<string | null>(localStorage.getItem('wechat_token'))
  const loading = ref(false)
  const error = ref<string | null>(null)

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

  // 清除用户信息
  function clearUser() {
    user.value = null
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
    key: 'wechat-store',
    storage: localStorage,
    paths: ['user']
  }
})