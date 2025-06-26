// src/utils/authUtils.ts

// 从环境变量获取配置，确保生产环境和开发环境的灵活性
// 请确保你的 .env 文件中定义了这些变量
// 例如：VITE_WECHAT_APP_ID=wxccbf0238cab0a75c, VITE_API_BASE_URL=http://www.tianshunchenjie.com
const appId = import.meta.env.VITE_WECHAT_APP_ID;
const backendUrl = import.meta.env.VITE_API_BASE_URL;

/**
 * 触发微信网页授权登录流程。
 * 该函数会重定向浏览器到微信授权页面。
 */
export const triggerWechatLogin = () => {
  // 对回调 URI 进行编码
  const redirectUri = encodeURIComponent(`${backendUrl}/api/wechat/callback`);
  // 生成一个随机的 state 参数，用于防止 CSRF 攻击
  const state = 'STATE_' + Date.now() + '_' + Math.random().toString(36).substr(2, 8);

  // 构建微信 OAuth 授权 URL
  const authUrl = `https://open.weixin.qq.com/connect/oauth2/authorize?appid=${appId}&redirect_uri=${redirectUri}&response_type=code&scope=snsapi_base&state=${state}#wechat_redirect`;

  console.log('重定向到微信 OAuth:', authUrl);
  // 执行页面重定向
  window.location.href = authUrl;
};