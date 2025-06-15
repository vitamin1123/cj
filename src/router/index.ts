// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import Result404 from '@/views/NotFound404View/NotFound404View.vue'
// import { useWechatStore } from '@/store/wechatStore'
import { useAuthStore } from '@/store/authStore'
import axios from 'axios'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // 关键修改：简化/auth-success路由，只做跳转处理
    {
      path: '/auth-success',
      name: 'auth-success',
      component: {
        template: '<div style="padding: 20px; text-align: center;">授权成功，跳转中...</div>'
      },
      beforeEnter: (to, from, next) => {
        // const openid = to.query.openid as string
        const token = to.query.token as string
        if ( token) {
          // 立即保存openid到store和localStorage
          
          const authStore = useAuthStore()
          
          authStore.setToken(token)
          // localStorage.setItem('wechat_openid', openid)
          
          // 强制跳转到/home，使用replace避免历史记录问题
          next({ path: '/home', replace: true })
        } else {
          // 没有openid时强制跳转到提示页
          next({ path: '/reopen', replace: true })
        }
      }
    },
    {
      path: '/404',
      name: '404',
      component: Result404,
      meta: { title: '404' }
    },
    {
      path: '/',
      name: 'index',
      redirect: '/home' // 根路径直接重定向到home
    },
    {
      path: '/home',
      name: 'home',
      component: () => import('@/views/Home/Home.vue'),
      meta: { title: '首页' }
    },
    {
      path: '/userCenter',
      name: 'userCenter',
      component: () => import('@/views/userCenter/userCenter.vue'),
      meta: { title: '个人中心' }
    },
    {
      path: '/detail/:id',
      name: 'detail',
      component: () => import('@/views/Detail/Detail.vue'),
      meta: { title: '详细信息' }
    },
    {
      path: '/explore',
      name: 'explore',
      component: () => import('@/views/Explore/Explore.vue'),
      meta: { title: '寻觅' }
    },
    {
      path: '/likes',
      name: 'likes',
      component: () => import('@/views/Likes/Likes.vue'),
      meta: { title: '喜欢' }
    },
    {
      path: '/profile-setup',
      name: 'ProfileSetup',
      component: () => import('@/views/ProfileSetup/ProfileSetup.vue')
    },
    {
      path: '/reopen',
      name: 'reopen',
      component: () => import('@/views/ReopenPage/ReopenPage.vue'),
      meta: { title: '请在微信中打开' }
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/404'
    }
  ]
})

// 配置axios基础URL
axios.defaults.baseURL = 'http://www.tianshunchenjie.com'

// 微信授权相关函数 - 确保立即跳转
const triggerWechatLogin = () => {
  const appId = 'wxccbf0238cab0a75c'
  const backendUrl = 'http://www.tianshunchenjie.com'
  const redirectUri = encodeURIComponent(`${backendUrl}/api/wechat/callback`)
  const state = 'STATE_' + Date.now() + '_' + Math.random().toString(36).substr(2, 8)
  
  const authUrl = `https://open.weixin.qq.com/connect/oauth2/authorize?appid=${appId}&redirect_uri=${redirectUri}&response_type=code&scope=snsapi_base&state=${state}#wechat_redirect`
  
  localStorage.setItem('wechat_auth_state', state)
  
  // 立即跳转，不等待
  window.location.href = authUrl
}

// 路由守卫 - 只处理openid检查
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = (to.meta?.title as string) ?? '自助功能'
  
  // 特殊路径直接放行
  if (to.path === '/reopen' || to.path === '/auth-success' || to.path === '/404') {
    return next()
  }

  // 检查是否有openid
  const storedOpenid = localStorage.getItem('wechat_openid')
  if (!storedOpenid) {
    // 检查是否在微信环境中
    const isWechat = /micromessenger/i.test(navigator.userAgent)
    
    if (!isWechat) {
      // 不在微信环境，跳转到重新打开页面
      return next({ path: '/reopen', replace: true })
    } else {
      // 在微信环境但没有openid，立即触发授权
      triggerWechatLogin()
      return // 停止后续处理
    }
  }

  next()
})

export default router