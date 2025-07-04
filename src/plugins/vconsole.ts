// src/plugins/vconsole.ts
import type { App } from 'vue'; // 使用import type导入类型
import VConsole from 'vconsole';

// // 根据环境变量控制是否启用vConsole
// const enableVConsole = import.meta.env.MODE === 'development' || 
//                      (window as any).__DEV__; // 或自定义标志

export const vConsolePlugin = {
  install(app: App) { // App仅作为类型使用
    if (true) {
      const vConsole = new VConsole();
      app.config.globalProperties.$vconsole = vConsole;
      console.log('vConsole initialized');
    }
  },
};