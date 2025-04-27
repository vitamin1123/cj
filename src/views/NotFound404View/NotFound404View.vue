<template>
  <div class="not-found-container">
    <div class="animation-container">
      <div class="error-code">404</div>
      <div class="error-message">页面不存在</div>
      <div class="error-description">
        您访问的页面可能已被删除、暂时不可用或地址输入错误
      </div>
      <t-button theme="primary" @click="goHome">返回首页</t-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.not-found-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.animation-container {
  text-align: center;
  animation: fadeIn 0.8s ease-in-out;
}

.error-code {
  font-size: 120px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 20px;
  text-shadow: 3px 3px 0 rgba(0, 0, 0, 0.1);
}

.error-message {
  font-size: 24px;
  color: #2c3e50;
  margin-bottom: 10px;
}

.error-description {
  font-size: 16px;
  color: #7f8c8d;
  margin-bottom: 30px;
  max-width: 500px;
  line-height: 1.6;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
  