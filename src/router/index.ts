// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import Result404 from '@/views/NotFound404View/NotFound404View.vue'
// import { useWechatStore } from '@/store/wechatStore'
import { useAuthStore } from '@/store/authStore'
import axios from 'axios'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [

    {
      path: '/auth-success',
      name: 'auth-success',
      component: {
        template: '<div style="padding: 20px; text-align: center;">授权成功，跳转中...</div>'
      },
      beforeEnter: (to, from, next) => {
        
        const token = to.query.token as string
        if ( token) {
 
          
          const authStore = useAuthStore()
          
          authStore.setToken(token)

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
      redirect: '/home' 
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
  

  
  window.location.href = authUrl
}

router.beforeEach((to, from, next) => {

  document.title = (to.meta?.title as string) ?? '自助功能'

  if (to.path === '/reopen' || to.path === '/auth-success' || to.path === '/404') {
    return next()
  }

  const authStore = useAuthStore()
  if (!authStore.token) {
    
    const isWechat = /micromessenger/i.test(navigator.userAgent)
    
    if (!isWechat) {
      
      return next({ path: '/reopen', replace: true })
    } else {
      
      triggerWechatLogin()
      return 
    }
  }

  next()
})

export default router