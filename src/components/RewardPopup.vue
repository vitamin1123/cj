<!-- src/components/RewardPopup.vue -->
<template>
  <van-popup
    v-model:show="show"
    position="bottom"
    round
    closeable
    close-icon="close"
    :style="{ height: 'auto', maxHeight: '85vh' }"
    class="reward-popup"
  >
    <div class="reward-popup-container">
      <!-- 标题 -->
      <div class="popup-header">
        <h2 class="popup-title">支持红娘工作</h2>
        <p class="popup-subtitle">感谢您的每一份支持 ❤️</p>
      </div>

      <!-- 输入区域 -->
      <div class="input-section">
        <div class="input-group">
          <label class="input-label">附言祝福</label>
          <div class="input-wrapper">
            <van-field
              v-model="blessing"
              placeholder="给红娘的暖心话..."
              maxlength="30"
              class="blessing-input"
            />
            <van-button 
              class="random-btn" 
              size="small" 
              @click="randomBlessing"
              :disabled="loading"
            >
              <van-icon name="replay" />
            </van-button>
          </div>
        </div>

        <div class="input-group">
          <label class="input-label">打赏金额</label>
          <div class="input-wrapper">
            <van-field
              v-model="customAmount"
              type="number"
              placeholder="0.00"
              maxlength="8"
              class="amount-input"
              :formatter="amountFormatter"
            >
              <template #left-icon>
                <span class="currency">¥</span>
              </template>
            </van-field>
            <van-button 
              class="random-btn" 
              size="small" 
              @click="randomAmount"
              :disabled="loading"
            >
              <van-icon name="after-sale" />
            </van-button>
          </div>
        </div>
      </div>

      <!-- 固定金额选项 -->
      <div class="preset-amounts">
        <div class="section-title">快速选择</div>
        <div class="amount-grid">
          <div
            v-for="amount in presetAmounts"
            :key="amount"
            class="amount-card"
            :class="{ active: selectedAmount === amount }"
            @click="selectAmount(amount)"
          >
            <div class="amount-value">¥{{ amount }}</div>
            <div class="amount-desc">{{ getAmountDesc(amount) }}</div>
          </div>
        </div>
      </div>

      <!-- 确认按钮 -->
      <div class="action-section">
        <van-button
          type="primary"
          block
          round
          size="large"
          class="confirm-btn"
          :disabled="!finalAmount || loading"
          @click="handleReward"
        >
          <template v-if="loading">
            <van-loading size="20" />
            处理中...
          </template>
          <template v-else>
            确认打赏 ¥{{ finalAmount }}
          </template>
        </van-button>
      </div>

      <!-- 历史记录 -->
      <div class="history-section" v-if="totalTips > 0">
        <div class="history-title">
          <van-icon name="gift" />
          已累计支持 ¥{{ totalTips.toFixed(2) }}
        </div>
      </div>
    </div>
  </van-popup>

  <!-- 支付成功提示 -->
  <van-overlay :show="showSuccess" @click="showSuccess = false">
    <div class="success-wrapper">
      <div class="success-card">
        <div class="success-icon">🎉</div>
        <div class="success-text">打赏成功！</div>
        <div class="success-sub">感谢您对红娘工作的支持</div>
      </div>
    </div>
  </van-overlay>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { showToast } from 'vant';
import apiClient from '@/plugins/axios';
import wx from 'weixin-js-sdk';
const sdkReady = ref(false); 
const sdkInitStarted = ref(false);
const props = defineProps<{
  modelValue: boolean;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: boolean];
}>();

// 数据
const loading = ref(false);
const showSuccess = ref(false);
const blessing = ref('');
const customAmount = ref('');
const selectedAmount = ref<number | null>(null);
const totalTips = ref(0);

const presetAmounts = [20, 50, 100, 200, 500, 1000, 2000, 5000];

const luckyAmounts = [
  { amount: 6.66, blessing: '六六大顺，红娘辛苦啦！' },
  { amount: 8.88, blessing: '发发发，感谢红娘牵红线！' },
  { amount: 16.66, blessing: '一路顺风，红娘最棒！' },
  { amount: 18.88, blessing: '要发发发，红娘真伟大！' },
  { amount: 66.6, blessing: '顺顺顺，红娘最贴心！' },
  { amount: 88.8, blessing: '发发发，红娘顶呱呱！' },
  { amount: 168, blessing: '一路发，红娘辛苦啦！' },
  { amount: 188, blessing: '要发发，感谢红娘牵线！' },
  { amount: 666, blessing: '六六大顺，红娘最用心！' },
  { amount: 888, blessing: '发发发，红娘辛苦啦！' },
  { amount: 1314, blessing: '一生一世，感谢红娘！' },
  { amount: 520, blessing: '我爱你，红娘辛苦了！' }
];

// 计算属性
const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
});

const finalAmount = computed(() => {
  if (selectedAmount.value) return selectedAmount.value;
  const amount = parseFloat(customAmount.value) || 0;
  return Math.round(amount * 100) / 100; // 保留两位小数
});

// 方法
const amountFormatter = (value: string) => {
  // 只允许数字和小数点
  const filtered = value.replace(/[^\d.]/g, '');
  
  // 限制只能有一个小数点
  const parts = filtered.split('.');
  if (parts.length > 2) {
    return parts[0] + '.' + parts.slice(1).join('');
  }
  
  // 限制小数位数
  if (parts[1] && parts[1].length > 2) {
    return parts[0] + '.' + parts[1].slice(0, 2);
  }
  
  return filtered;
};

const randomBlessing = () => {
  const randomItem = luckyAmounts[Math.floor(Math.random() * luckyAmounts.length)];
  blessing.value = randomItem.blessing;
};

const randomAmount = () => {
  const randomItem = luckyAmounts[Math.floor(Math.random() * luckyAmounts.length)];
  customAmount.value = randomItem.amount.toString();
  blessing.value = randomItem.blessing;
  selectedAmount.value = null;
};

const selectAmount = (amount: number) => {
  selectedAmount.value = amount;
  customAmount.value = '';
  if (!blessing.value) {
    blessing.value = getAmountDesc(amount);
  }
};

const getAmountDesc = (amount: number) => {
  const descMap: Record<number, string> = {
    20: '小小谢意',
    50: '心意满满',
    100: '感谢支持',
    200: '鼎力相助',
    500: '深情厚谊',
    1000: '万分感谢',
    2000: '感恩戴德',
    5000: '恩情似海'
  };
  return descMap[amount] || '感谢支持';
};

const loadTotalTips = async () => {
  try {
    const response = await apiClient.get('/tip/total');
    totalTips.value = response.data.total;
  } catch (error) {
    console.error('获取打赏总额失败:', error);
  }
};

const handleReward = async () => {
  if (!sdkReady.value) {
    if (!sdkInitStarted.value) {
      sdkInitStarted.value = true;
      await initWechatSDK();
    }
    showToast('微信支付环境初始化中，请稍候');
    return;
  }
  if (!finalAmount.value || finalAmount.value <= 0) {
    showToast('请输入有效的打赏金额');
    return;
  }
if (!sdkReady.value) {
    alert('微信支付环境未准备好，请稍后重试');
    return;
  }
  

  loading.value = true;

  try {
    const response = await apiClient.post('/api/create-tip-payment', {
      amount: finalAmount.value,
      message: blessing.value || '感谢红娘'
    });

    const paymentParams = response.data;

    wx.chooseWXPay({
      timestamp: paymentParams.timeStamp,
      nonceStr: paymentParams.nonceStr,
      package: paymentParams.package,
      signType: paymentParams.signType,
      paySign: paymentParams.paySign,
      success: () => {
        showSuccess.value = true;
        loadTotalTips();
        setTimeout(() => {
          showSuccess.value = false;
          show.value = false;
        }, 1500);
      },
      fail: (res: any) => {
        showToast(`支付失败: ${res.errMsg || '未知错误'}`);
      },
      cancel: () => {
        showToast('已取消支付');
      },
      complete: () => {
        loading.value = false;
      }
    });
  } catch (error: any) {
    showToast(`打赏失败: ${error.response?.data?.detail || '未知错误'}`);
    loading.value = false;
  }
};

// 监听弹窗打开
watch(() => show.value, (newVal) => {
  if (newVal) {
    loadTotalTips();
    // 自动填充随机祝福
    if (!blessing.value) {
      randomBlessing();
    }
  }
});

// 监听金额变化，清除选中状态
watch(customAmount, () => {
  if (customAmount.value) {
    selectedAmount.value = null;
  }
});

const initWechatSDK = async () => {
  if (sdkReady.value || sdkInitStarted.value) return;
  sdkInitStarted.value = true;

  try {
    const url = window.location.href.split('#')[0];
    const configResponse = await apiClient.get('/api/wechat/jssdk-signature', {
      params: { url }
    });

    const configData = configResponse.data;

    wx.config({
      debug: false,
      appId: configData.appId,
      timestamp: configData.timestamp,
      nonceStr: configData.nonceStr,
      signature: configData.signature,
      jsApiList: ['chooseWXPay']
    });

    wx.ready(() => {
      sdkReady.value = true;
      console.log('微信JS-SDK初始化完成');
    });

    wx.error((res: any) => {
      console.error('微信JS-SDK配置失败:', res);
      showToast('微信支付初始化失败，请重试');
    });
  } catch (error) {
    console.error('初始化失败:', error);
    showToast('微信支付初始化失败，请重试');
  }
};

// onMounted(() => {
//   initWechatSDK();
// });

</script>

<style scoped>
.reward-popup {
  background: #F2EEE8;
}

.reward-popup-container {
  padding: 20px;
  background: #F2EEE8;
  min-height: 400px;
}

.popup-header {
  text-align: center;
  margin-bottom: 30px;
}

.popup-title {
  font-size: 22px;
  color: #6A6A6A;
  margin: 0 0 8px 0;
  font-weight: bold;
}

.popup-subtitle {
  font-size: 14px;
  color: #999;
  margin: 0;
}

.input-section {
  margin-bottom: 25px;
}

.input-group {
  margin-bottom: 20px;
}

.input-label {
  display: block;
  font-size: 14px;
  color: #6A6A6A;
  margin-bottom: 8px;
  font-weight: 500;
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

.blessing-input,
.amount-input {
  flex: 1;
  background: white;
  border: 1px solid #D9D9D9;
  border-radius: 8px;
  padding: 12px 15px;
  font-size: 16px;
}

.currency {
  color: #ff6b6b;
  font-weight: bold;
  margin-right: 5px;
}

.random-btn {
  background: #EBE3D7;
  border: 1px solid #D9D9D9;
  color: #6A6A6A;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}

.preset-amounts {
  margin-bottom: 30px;
}

.section-title {
  font-size: 16px;
  color: #6A6A6A;
  margin-bottom: 15px;
  font-weight: 500;
}

.amount-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.amount-card {
  background: white;
  border: 1px solid #D9D9D9;
  border-radius: 8px;
  padding: 15px 5px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.amount-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.amount-card.active {
  background: #ff6b6b;
  border-color: #ff6b6b;
  color: white;
}

.amount-value {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 4px;
}

.amount-desc {
  font-size: 12px;
  opacity: 0.8;
}

.action-section {
  margin-bottom: 20px;
}

.confirm-btn {
  background: linear-gradient(135deg, #ff6b6b, #ff4d4f);
  border: none;
  font-size: 18px;
  font-weight: bold;
  height: 50px;
}

.history-section {
  text-align: center;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
}

.history-title {
  font-size: 14px;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.success-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
}

.success-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  animation: bounce-in 0.3s;
}

.success-icon {
  font-size: 60px;
  margin-bottom: 15px;
}

.success-text {
  font-size: 20px;
  color: #333;
  margin-bottom: 8px;
  font-weight: bold;
}

.success-sub {
  font-size: 14px;
  color: #666;
}

@keyframes bounce-in {
  0% {
    transform: scale(0.8);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>