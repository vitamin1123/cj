<template>
  <div class="profile-setup-container">
    <!-- 顶部进度条 -->
    <div class="progress-container">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: `${(currentStep / totalSteps) * 100}%` }"></div>
      </div>
      <div class="progress-text">{{ currentStep }}/{{ totalSteps }}</div>
    </div>

    <!-- 卡片容器 -->
    <van-swipe 
      class="setup-swipe" 
      :loop="false" 
      :show-indicators="false"
      :touchable="false"
      :vertical="false"
      :stop-propagation="true" 
      :prevent-default="true" 
      ref="swipeRef"
    >
      <!-- 性别选择 -->
      <van-swipe-item>
        <div class="setup-card">
          <div class="card-icon">👤</div>
          <h2 class="card-title">选择性别</h2>
          <p class="card-subtitle">让我们更好地了解你</p>
          <div class="gender-options">
            <div 
              class="gender-option" 
              :class="{ active: formData.gender === 'male' }"
              @click="formData.gender = 'male'"
            >
              <div class="gender-icon">👨</div>
              <span>男生</span>
            </div>
            <div 
              class="gender-option" 
              :class="{ active: formData.gender === 'female' }"
              @click="formData.gender = 'female'"
            >
              <div class="gender-icon">👩</div>
              <span>女生</span>
            </div>
          </div>
        </div>
      </van-swipe-item>

      <!-- 出生日期和时间 -->
      <van-swipe-item>
        <div class="setup-card">
          <div class="card-icon">🎂</div>
          <h2 class="card-title">出生信息</h2>
          <p class="card-subtitle">告诉我们你的生日和出生时间</p>
          
          <!-- 历法选择 -->
          <div class="calendar-type-selector">
            <button 
              class="calendar-type-btn" 
              :class="{ active: calendarType === 'solar' }"
              @click="toggleCalendar('solar')"
            >
              公历
            </button>
            <button 
              class="calendar-type-btn" 
              :class="{ active: calendarType === 'lunar' }"
              @click="toggleCalendar('lunar')"
            >
              农历
            </button>
          </div>
          
          <!-- 日期时间选择 -->
          <div class="date-time-container">
            <!-- 日期选择 -->
            <div class="date-section">
              <label class="section-label">出生日期</label>
              
              <!-- 自定义日历弹窗 -->
              <van-popup v-model:show="showDatePicker" position="bottom" :style="{ height: '70%' }">
                <div class="custom-calendar-container">
                  <!-- 日历头部导航 -->
                  <div class="calendar-header">
                    <van-icon name="arrow-left" @click="navigateMonth('prev')" class="nav-arrow" />
                    <div class="header-title">
                      {{ `${currentDate.getFullYear()}年${currentDate.getMonth() + 1}月` }}
                    </div>
                    <van-icon name="arrow" @click="navigateMonth('next')" class="nav-arrow" />
                  </div>
                  
                  <div class="calendar-actions">
                    <button class="today-btn" @click="goToday">回今天</button>
                    <button class="confirm-btn" @click="showDatePicker = false">确定</button>
                  </div>
                  
                  <!-- 日历组件 -->
                  <van-calendar
                    :key="calendarType"
                    :poppable="false"
                    :show-confirm="false"
                    v-model:current-date="currentDate"
                    :formatter="formatter"
                    :min-date="minDate"
                    :max-date="maxDate"
                    @select="onDateConfirm"
                    class="custom-calendar"
                  />
                </div>
              </van-popup>
              
              <button 
                class="btn-secondary date-btn" 
                @click="showDatePicker = true"
              >
                {{ formatDisplayDate }}
                <span class="btn-icon">📅</span>
              </button>
            </div>
            
            <!-- 时间选择 -->
            <div class="time-section">
              <label class="section-label">出生时间</label>
              
              <van-popup v-model:show="showTimePicker" position="bottom">
                <van-time-picker
                  :model-value="[formData.birthTime]"
                  title="选择出生时间"
                  @confirm="onTimeConfirm"
                  @cancel="showTimePicker = false"
                />
              </van-popup>
              
              <button 
                class="btn-secondary time-btn" 
                @click="showTimePicker = true"
              >
                {{ formData.birthTime }}
                <span class="btn-icon">🕐</span>
              </button>
            </div>
          </div>
        </div>
      </van-swipe-item>

      <!-- 身高 -->
      <van-swipe-item>
        <div class="setup-card">
          <div class="card-icon">📏</div>
          <h2 class="card-title">身高</h2>
          <p class="card-subtitle">请输入你的身高</p>
          <div class="input-container">
            <van-field
              v-model="formData.height"
              type="number"
              label="身高"
              :maxlength="3"
              :min="120"
              :max="240"
              input-align="center"
              :formatter="heightFormatter"
              :rules="[{ required: true, message: '请输入身高' }, { validator: heightValidator, message: '身高范围120-240cm' }]"
              class="setup-input"
            >
              <template #right-icon>
                <span class="input-unit">cm</span>
              </template>
            </van-field>
          </div>
        </div>
      </van-swipe-item>

      <!-- 体重 -->
      <van-swipe-item>
        <div class="setup-card">
          <div class="card-icon">⚖️</div>
          <h2 class="card-title">体重</h2>
          <p class="card-subtitle">请输入你的体重</p>
          <div class="input-container">
            <van-field
              v-model="formData.weight"
              type="number"
              label="体重"
              input-align="center"
              :max="250"
              :rules="[{ required: true, message: '请输入体重' }, { validator: weightValidator, message: '体重不能超过250kg' }]"
              class="setup-input"
            >
              <template #right-icon>
                <span class="input-unit">kg</span>
              </template>
            </van-field>
          </div>
        </div>
      </van-swipe-item>

      <!-- 地区 -->
      <van-swipe-item>
        <div class="setup-card">
          <div class="card-icon">📍</div>
          <h2 class="card-title">所在地区</h2>
          <p class="card-subtitle">选择你的所在地</p>
          <div class="input-container">
            <van-field
              v-model="formData.region"
              is-link
              readonly
              label="所在地区"
              placeholder="请选择所在地区"
              @click="showAreaPicker = true"
              input-align="center"
              :rules="[{ required: true, message: '请选择所在地区' }]"
            />
          </div>
          
          <!-- Area选择器弹窗 -->
          <van-popup v-model:show="showAreaPicker" position="bottom">
            <van-area
              v-model="formData.regionCode"
              title="选择地区"
              :area-list="areaList"
              @confirm="onAreaConfirm"
              @cancel="showAreaPicker = false"
              :columns-placeholder="['请选择省', '请选择市', '请选择区']"
            />
          </van-popup>
        </div>
      </van-swipe-item>

      <!-- 职业 -->
      <van-swipe-item>
        <div class="setup-card">
          <div class="card-icon">💼</div>
          <h2 class="card-title">职业</h2>
          <p class="card-subtitle">你从事什么工作</p>
          <div class="input-container">
            <van-field
              v-model="formData.occupation"
              label="职业"
              placeholder="请输入职业"
              input-align="center"
              :rules="[{ required: true, message: '请输入职业' }]"
            />
          </div>
        </div>
      </van-swipe-item>

      <!-- 收入 -->
      <van-swipe-item>
        <div class="setup-card">
          <div class="card-icon">💰</div>
          <h2 class="card-title">收入水平</h2>
          <p class="card-subtitle">选择你的收入范围</p>
          <div class="income-options">
            <div 
              v-for="income in incomeOptions"
              :key="income.value"
              class="income-option"
              :class="{ active: formData.income === income.value }"
              @click="formData.income = income.value"
            >
              {{ income.label }}
            </div>
          </div>
        </div>
      </van-swipe-item>

      <!-- 学历 -->
      <van-swipe-item>
        <div class="setup-card">
          <div class="card-icon">🎓</div>
          <h2 class="card-title">学历</h2>
          <p class="card-subtitle">你的教育背景</p>
          <div class="education-options">
            <div 
              v-for="edu in educationOptions"
              :key="edu.value"
              class="education-option"
              :class="{ active: formData.education === edu.value }"
              @click="formData.education = edu.value"
            >
              {{ edu.label }}
            </div>
          </div>
        </div>
      </van-swipe-item>

      <!-- 信仰 -->
      <van-swipe-item>
        <div class="setup-card">
          <div class="card-icon">🙏</div>
          <h2 class="card-title">信仰</h2>
          <p class="card-subtitle">你的宗教信仰</p>
          <div class="input-container">
            <input 
              type="text" 
              v-model="formData.religion" 
              placeholder="请输入信仰（可选）"
              class="setup-input"
            />
          </div>
        </div>
      </van-swipe-item>

      <!-- MBTI -->
      <van-swipe-item>
        <div class="setup-card">
          <div class="card-icon">🧠</div>
          <h2 class="card-title">MBTI人格</h2>
          <p class="card-subtitle">你的人格类型</p>
          <div class="mbti-options">
            <div 
              v-for="mbti in mbtiOptions"
              :key="mbti"
              class="mbti-option"
              :class="{ active: formData.mbti === mbti }"
              @click="formData.mbti = mbti"
            >
              {{ mbti }}
            </div>
          </div>
        </div>
      </van-swipe-item>

      <!-- 简介 -->
      <van-swipe-item>
        <div class="setup-card">
          <div class="card-icon">📝</div>
          <h2 class="card-title">个人简介</h2>
          <p class="card-subtitle">介绍一下自己吧</p>
          <div class="textarea-container">
            <textarea 
              v-model="formData.bio" 
              placeholder="写一段简短的自我介绍..."
              class="setup-textarea"
              maxlength="200"
            ></textarea>
            <div class="char-count">{{ formData.bio.length }}/200</div>
          </div>
        </div>
      </van-swipe-item>

      <!-- 隐私简介 -->
      <van-swipe-item>
        <div class="setup-card">
          <div class="card-icon">🔒</div>
          <h2 class="card-title">隐私简介</h2>
          <p class="card-subtitle">只有陈姐能看到</p>
          <div class="textarea-container">
            <textarea 
              v-model="formData.privateBio" 
              placeholder="写一些更私密的信息..."
              class="setup-textarea"
              maxlength="200"
            ></textarea>
            <div class="char-count">{{ formData.privateBio.length }}/200</div>
          </div>
        </div>
      </van-swipe-item>
    </van-swipe>

    <!-- 底部按钮 -->
    <div class="bottom-actions">
      <button 
        v-if="currentStep > 1" 
        class="btn-secondary" 
        @click="prevStep"
      >
        上一步
      </button>
      <button 
        class="btn-primary" 
        @click="nextStep"
        :disabled="!canProceed"
      >
        {{ currentStep === totalSteps ? '完成' : '下一步' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { Area, Swipe, SwipeItem, DatePicker, TimePicker, Toast, Calendar, Popup, Icon, Field } from 'vant';
import { areaList } from '@vant/area-data';

import { Solar, Lunar } from 'lunar-typescript';

const router = useRouter();
const swipeRef = ref();
const currentStep = ref(1);
const totalSteps = 12;
const showDatePicker = ref(false);
const showTimePicker = ref(false);
const showAreaPicker = ref(false); // New ref for area picker
// 直接使用导入的areaList数据
const calendarType = ref('solar'); // 'solar' 公历, 'lunar' 农历

// 表单数据
const formData = ref({
  gender: '',
  birthDate: new Date(),
  birthTime: '12:00',
  height: '',
  weight: '',
  region: '',
  regionCode: '', // 新增：存储地区码
  occupation: '',
  income: '',
  education: '',
  religion: '',
  mbti: '',
  bio: '',
  privateBio: ''
});

watch(currentStep, (newVal) => {
  // 当currentStep变化时，更新swipe位置
  swipeRef.value?.swipeTo(newVal - 1);
});
// 日期范围
const minDate = new Date(1950, 0, 1);
const maxDate = new Date(2010, 11, 31);
const currentDate = ref(new Date());
const weightValidator = (value: string | number) => {
  return Number(value) <= 250;
};
// 农历日期格式化函数
const formatter = (day: any) => {
  const date = new Date(day.date);
  const solar = Solar.fromDate(date);
  const lunar = solar.getLunar();
  
  // 设置周末样式
  if (date.getDay() === 0 || date.getDay() === 6) {
    day.className = 'weekend-red';
  }
  
  // 显示农历信息
  if (calendarType.value === 'lunar') {
    // 获取农历节日
    const festivals = lunar.getFestivals();
    if (festivals && festivals.length > 0) {
      day.bottomInfo = festivals[0];
    } else {
      // 获取节气
      const jieQi = lunar.getJieQi();
      if (jieQi) {
        day.bottomInfo = jieQi;
      } else {
        // 显示农历日期
        day.bottomInfo = lunar.getDayInChinese();
      }
    }
  }
  
  return day;
};

// 月份导航
const navigateMonth = (direction: 'prev' | 'next') => {
  const current = new Date(currentDate.value);
  if (direction === 'prev') {
    current.setMonth(current.getMonth() - 1);
  } else {
    current.setMonth(current.getMonth() + 1);
  }
  currentDate.value = current;
};

// 回到今天
const goToday = () => {
  currentDate.value = new Date();
};

// 历法切换
const toggleCalendar = (type: 'solar' | 'lunar') => {
  calendarType.value = type;
};

// 日期确认
const onDateConfirm = (value: Date) => {
  formData.value.birthDate = value;
  showDatePicker.value = false;
};

// 时间确认
const onTimeConfirm = (value: string) => {
  formData.value.birthTime = value;
  showTimePicker.value = false;
};

// 格式化显示日期
const formatDisplayDate = computed(() => {
  const date = formData.value.birthDate;
  if (calendarType.value === 'solar') {
    return date.toLocaleDateString('zh-CN');
  } else {
    const solar = Solar.fromDate(date);
    const lunar = solar.getLunar();
    return `农历${lunar.getYearInChinese()}年${lunar.getMonthInChinese()}月${lunar.getDayInChinese()}`;
  }
});

// 地区选择确认 - 更新为Vant4格式
const onAreaConfirm = ({ selectedOptions }: { selectedOptions: Array<{ text: string; value: string }> }) => {
  // selectedOptions是一个数组，包含选中的省市区信息
  const regionNames = selectedOptions.map(option => option.text).join('-');
  const regionCodes = selectedOptions.map(option => option.value);
  
  formData.value.region = regionNames;
  formData.value.regionCode = regionCodes[regionCodes.length - 1]; // 存储最后一级的地区码
  showAreaPicker.value = false;
};

// 选项数据
const incomeOptions = [
  { label: '3K以下', value: 'below_3k' },
  { label: '3K-5K', value: '3k_5k' },
  { label: '5K-8K', value: '5k_8k' },
  { label: '8K-12K', value: '8k_12k' },
  { label: '12K-20K', value: '12k_20k' },
  { label: '20K以上', value: 'above_20k' }
];

const educationOptions = [
  { label: '高中及以下', value: 'high_school' },
  { label: '大专', value: 'college' },
  { label: '本科', value: 'bachelor' },
  { label: '硕士', value: 'master' },
  { label: '博士', value: 'phd' }
];

const mbtiOptions = [
  'INTJ', 'INTP', 'ENTJ', 'ENTP',
  'INFJ', 'INFP', 'ENFJ', 'ENFP',
  'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ',
  'ISTP', 'ISFP', 'ESTP', 'ESFP'
];

// 身高输入格式化器
const heightFormatter = (value: string) => {
  // 只允许输入数字，且最大3位
  return value.replace(/[^\d]/g, '').slice(0, 3);
};
const heightValidator = (value: string | number) => {
  const num = Number(value);
  return num >= 120 && num <= 240;
};

// 计算是否可以继续
const canProceed = computed(() => {
  switch (currentStep.value) {
    case 1: return formData.value.gender !== '';
    case 2: return true; // 日期有默认值
    case 3: return formData.value.height !== '' && heightValidator(formData.value.height);
    case 4: return formData.value.weight !== '';
    case 5: return formData.value.region !== '';
    case 6: return formData.value.occupation !== '';
    case 7: return formData.value.income !== '';
    case 8: return formData.value.education !== '';
    case 9: return true; // 信仰可选
    case 10: return formData.value.mbti !== '';
    case 11: return formData.value.bio.trim() !== '';
    case 12: return true; // 隐私简介可选
    default: return false;
  }
});

// 方法
// const onSwipeChange = (index: number) => {
//   currentStep.value = index + 1;
// };

const nextStep = () => {
  if (currentStep.value === totalSteps) {
    submitForm();
  } else {
    // swipeRef.value?.next();
    currentStep.value++;
    swipeRef.value?.swipeTo(currentStep.value - 1);
  }
};

const prevStep = () => {
//   swipeRef.value?.prev();
currentStep.value--;
  swipeRef.value?.swipeTo(currentStep.value - 1);
};

const submitForm = async () => {
  try {
    // 这里调用API提交表单数据
    console.log('提交表单数据:', formData.value);
    Toast.success('信息保存成功！');
    router.push('/home');
  } catch (error) {
    Toast.fail('保存失败，请重试');
  }
};

onMounted(() => {
  // 检查是否已经登录和是否需要填写信息
  // 这里可以添加openid检查逻辑
});
</script>

<style scoped>
.profile-setup-container {
  background-color: #F2EEE8;
  min-height: 100vh;
  font-family: "Microsoft YaHei", sans-serif;
  display: flex;
  flex-direction: column;
}

/* 进度条 */
.progress-container {
  padding: 20px 16px 10px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background-color: #E0D5C7;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #D75670;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 14px;
  color: #6A6A6A;
  font-weight: 500;
}

/* 滑动容器 */
.setup-swipe {
  width: 100vw;
  overflow: hidden !important; /* 隐藏溢出内容 */
  touch-action: none !important; /* 禁用触摸操作 */
}

/* 卡片样式 */
.setup-card {
  width: 96vw;
  margin: 20px auto;
  border-radius: 20px;
  box-shadow: 0 4px 24px 0 rgba(0,0,0,0.08);
  background: #fff;
  transition: box-shadow 0.3s, transform 0.3s;
  position: relative;
  z-index: 2;
  padding: 40px 24px;
  text-align: center;
  min-height: 400px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* 淡化左右卡片 */
.van-swipe-item {
  display: flex;
  justify-content: center;
  align-items: center;
  transition: filter 0.3s, opacity 0.3s, transform 0.3s;
}
.van-swipe-item:not(.van-swipe-item-active) .setup-card {
  /* 去除模糊和灰度，仅保留透明和缩放 */
  filter: none;
  opacity: 0.6;
  transform: scale(0.95);
  z-index: 1;
}
.van-swipe-item.van-swipe-item-active .setup-card {
  filter: none;
  opacity: 1;
  transform: scale(1);
  z-index: 2;
}

.card-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.card-title {
  font-size: 24px;
  color: #333;
  margin-bottom: 8px;
  font-weight: 600;
}

.card-subtitle {
  font-size: 16px;
  color: #6A6A6A;
  margin-bottom: 32px;
  line-height: 1.4;
}

/* 性别选择 */
.gender-options {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.gender-option {
  background-color: #F8F8F8;
  border: 2px solid #E0E0E0;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 100px;
}

.gender-option.active {
  background-color: #D75670;
  border-color: #D75670;
  color: white;
}

.gender-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

/* 输入框 */
.input-container {
  position: relative;
  margin: 0 auto;
  max-width: 280px;
}

.setup-input {
  width: 100%;
  padding: 16px;
  font-size: 16px;
  border: 1px solid #E0D5C7;
  border-radius: 8px;
  background-color: #FFFFFF;
  color: #333;
  text-align: center;
  outline: none;
  transition: border-color 0.3s ease;
}

.setup-input::placeholder {
  color: #999;
  text-align: center;
}

.setup-input:focus {
  border-color: #D75670;
  background-color: white;
}

.input-unit {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  color: #6A6A6A;
  font-size: 16px;
}

/* 文本域 */
.textarea-container {
  position: relative;
  max-width: 320px;
  margin: 0 auto;
}

.setup-textarea {
  width: 100%;
  min-height: 120px;
  padding: 16px;
  font-size: 16px;
  border: 1px solid #E0D5C7;
  border-radius: 8px;
  background-color: #FFFFFF;
  color: #333;
  resize: vertical;
  font-family: "Microsoft YaHei", sans-serif;
  text-align: center;
  outline: none;
  transition: border-color 0.3s ease;
}

.setup-textarea::placeholder {
  color: #999;
  text-align: center;
}

.setup-textarea:focus {
  border-color: #D75670;
  background-color: white;
}

.char-count {
  position: absolute;
  bottom: 8px;
  right: 12px;
  font-size: 12px;
  color: #6A6A6A;
}

/* 收入选项 */
.income-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  max-width: 320px;
  margin: 0 auto;
}

.income-option {
  background-color: #F8F8F8;
  border: 2px solid #E0E0E0;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.income-option.active {
  background-color: #D75670;
  border-color: #D75670;
  color: white;
}

/* 学历选项 */
.education-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 280px;
  margin: 0 auto;
}

.education-option {
  background-color: #F8F8F8;
  border: 2px solid #E0E0E0;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
}

.education-option.active {
  background-color: #D75670;
  border-color: #D75670;
  color: white;
}

/* MBTI选项 */
.mbti-options {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  max-width: 320px;
  margin: 0 auto;
}

.mbti-option {
  background-color: #F8F8F8;
  border: 2px solid #E0E0E0;
  border-radius: 8px;
  padding: 8px 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 12px;
  font-weight: 600;
}

.mbti-option.active {
  background-color: #D75670;
  border-color: #D75670;
  color: white;
}

/* 日期选择器 */
.date-picker-container {
  max-width: 320px;
  margin: 0 auto;
  background-color: white;
  border-radius: 12px;
  overflow: hidden;
}

/* 底部按钮 */
.bottom-actions {
  padding: 20px 16px 40px;
  display: flex;
  gap: 12px;
}

.btn-primary, .btn-secondary {
  flex: 1;
  padding: 16px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: "Microsoft YaHei", sans-serif;
}

.btn-primary {
  background-color: #D75670;
  color: white;
}

.btn-primary:disabled {
  background-color: #E0E0E0;
  color: #6A6A6A;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #F8F8F8;
  color: #333;
  border: 2px solid #E0E0E0;
}

/* 统一设置所有输入框placeholder居中 */
.van-field__control {
  text-align: center !important;
}
.van-field__control::placeholder {
  text-align: center !important;
}

/* 普通input输入框 */
.setup-input {
  text-align: center;
}
.setup-input::placeholder {
  text-align: center;
}

/* textarea输入框 */
.setup-textarea {
  text-align: center;
}
.setup-textarea::placeholder {
  text-align: center;
}

:deep(.van-field__control) {
  text-align: center !important;
}
:deep(.van-field__control::placeholder) {
  text-align: center !important;
}

.btn-primary:not(:disabled):active {
  background-color: #C44A63;
}

.btn-secondary:active {
  background-color: #E0E0E0;
}

/* 历法选择器 */
.calendar-type-selector {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  justify-content: center;
}

.calendar-type-btn {
  padding: 8px 16px;
  border: 1px solid #E0D5C7;
  background-color: #FFFFFF;
  color: #6A6A6A;
  border-radius: 20px;
  font-size: 14px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.calendar-type-btn.active {
  background-color: #D75670;
  color: #FFFFFF;
  border-color: #D75670;
}

/* 日期时间容器 */
.date-time-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.date-section,
.time-section {
  text-align: left;
}

.section-label {
  display: block;
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

/* 自定义日历容器 */
.custom-calendar-container {
  padding: 16px;
  background-color: #FFFFFF;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 0 8px;
}

.header-title {
  font-size: 18px;
  font-weight: 500;
  color: #333;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.lunar-year-info {
  font-size: 12px;
  color: #D75670;
  margin-top: 4px;
  font-weight: normal;
}

.nav-arrow {
  font-size: 20px;
  color: #D75670;
  cursor: pointer;
  padding: 8px;
}

.calendar-actions {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.today-btn,
.confirm-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 16px;
  font-size: 14px;
  cursor: pointer;
}

.today-btn {
  background-color: #F0F0F0;
  color: #666;
}

.confirm-btn {
  background-color: #D75670;
  color: white;
}

/* 自定义日历样式 */
.custom-calendar {
  background-color: transparent;
}

.custom-calendar :deep(.van-calendar__header) {
  display: none;
}

.custom-calendar :deep(.van-calendar__weekdays) {
  color: #666;
  font-size: 14px;
}

.custom-calendar :deep(.van-calendar__weekday:first-child),
.custom-calendar :deep(.van-calendar__weekday:last-child) {
  color: #D75670;
}

.custom-calendar :deep(.weekend-red) {
  color: #D75670 !important;
}

.custom-calendar :deep(.van-calendar__day) {
  font-size: 16px;
  height: 44px;
}

.custom-calendar :deep(.van-calendar__top-info) {
  font-size: 14px;
  font-weight: bold;
  color: #333;
}

.custom-calendar :deep(.van-calendar__bottom-info) {
  font-size: 10px;
  color: #999;
  margin-top: 2px;
}

.custom-calendar :deep(.van-calendar__selected-day) {
  background-color: #D75670;
  color: white;
}

.custom-calendar :deep(.van-calendar__selected-day .van-calendar__top-info),
.custom-calendar :deep(.van-calendar__selected-day .van-calendar__bottom-info) {
  color: white !important;
}

/* 日期时间按钮 */
.date-btn,
.time-btn {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  font-size: 16px;
  border: 1px solid #E0D5C7;
  background-color: #FFFFFF;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.date-btn:hover,
.time-btn:hover {
  border-color: #D75670;
}

.btn-icon {
  font-size: 18px;
}

/* 统一设置所有输入框placeholder居中 */
.van-field__control {
  text-align: center !important;
}
.van-field__control::placeholder {
  text-align: center !important;
}

/* 普通input输入框 */
.setup-input {
  text-align: center;
}
.setup-input::placeholder {
  text-align: center;
}

/* textarea输入框 */
.setup-textarea {
  text-align: center;
}
.setup-textarea::placeholder {
  text-align: center;
}

:deep(.van-field__control) {
  text-align: center !important;
}
:deep(.van-field__control::placeholder) {
  text-align: center !important;
}

.btn-primary:not(:disabled):active {
  background-color: #C44A63;
}

.btn-secondary:active {
  background-color: #E0E0E0;
}
</style>