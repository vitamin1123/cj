// src/plugins/axios.ts
import axios from 'axios';
import { useAuthStore } from '@/store/authStore';
// 直接导入路由实例，而不是 useRouter 钩子，因为这里不是 Vue 组件环境
import router from '@/router'; 
// 导入我们新创建的微信授权工具函数
import { triggerWechatLogin } from '@/utils/authUtils'; 

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL, // 替换为你的 API 基础 URL
  timeout: 30000,
});

// 请求拦截器：在每个请求中附加 Token
apiClient.interceptors.request.use(
  async (config) => {
    const authStore = useAuthStore();
    const token = authStore.token;

    if (token) {
      // 推荐：移除 encodeURIComponent。JWT 通常是 Base64 编码，本身就是 URL 安全的。
      // 除非后端有特殊要求，否则不应再次编码。
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 新增响应拦截器：处理 Token 失效
apiClient.interceptors.response.use(
  (response) => response, // 成功响应直接返回
  async (error) => {
    const { status, data } = error.response || {};
    console.log('Axios 响应拦截器捕获错误: ', status, data);

    // **关键修改点：检查 403 错误及后端返回的特定错误信息**
    // 确保这里的 `data?.detail` 与你的 `server.py` 中 HTTPException 的 `detail` 字段完全匹配
    if (status === 403 && (data?.detail === "Token 已过期" || data?.detail === "无效的 Token")) {
      const authStore = useAuthStore();

      console.error('API 错误：Token 已过期或无效，尝试重新认证。');

      // 1. 清除本地存储中所有与认证相关的过期数据
      authStore.clearToken();
      authStore.clearUserCode(); // 清除 userCode，如果它也是认证的一部分

      // 2. 判断当前环境是否为微信内置浏览器
      const isWechat = /micromessenger/i.test(navigator.userAgent);

      if (isWechat) {
        // 3. 在微信环境中，触发微信 OAuth 认证流程（会进行页面重定向）
        triggerWechatLogin();
        
        // 返回一个永远不会 resolve/reject 的 Promise，以中断当前请求的错误传播链
        // 因为页面会立即重定向，后续的错误处理不再有意义
        return new Promise(() => {});
      } else {
        // 4. 对于非微信环境（如在浏览器直接访问或开发者工具中），重定向到提示页
        // 建议重定向到 `/reopen` 页面，因为它专门用于提示用户在微信中打开
        router.replace('/reopen');

        // 可以返回一个已解决的 Promise 来停止错误传播，或返回原始错误
        // 这里返回 Promise.resolve() 表示我们已经处理了错误，不需要下游继续捕获
        return Promise.resolve(); 
      }
    }

    // 如果不是 Token 过期/无效的 403 错误，则将错误继续抛出，让其他地方处理
    return Promise.reject(error);
  }
);

export default apiClient;