// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router';
import type { App } from 'vue';
import Result404 from '@/views/NotFound404View/NotFound404View.vue';
import { useAuthStore } from '@/store/authStore';
// import axios from 'axios' // 此行不再需要，axios配置已在plugins/axios.ts中封装
import { setPreviousRoute } from '@/utils/routeHistory';
// 导入我们新创建的微信授权工具函数
import { triggerWechatLogin } from '@/utils/authUtils'; 
import { useUrlStore } from '@/store/urlStore'
import { usePaymentStore } from '@/store/paymentStore';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // ... (保持现有路由配置不变)
    {
      path: '/auth-success',
      name: 'auth-success',
      component: {
        template: '<div style="padding: 20px; text-align: center;">授权成功，跳转中...</div>'
      },
      beforeEnter: (to, from, next) => {
        const token = to.query.token as string;
        if (token) {
          const authStore = useAuthStore();
          authStore.setToken(token);
          next({ path: '/home', replace: true });
        } else {
          next({ path: '/reopen', replace: true });
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
      path: '/chat',
      name: 'Chat',
      component: () => import('@/views/Chat/Chat.vue'),
      meta: { title: '聊天' }
    },
    {
      path: '/detail/:id',
      name: 'detail',
      component: () => import('@/views/Detail/Detail.vue'),
      meta: { title: '详细信息' }
    },
    {
      path: '/profile/:id',
      name: 'profile',
      component: () => import('@/views/Profile/Profile.vue'),
      meta: { title: '用户资料' }
    },
    {
      path: '/explore',
      name: 'explore',
      component: () => import('@/views/Explore/Explore.vue'),
      meta: { title: '寻觅' ,keepAlive: true }
    },
    {
      path: '/payment',
      name: 'payment',
      component: () => import('@/views/Payment/Payment.vue'),
      meta: { title: '开通会员' }
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
      path: '/manacenter',
      name: 'manacenter',
      component: () => import('@/views/ManaCenter/ManaCenter.vue'),
      meta: { title: '管理' }
    },
    {
      path: '/adminchat',
      name: 'adminchat',
      component: () => import('@/views/AdminChat/AdminChat.vue'),
      meta: { title: '沟通' }
    },
    {
      path: '/moderation',
      name: 'moderation',
      component: () => import('@/views/Moderation/Moderation.vue'),
      meta: { title: '审核' }
    },
    {
      path: '/moderation-detail/:id',
      name: 'moderation-detail',
      component: () => import('@/views/ModerationDetail/ModerationDetail.vue'),
      meta: { title: '审核明细' }
    },
    {
      path: '/mana',
      name: 'mana',
      component: () => import('@/views/Mana/Mana.vue'),
      meta: { title: '管理' }
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/404'
    }
  ]
});

// **删除这里原有的 axios.defaults.baseURL 和 triggerWechatLogin 函数定义**
// 因为它们已经分别被 apiClient 封装和移动到 authUtils.ts

router.beforeEach(async (to, from, next) => {
  const paymentStore = usePaymentStore();
  document.title = (to.meta?.title as string) ?? '自助功能';
  const urlStore = useUrlStore()
  
  // 构建完整URL（包含origin）
  const fullUrl = `${window.location.origin}${to.fullPath}`
  urlStore.updateCurrentUrl(fullUrl)
  // 允许访问的白名单路由
  const publicRoutes = ['/home','/reopen', '/auth-success', '/404', '/payment' ,'/chat','/userCenter','/profile-setup'];
  
  if (publicRoutes.includes(to.path)) {
    return next();
  }

  const authStore = useAuthStore();
  if (!authStore.token) {
    const isWechat = /micromessenger/i.test(navigator.userAgent);
    
    if (!isWechat) {
      next({ path: '/reopen', replace: true });
    } else {
      // 保存当前路由作为"上一个路由"（可选，取决于你的路由历史逻辑）
      setPreviousRoute(from);
      // 调用从 authUtils.ts 导入的微信登录函数
      triggerWechatLogin();
      // 在此情况下不调用 next()，因为页面会直接重定向，防止死循环或重复导航
    }
  } 
  else {
    const requiresPayment = !publicRoutes.includes(to.path);
    
    if (requiresPayment) {
      // 如果支付状态尚未加载，先加载
      if (!paymentStore.isPaid && !paymentStore.loading) {
        await paymentStore.checkPaymentStatus();
      }
      
      // 如果未支付，重定向到支付页面
      if (!paymentStore.isPaid) {
        return next({ path: '/payment', replace: true });
      }
    }
    next();
  }
});

// 全局后置守卫记录路由历史
router.afterEach((to, from) => {
  // ... (保持不变)
  const excludeRoutes = ['/auth-success', '/reopen', '/404'];
  
  if (excludeRoutes.includes(from.path) || from.path === '/') {
    return;
  }
  setPreviousRoute(from);
});

export default router;