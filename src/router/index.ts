// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import Result404 from '@/views/NotFound404View/NotFound404View.vue'

import IndexView from '@/views/IndexView/IndexView.vue'
import HomeView from '@/views/Home/Home.vue'
import userCenterView from '@/views/userCenter/userCenter.vue'
import { useAuthStore } from '@/store/authStore'
import DetailView from '@/views/Detail/Detail.vue'
import ExploreView from '@/views/Explore/Explore.vue'
import LikesView from '@/views/Likes/Likes.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [

    {
      path: '/404',
      name: '404',
      component: Result404,
      meta: {
        title: '404' // 自定义标题
      }
    },
    
  
    
    {
      path: '/',
      name: 'index',
      component: IndexView,
      meta: {
        title: '首页' // 自定义标题
      }
    },
    {
      path: '/home',
      name: 'home',
      component: HomeView,
      meta: {
        title: '扉页' // 自定义标题
      }
    },
    {
      path: '/userCenter',
      name: 'userCenter',
      component: userCenterView,
      meta: {
        title: '个人中心' // 自定义标题
      }
    },
    // HomeView
    // 在routes数组中添加新路由
    {
      path: '/detail/:id',
      name: 'detail',
      component: DetailView,
      meta: {
        title: '详细信息'
      }
    },
    {
      path: '/explore',
      name: 'explore',
      component: ExploreView,
      meta: {
        title: '寻觅'
      }
    },
    {
      path: '/likes',
      name: 'likes',
      component: LikesView,
      meta: {
        title: '喜欢'
      }
    }
  ],
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // document.title = to.meta.title || '自助功能'
  document.title = (to.meta?.title as string) ?? '自助功能'
  const authStore = useAuthStore()

  // 从 URL 中提取 token 参数
  const tokenFromQuery = Array.isArray(to.query.token) ? to.query.token[0] : to.query.token

  // 如果 URL 中有 token 并且 authStore 没有保存 token，则存储 token 并移除 URL 中的 token 参数
  if (tokenFromQuery && tokenFromQuery !== authStore.token) {
    authStore.setToken(tokenFromQuery)

    // 移除 token 参数
    const { token, ...queryWithoutToken } = to.query
    return next({ path: to.path, query: queryWithoutToken, replace: true })
  }

  // 如果没有 token 并且 authStore 中也没有 token，重定向到 404
  // if (!tokenFromQuery && !authStore.token) {
  //   console.log('确实没有token')
  //   if (to.path === '/login' || to.path === '/404') {
  //     return next()
  //   }
  //   // return next({ path: '/404' })
  //   // 根据 vismem 参数判断跳转方向
  //   if (to.path === '/vismem') {
  //     return next({ path: '/404' })
  //   } else {
  //     return next({ path: '/login' })
  //   }
  // }

  next()
})

// router.beforeEach((to, from, next) => {
//   const authStore = useAuthStore()

//   // 从 URL 中获取 token，并确保它是 string 类型
//   const token_tp = Array.isArray(to.query.token) ? to.query.token[0] : to.query.token
//   console.log("看看有没有token", token_tp, authStore.token,token_tp!==authStore.token)

//   // 如果 URL 中没有 token 并且 authStore 也没有 token，重定向到 /404
//   if (!token_tp && !authStore.token && to.path !== '/404') {
//     return next({ path: '/404' })
//   }

//   // 如果 URL 中有 token 且 authStore 中没有存储 token，则进行 token 处理
//   if (typeof token_tp === 'string' && token_tp && (!authStore.token || token_tp!== authStore.token)) {
//     authStore.setToken(token_tp)
//     console.log('authStore写入成功')

//     // 移除 URL 中的 token 参数，避免暴露
//     const { token , ...queryWithoutToken } = to.query

//     return next({ ...to, query: queryWithoutToken, replace: true })
//   }

//   // 如果 URL 没有 token，但 authStore 已经有 token，则直接放行
//   next()
// })




export default router
