import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from '@/App.vue'
import router from '@/router'
import { Lazyload } from 'vant'
import 'vant/lib/index.css';
import 'tdesign-vue-next/es/style/index.css';
import '@/style.css';
// import { vConsolePlugin } from './plugins/vconsole';


const app = createApp(App)
const pinia = createPinia()
app.use(pinia) // 确保 Pinia 先安装

import { useUrlStore } from '@/store/urlStore'
const urlStore = useUrlStore()
// 检测iOS微信环境并缓存初始URL
const isIOSWechat = /iphone|ipad|ipod/i.test(navigator.userAgent) && 
                   /MicroMessenger/i.test(navigator.userAgent)

if (isIOSWechat) {
  urlStore.setIosWechatInitialUrl(window.location.href)
}
// 先创建 Pinia



app.use(router)

app.use(Lazyload, {
    lazyComponent: true  // 关键配置
  })


// app.use(vConsolePlugin); // 注册vConsole插件
app.mount('#app')
