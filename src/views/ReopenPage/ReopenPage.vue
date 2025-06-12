<template>
  <div class="reopen-container">
    <div class="content">
      <div class="icon-container">
        <div class="wechat-icon">
          <svg viewBox="0 0 1024 1024" width="80" height="80">
            <path d="M331.5 235.5c-31.2 0-52 20.8-52 46.8s20.8 46.8 52 46.8 52-20.8 52-46.8-20.8-46.8-52-46.8z m0 0M235.5 235.5c-31.2 0-52 20.8-52 46.8s20.8 46.8 52 46.8 52-20.8 52-46.8-20.8-46.8-52-46.8z m0 0" fill="#07C160"/>
            <path d="M283.5 0C127.1 0 0 101.4 0 226.7c0 72.8 37.4 138.1 95.9 180.8L78 512l109.4-54.7c31.2 6.2 56.2 12.4 87.4 12.4 7.3 0 14.5-0.4 21.6-1.1-4.5-15.5-7.1-31.8-7.1-48.7 0-108.1 93.1-195.6 208-195.6 11.2 0 22.1 0.9 32.8 2.5C503.9 98.1 401.6 0 283.5 0z m0 0" fill="#07C160"/>
            <path d="M1024 389.9c0-108.1-108.1-195.6-239.9-195.6S544.2 281.8 544.2 389.9s108.1 195.6 239.9 195.6c24.9 0 49.9-6.2 74.8-12.4L967 627.8l-18.7-93.4c49.9-37.4 75.7-87.4 75.7-144.5z m-319.8-46.8c-18.7 0-37.4-18.7-37.4-37.4s18.7-37.4 37.4-37.4 37.4 18.7 37.4 37.4-18.7 37.4-37.4 37.4z m159.9 0c-18.7 0-37.4-18.7-37.4-37.4s18.7-37.4 37.4-37.4 37.4 18.7 37.4 37.4-18.7 37.4-37.4 37.4z m0 0" fill="#07C160"/>
          </svg>
        </div>
      </div>
      
      <h1 class="title">请在微信中打开</h1>
      
      <p class="description">
        为了获得最佳体验，请在微信中重新打开此页面
      </p>
      
      <div class="steps">
        <div class="step">
          <div class="step-number">1</div>
          <div class="step-text">复制当前页面链接</div>
        </div>
        <div class="step">
          <div class="step-number">2</div>
          <div class="step-text">在微信中粘贴并打开</div>
        </div>
        <div class="step">
          <div class="step-number">3</div>
          <div class="step-text">享受完整功能体验</div>
        </div>
      </div>
      
      <button class="copy-btn" @click="copyLink">
        <span v-if="!copied">复制链接</span>
        <span v-else class="copied">✓ 已复制</span>
      </button>
      
      <div class="qr-hint">
        <p>或者扫描二维码在微信中打开</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Toast } from 'vant'

const copied = ref(false)

const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(window.location.href)
    copied.value = true
    Toast.success('链接已复制到剪贴板')
    
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    // 降级方案
    const textArea = document.createElement('textarea')
    textArea.value = window.location.href
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    
    copied.value = true
    Toast.success('链接已复制到剪贴板')
    
    setTimeout(() => {
      copied.value = false
    }, 2000)
  }
}
</script>

<style scoped>
.reopen-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

.content {
  background: white;
  border-radius: 20px;
  padding: 40px 30px;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  width: 100%;
}

.icon-container {
  margin-bottom: 30px;
}

.wechat-icon {
  display: inline-block;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 50%;
  box-shadow: 0 8px 25px rgba(7, 193, 96, 0.15);
}

.title {
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 15px 0;
}

.description {
  font-size: 16px;
  color: #7f8c8d;
  line-height: 1.6;
  margin: 0 0 40px 0;
}

.steps {
  margin-bottom: 40px;
}

.step {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  text-align: left;
}

.step-number {
  width: 32px;
  height: 32px;
  background: #07C160;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  margin-right: 15px;
  flex-shrink: 0;
}

.step-text {
  font-size: 15px;
  color: #34495e;
  line-height: 1.4;
}

.copy-btn {
  width: 100%;
  padding: 15px;
  background: #07C160;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 30px;
}

.copy-btn:hover {
  background: #06ad56;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(7, 193, 96, 0.3);
}

.copy-btn:active {
  transform: translateY(0);
}

.copied {
  color: #fff;
}

.qr-hint {
  padding-top: 20px;
  border-top: 1px solid #ecf0f1;
}

.qr-hint p {
  font-size: 14px;
  color: #95a5a6;
  margin: 0;
}

@media (max-width: 480px) {
  .content {
    padding: 30px 20px;
  }
  
  .title {
    font-size: 24px;
  }
  
  .description {
    font-size: 15px;
  }
}
</style>