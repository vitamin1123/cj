<!-- src/views/Payment/Payment.vue -->
<template>
  <div class="payment-container">
    <van-floating-bubble
      v-model:offset="offset"
      axis="xy"
      magnetic="x"
      icon="revoke"
      :size="54"
      :gap="10"
      @click="goBack"
      style="--van-floating-bubble-background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);"
    />
    <div class="payment-content">
      <h1>开通会员，解锁全部功能</h1>
      <p>支付200元即可享受1年完整会员服务</p>
      
      <div class="price-display">
        <span class="amount">¥200</span>
        <span class="duration">/年</span>
      </div>
      
      <div class="benefits">
        <div v-for="(benefit, index) in benefits" :key="index" class="benefit">
          <span class="checkmark">✓</span> {{ benefit }}
        </div>
      </div>
      
      <button 
        class="payment-button"
        @click="handlePayment"
        :disabled="loading"
      >
        {{ loading ? '支付处理中...' : '立即支付' }}
      </button>
      
      
      
      <!-- <div class="footer">
        <p>支付即表同意<a href="/terms">服务条款</a>和<a href="/privacy">隐私政策</a></p>
      </div> -->
    </div>
    
    <div v-if="showSuccess" class="success-overlay">
      <div class="success-content">
        <div class="success-icon">✓</div>
        <h2>支付成功！</h2>
        <p>您已成功开通会员服务</p>
        <button @click="goToHome">返回首页</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/plugins/axios'
import wx from 'weixin-js-sdk'; // 使用安装的微信JS-SDK包
import { usePaymentStore } from '@/store/paymentStore';

const router = useRouter();
const paymentStore = usePaymentStore();
const loading = ref(false);
const showSuccess = ref(false);
const sdkReady = ref(false); // 跟踪SDK是否已初始化
const offset = ref({ x: 0.05 * window.innerWidth, y: 0.03 * window.innerHeight });
const goBack = () => {

    router.replace('/home');

};
const benefits = [
  '无限制查看用户资料',
  '查看访客记录',
  '高级匹配功能',
  '专属客服支持',
];

// 初始化微信JS-SDK
const initWechatSDK = async () => {
  try {
    // 1. 获取当前页面的URL（去掉#后面的部分）
    const url = window.location.href.split('#')[0];
    
    // 2. 从后端获取JS-SDK配置
    const configResponse = await apiClient.get('/api/wechat/jssdk-signature', {
      params: { url }
    });
    
    const configData = configResponse.data;
    
    // 3. 配置微信JS-SDK
    wx.config({
      debug: false, // 生产环境关闭调试
      appId: configData.appId,
      timestamp: configData.timestamp,
      nonceStr: configData.nonceStr,
      signature: configData.signature,
      jsApiList: ['chooseWXPay'] // 只需要支付API
    });
    
    // 4. 验证配置
    wx.ready(() => {
      sdkReady.value = true;
      console.log('微信JS-SDK初始化完成');
    });
    
    wx.error((res: any) => {
      console.error('微信JS-SDK配置失败:', res);
      alert('微信支付环境初始化失败，请刷新页面重试');
    });
  } catch (error) {
    console.error('初始化微信JS-SDK失败:', error);
    alert('初始化微信支付失败，请重试');
  }
};

const handlePayment = async () => {
  if (!sdkReady.value) {
    alert('微信支付环境未准备好，请稍后重试');
    return;
  }
  
  loading.value = true;
  
  try {
    // 1. 从后端获取支付参数
    const response = await apiClient.post('/api/create-payment', {
      amount: 1, // 金额单位：分（200元 = 20000分）
      description: '开通一年会员服务'
    });
    const paymentParams = response.data;
    
    // 2. 调用微信支付
    wx.chooseWXPay({
      timestamp: paymentParams.timeStamp,
      nonceStr: paymentParams.nonceStr,
      package: paymentParams.package,
      signType: paymentParams.signType,
      paySign: paymentParams.paySign,
      success: async() => {
        // 支付成功
        showSuccess.value = true;
        loading.value = false;
        
        // 更新支付状态
        paymentStore.setPaymentStatus(true);
        const statusRes = await apiClient.get('/api/check-payment');
          if (statusRes.data.is_paid) {
            console.log('支付状态验证成功');
          }
        // 可选：显示成功状态几秒后自动跳转
        setTimeout(() => {
          goToHome();
        }, 10000);
      },
      fail: (res: any) => {
        // 支付失败
        console.error('支付失败:', res);
        alert(`支付失败: ${res.errMsg || '未知错误'}`);
        loading.value = false;
      },
      cancel: () => {
        // 用户取消支付
        alert('您已取消支付');
        loading.value = false;
      }
    });
  } catch (error: any) {
    console.error('支付请求失败:', error);
    alert(`支付失败: ${error.response?.data?.message || error.message || '未知错误'}`);
    loading.value = false;
  }
};

const goToHome = () => {
  router.replace('/home');
};

// 组件挂载时初始化微信SDK
onMounted(() => {
  initWechatSDK();
});
</script>

<style scoped>
.payment-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
  position: relative;
}

.payment-content {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 500px;
  width: 100%;
  z-index: 1;
}

h1 {
  color: #333;
  margin-bottom: 10px;
  font-size: 24px;
  font-weight: bold;
}

p {
  color: #666;
  margin-bottom: 30px;
  font-size: 16px;
}

.price-display {
  margin: 25px 0;
}

.amount {
  font-size: 42px;
  font-weight: bold;
  color: #ff4d4f;
}

.duration {
  font-size: 16px;
  color: #999;
  margin-left: 5px;
}

.benefits {
  margin: 30px 0;
  text-align: left;
}

.benefit {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
  font-size: 16px;
}

.checkmark {
  color: #07c160;
  margin-right: 10px;
  font-weight: bold;
  font-size: 18px;
}

.payment-button {
  background: linear-gradient(135deg, #ff6b6b, #ff4d4f);
  color: white;
  border: none;
  border-radius: 50px;
  padding: 16px 40px;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  margin: 20px 0;
  width: 100%;
  box-shadow: 0 4px 10px rgba(255, 77, 79, 0.3);
}

.payment-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(255, 77, 79, 0.4);
}

.payment-button:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.payment-methods {
  margin: 25px 0;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 10px;
}

.method {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.method.active {
  border-color: #07c160;
  background-color: rgba(7, 193, 96, 0.05);
}

.method img {
  width: 30px;
  height: 30px;
  margin-right: 10px;
}

.method span {
  font-size: 16px;
  color: #333;
}

.footer {
  font-size: 14px;
  color: #999;
  margin-top: 20px;
}

.footer a {
  color: #2575fc;
  text-decoration: none;
  margin: 0 5px;
}

/* 支付成功覆盖层 */
.success-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
}

.success-content {
  background: white;
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  max-width: 400px;
  width: 90%;
}

.success-icon {
  width: 80px;
  height: 80px;
  background: #07c160;
  color: white;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 40px;
  margin: 0 auto 20px;
}

.success-content h2 {
  color: #333;
  margin-bottom: 10px;
}

.success-content p {
  color: #666;
  margin-bottom: 30px;
}

.success-content button {
  background: #07c160;
  color: white;
  border: none;
  border-radius: 50px;
  padding: 12px 30px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}
</style>