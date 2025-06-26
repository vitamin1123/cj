import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from '@/App.vue'
import router from '@/router'
import { Lazyload } from 'vant'
import 'vant/lib/index.css';
import 'tdesign-vue-next/es/style/index.css';
import '@/style.css';

const app = createApp(App)

// 先创建 Pinia
const pinia = createPinia()
app.use(pinia) // 确保 Pinia 先安装

app.use(router)

app.use(Lazyload, {
    lazyComponent: true  // 关键配置
  })



app.mount('#app')
