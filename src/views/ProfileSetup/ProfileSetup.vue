<template>

  <div class="profile-setup-container">
    <!-- 添加悬浮返回按钮 -->
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
    <div class="card-icon animate-bounce">🎂</div>
    <h2 class="card-title">出生信息</h2>
    <p class="card-subtitle">告诉我们你的生日</p>
    
    <!-- 日期选择 -->
    <div class="date-section">
      <label class="section-label">
        出生日期 <span class="required-mark">*</span>
      </label>
      <van-popup v-model:show="showDatePicker" position="bottom">
        <van-date-picker
          v-model="currentDate"
          :min-date="minDate"
          :max-date="maxDate"
          title="选择出生日期"
          @confirm="onDateConfirm"
          @cancel="showDatePicker = false"
          :columns-type="['year', 'month', 'day']"
        />
      </van-popup>
      <button 
        class="btn-secondary date-btn animate-scale" 
        @click="showDatePicker = true" 
        :class="{ 'has-value': formData.birthDate }"
      >
        <div class="date-display">
          <div class="main-date">{{ formatSolar(formData.birthDate) }}</div>
          <div class="sub-date">{{ formatLunar(formData.birthDate) }}</div>
        </div>
        <span class="btn-icon">📅</span>
      </button>
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
              @keyup.enter="handleEnter"
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
              @keyup.enter="handleEnter"
            >
              <template #right-icon>
                <span class="input-unit">kg</span>
              </template>
            </van-field>
          </div>
        </div>
      </van-swipe-item>

      <!-- 第5步：婚姻状况 -->
    <van-swipe-item>
  <div class="setup-card">
    <div class="card-icon">💍</div>
    <h2 class="card-title">婚姻状况</h2>
    <p class="card-subtitle">请选择你的婚姻状态</p>
    <div class="marital-toggle">
      <span :class="{ active: formData.married === 0 }">未婚</span>
      <van-switch
        v-model="formData.married"
        :active-value="1"
        :inactive-value="0"
        size="24px"
        active-color="#D75670"
      />
      <span :class="{ active: formData.married === 1 }">已婚</span>
    </div>
  </div>
</van-swipe-item>

<!-- 第6步：孩子状况（仅当已婚时显示） -->
<van-swipe-item v-if="showChildrenStep">
  <div class="setup-card">
    <div class="card-icon">👶</div>
    <h2 class="card-title">孩子状况</h2>
    <p class="card-subtitle">你有孩子吗？</p>
    <div class="children-toggle">
      <span :class="{ active: formData.child === 0 }">没有孩子</span>
      <van-switch
        v-model="formData.child"
        :active-value="1"
        :inactive-value="0"
        size="24px"
        active-color="#D75670"
      />
      <span :class="{ active: formData.child === 1 }">有孩子</span>
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
              :area-list="areaList"
              :columns-placeholder="['', '', '']"
              title="选择地区"
              @confirm="onAreaConfirm"
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
              maxlength="50"
              @keyup.enter="handleEnter"
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
      <!-- <van-swipe-item v-if="false">
        <div class="setup-card">
          <div class="card-icon">🙏</div>
          <h2 class="card-title">信仰（可选）</h2>
          <p class="card-subtitle">你的宗教信仰</p>
          <div class="input-container">
            <van-field
  v-model="formData.religionText"
  is-link
  readonly
  label="宗教信仰"
  placeholder="请选择"
  @click="showReligionPicker = true"
/>
<van-popup v-model:show="showReligionPicker" position="bottom">
  <van-picker
    :columns="religionOptions"
    @confirm="onReligionConfirm"
    @cancel="showReligionPicker = false"
  />
</van-popup>
          </div>
        </div>
      </van-swipe-item> -->

      <!-- MBTI -->
      <!-- <van-swipe-item v-if="false">
        <div class="setup-card">
          <div class="card-icon">🧠</div>
          <h2 class="card-title">MBTI人格（可选）</h2>
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
      </van-swipe-item> -->

      <!-- 联系方式 -->
      <van-swipe-item>
        <div class="setup-card">
          <div class="card-icon">📱</div>
          <h2 class="card-title">联系方式</h2>
          <p class="card-subtitle">请输入你的手机号码</p>
          <div class="input-container">
            <van-field
              v-model="formData.phone"
              type="tel"
              label="手机号码"
              placeholder="请输入手机号码"
              input-align="center"
              maxlength="11"
              :rules="[
                { required: true, message: '请输入手机号码' }, 
                { validator: phoneValidator, message: '请输入正确的手机号码' }
              ]"
              class="setup-input"
              @keyup.enter="handleEnter"
            />
          </div>
        </div>
      </van-swipe-item>

      <!-- 简介 -->
      <van-swipe-item>
        <div class="setup-card">
          <div class="card-icon">📝</div>
          <h2 class="card-title">个人简介</h2>
          <p class="card-subtitle">介绍一下自己吧</p>
          <div class="textarea-container bio-container">
            <textarea 
              v-model="formData.bio" 
              placeholder="写一段简短的自我介绍..."
              class="setup-textarea bio-textarea"
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
          <div class="textarea-container private-bio-container">
            <textarea 
              v-model="formData.privateBio" 
              placeholder="写一些更私密的信息..."
              class="setup-textarea private-textarea"
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
import { Area, Swipe, SwipeItem, DatePicker, TimePicker, Toast,showFailToast,showSuccessToast, Calendar, Popup, Icon, Field, FloatingBubble  } from 'vant';
import { areaList } from '@vant/area-data';
import lunisolar from 'lunisolar';
import apiClient from '@/plugins/axios';
import { useUserInfoStore } from '@/store/userinfo'
import type { UserProfile } from '@/store/userinfo';
import { getPreviousRoute } from '@/utils/routeHistory';

const userStore = useUserInfoStore()
const router = useRouter();
const swipeRef = ref();
const currentStep = ref(1);

const showDatePicker = ref(false);
const dateValue = ref(new Date());

const currentDate = ref([
  (new Date().getFullYear()).toString(),
  (new Date().getMonth() + 1).toString(),
  (new Date().getDate()).toString()
]);

const minDate = new Date(1980, 0, 1);
const maxDate = new Date(2100, 12, 31);

const showAreaPicker = ref(false);
const showReligionPicker = ref(false);

const handleEnter = () => {
  if (canProceed.value) {
    nextStep();
  }
};

const offset = ref({ x: 20, y: 40 });
// 直接使用导入的areaList数据

// 表单数据
const formData = ref({
  gender: '',
  birthDate: new Date(),
  height: '',
  weight: '',
  region: '',
  regionCode: '321282', 
  occupation: '',
  income: '',
  education: '',
  religion: '',
  religionText: '',
  mbti: '',
  phone: '',
  bio: '',
  privateBio: '',
  married: 0,
  child: 0
});

const totalSteps = computed(() => {
  let steps = 13; // 固定显示的总页数（不含孩子状况）
  if (formData.value.married === 1) {
    steps += 1; // 已婚时加1页（孩子状况）
  }
  return steps;
});

const showChildrenStep = computed(() => {
  return formData.value.married === 1;
});

// 设置婚姻状况并处理逻辑
const setMaritalStatus = (status: 0 | 1) => {
  formData.value.married = status;
  
  // 如果选择未婚，自动设置没有孩子
  if (status === 0) {
    formData.value.child = 0;
  }
};

watch(currentStep, (newVal) => {
  // 当currentStep变化时，更新swipe位置
  swipeRef.value?.swipeTo(newVal - 1);
});
const weightValidator = (value: string | number) => {
  return Number(value) <= 250;
};

const onDateConfirm = (params:any) => {
  const { selectedValues } = params;
  // selectedValues 是 string[], 例如 ['2023', '10', '26']
  currentDate.value = selectedValues; // 更新 currentDate 以保持 date-picker 的 v-model
  // 将选择的年月日转换为 Date 对象存储
  formData.value.birthDate = new Date(parseInt(selectedValues[0]), parseInt(selectedValues[1]) - 1, parseInt(selectedValues[2]));
  showDatePicker.value = false;
};

const goBack = () => {
  const previousRoute = getPreviousRoute();
  if (previousRoute) {
    router.replace({ path: previousRoute.path, query: previousRoute.query, params: previousRoute.params });
  } else {
    router.replace('/userCenter');
  }
};

const formatSolar = (date: Date | null) => {
  if (!date) return '请选择日期';
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;
};

const formatLunar = (date: Date | null) => {
  if (!date) return '';
  return lunisolar(date).format('lY年(cZ年) lMlD');
};


const onReligionConfirm = ({ selectedOptions }: { selectedOptions: Array<{ text: string; value: string }> }) => {
  formData.value.religion = selectedOptions[0].value;
  formData.value.religionText = selectedOptions[0].text;
  showReligionPicker.value = false;
};

const onAreaConfirm = ({ selectedOptions }: { selectedOptions: Array<{ text: string; value: string }> }) => {
  // selectedOptions是一个数组，包含选中的省市区信息
  // 我的候选词是’‘，如果某个选项为’‘就不join空的，只join前面不为空的
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

const religionOptions = [
  { text: '佛教', value: 'buddhism' },
  { text: '基督教', value: 'christianity' },
  { text: '伊斯兰教', value: 'islam' },
  { text: '道教', value: 'taoism' },
  { text: '无宗教信仰', value: 'none' },
  { text: '其他', value: 'other' }
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

const phoneValidator = (value: string) => {
  const phoneRegex = /^1[3-9]\d{9}$/;
  return phoneRegex.test(value);
};

// 计算是否可以继续
const canProceed = computed(() => {
  switch (currentStep.value) {
    case 1: return formData.value.gender !== '';
    case 2: return formData.value.birthDate !== null;
    case 3: return formData.value.height !== '' && heightValidator(formData.value.height);
    case 4: return formData.value.weight !== '' && weightValidator(formData.value.weight);
    case 5: return formData.value.married < 2; // 婚姻状况必选
    case 6: return formData.value.child < 2; // 孩子状况必选
    case 7: return formData.value.region !== '';
    case 8: return formData.value.occupation !== '';
    case 9: return formData.value.income !== '';
    case 10: return formData.value.education !== '';
    // case 11: return true; // 信仰可选
    // case 12: return true; // MBTI可选
    case 11: return formData.value.phone !== '' && phoneValidator(formData.value.phone); // 手机号必填且格式正确
    case 12: return true; // 简介可选
    case 13: return true; // 隐私简介可选
    default: return false;
  }
});

// 方法
// const onSwipeChange = (index: number) => {
//   currentStep.value = index + 1;
// };

// const getSwipeIndex = (step: number) => {
//   // 如果未婚，且逻辑步骤 >= 6，swipe索引要减1
//   if (formData.value.married === 0 && step >= 6) {
//     return step - 2; // 跳过第6步
//   }
//   return step - 1;
// };
const getSwipeIndex = (step: number) => {
  let offset = 0;
  if (formData.value.married === 0 && step >= 6) {
    offset += 1; // 未婚时跳过孩子状况
  }
  return step - 1 - offset;
};



const nextStep = () => {
  if (currentStep.value === totalSteps.value) {
    submitForm();
    return;
  }

  currentStep.value++;
  swipeRef.value?.swipeTo(getSwipeIndex(currentStep.value));
};

const prevStep = () => {
  currentStep.value--;
  swipeRef.value?.swipeTo(getSwipeIndex(currentStep.value));
};





const submitForm = async () => {
  try {
    // 将表单数据转换为后端需要的格式
    const profileData = {
      gender: formData.value.gender,
      birth_date: formData.value.birthDate ? formatDate(formData.value.birthDate) : null,
      height: formData.value.height ? parseInt(formData.value.height) : null,
      weight: formData.value.weight ? parseFloat(formData.value.weight) : null,
      region_code: formData.value.regionCode,
      occupation: formData.value.occupation,
      income_level: formData.value.income,
      education: formData.value.education,
      married: formData.value.married,
      child: formData.value.child,
      religion: formData.value.religion || null,
      mbti: formData.value.mbti || null,
      phone: formData.value.phone,
      mem: formData.value.bio,
      mem_pri: formData.value.privateBio
    };
    
    // 调用API提交表单数据
    const response = await apiClient.post('/api/profile', profileData);
    
    if (response.data?.status === 'success') {
      showSuccessToast('资料已提交审核')

      /* 1. 拼一份完整 UserProfile */
      const localProfile: UserProfile = {
        id: 0,
        nickname: '',
        phone: formData.value.phone,
        gender: formData.value.gender,
        birth_date: profileData.birth_date!,
        height: profileData.height!,
        weight: profileData.weight!,
        region_code: formData.value.regionCode,
        occupation: formData.value.occupation,
        education: formData.value.education,
        income_level: formData.value.income,
        religion: formData.value.religion || '',
        mbti: formData.value.mbti || '',
        mem: formData.value.bio,
        mem_pri: formData.value.privateBio,
        avatar: '',
        avatar_url: '',
        photo: '',
        points: 0
      }

      /* 2. 写本地 + 写 pinia */
      userStore.updateProfileAndCache(localProfile)

      router.replace('/home')
    }
  } catch (error) {
    showFailToast('保存失败，请重试');
    console.error('提交失败:', error);
  }
};

const formatDate = (date: Date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

// onMounted(async () => {
//   // 初始化当前日期为今天
//   dateValue.value = formData.value.birthDate || new Date();
  
//   try {
//     const response = await apiClient.get('/api/getprofile');
//     if (response.status === 200 && response.data) {
//       const profile = response.data;
//       formData.value.gender = profile.gender || '';
//       if (profile.birth_date) {
//         const birthDateObj = new Date(profile.birth_date);
//         formData.value.birthDate = birthDateObj;
        
//         // 更新日期选择器显示值
//         currentDate.value = [
//           birthDateObj.getFullYear().toString(),
//           (birthDateObj.getMonth() + 1).toString(),
//           birthDateObj.getDate().toString()
//         ];
//       }
//       formData.value.height = profile.height ? String(profile.height) : '';
//       formData.value.weight = profile.weight ? String(profile.weight) : '';
//       formData.value.region = profile.region || '';
//       formData.value.regionCode = profile.region_code || '321282';
//       formData.value.occupation = profile.occupation || '';
//       formData.value.income = profile.income_level || '';
//       formData.value.education = profile.education || '';
//       formData.value.religion = profile.religion || '';
//       formData.value.mbti = profile.mbti || '';
//       formData.value.phone = profile.phone || '';
//       formData.value.bio = profile.mem || '';
//       formData.value.privateBio = profile.mem_pri || '';

//       // 更新日期选择器显示值
//       if (profile.birth_date) {
//         const birthDate = new Date(profile.birth_date);
//         currentDate.value = [
//           birthDate.getFullYear().toString(),
//           (birthDate.getMonth() + 1).toString(),
//           birthDate.getDate().toString()
//         ];
//       }
//     }
//   } catch (error) {
//     console.error('加载用户资料失败:', error);
//     // 如果是404，表示用户资料不存在，可以忽略
//    
//   }
// });


// 从store加载数据到表单
const loadDataFromStore = () => {
  if (!userStore.profile) return;
  
  const profile = userStore.profile;
  formData.value.gender = profile.gender || '';
  formData.value.birthDate = userStore.birthDateObj ?? new Date();
  formData.value.height = profile.height ? String(profile.height) : '';
  formData.value.weight = profile.weight ? String(profile.weight) : '';
  
  // 地区代码转换为地区名称
  if (profile.region_code) {
    formData.value.regionCode = profile.region_code;
    // 查找对应的地区名称
    const province = areaList.province_list[profile.region_code.substring(0, 2) + '0000'];
    const city = areaList.city_list[profile.region_code.substring(0, 4) + '00'];
    const district = areaList.county_list[profile.region_code];
    
    if (province && city && district) {
      formData.value.region = `${province}-${city}-${district}`;
    } else if (province && district) {
      formData.value.region = `${province}-${district}`;
    } else if (province) {
      formData.value.region = province;
    }
  } else {
    formData.value.region = '';
    formData.value.regionCode = '321282';
  }
  
  formData.value.occupation = profile.occupation || '';
  formData.value.income = profile.income_level || '';
  formData.value.education = profile.education || '';
  
  // 宗教值映射到显示文本
  if (profile.religion) {
    const religionOption = religionOptions.find(opt => opt.value === profile.religion);
    if (religionOption) {
      formData.value.religion = religionOption.value;
      formData.value.religionText = religionOption.text;
    }
  } else {
    formData.value.religion = '';
    formData.value.religionText = '';
  }
  
  formData.value.mbti = profile.mbti || '';
  formData.value.phone = profile.phone || '';
  formData.value.bio = profile.mem || '';
  formData.value.privateBio = profile.mem_pri || '';

  if (userStore.formattedBirthDate) {
    currentDate.value = [...userStore.formattedBirthDate];
  }
};
watch(() => userStore.profile, loadDataFromStore, { immediate: true })
watch(currentStep, (newVal) => {
  swipeRef.value?.swipeTo(getSwipeIndex(newVal));
});
onMounted(() => {
  // 初始化当前日期为今天
  if (userStore.profile) {
    loadDataFromStore()
  }

});
</script>

<style scoped>


/* 个人简介和隐私简介文本域调整 */
.bio-container,
.private-bio-container {
  max-width: 100% !important; /* 填满可用空间 */
  width: 100%;
}

.bio-textarea,
.private-textarea {
  min-height: 180px !important; /* 增加高度 */
  width: 100%; /* 填满容器 */
  padding: 20px; /* 增加内边距 */
  font-size: 16px; /* 增大字体 */
}

.char-count {
  position: absolute;
  bottom: 15px; /* 调整位置 */
  right: 15px; /* 调整位置 */
  font-size: 14px; /* 增大字体 */
}
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

/* 日期选择区域 */
.date-section {
  text-align: left;
  max-width: 320px;
  margin: 0 auto;
}

.section-label {
  display: block;
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 12px;
  text-align: center;
}

.required-mark {
  color: #D75670;
  font-weight: bold;
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

/* 日历头部样式 */
.header-title {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.main-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.sub-title {
  font-size: 12px;
  color: #D75670;
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
  padding-bottom: 8px;
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
  height: 52px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 4px;
}

.custom-calendar :deep(.van-calendar__top-info) {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  line-height: 1;
}

.custom-calendar :deep(.van-calendar__bottom-info) {
  font-size: 11px;
  color: #999;
  line-height: 1;
  margin-top: 2px;
}

.custom-calendar :deep(.van-calendar__selected-day) {
  background-color: #D75670;
  color: white;
  border-radius: 8px;
}

.custom-calendar :deep(.van-calendar__selected-day .van-calendar__top-info),
.custom-calendar :deep(.van-calendar__selected-day .van-calendar__bottom-info) {
  color: white !important;
}

/* 日期按钮样式优化 */
.date-btn {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  font-size: 16px;
  border: 2px solid #E0D5C7;
  background-color: #FFFFFF;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 70px;
}

.date-btn.has-value {
  border-color: #D75670;
  background-color: #FFF8FA;
}

.date-btn:hover {
  border-color: #D75670;
  box-shadow: 0 2px 8px rgba(215, 86, 112, 0.1);
  transform: translateY(-1px);
}

/* 日期显示样式 */
.date-display {
  text-align: left;
  flex: 1;
}

.main-date {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.sub-date {
  font-size: 13px;
  color: #D75670;
  font-weight: normal;
  line-height: 1.2;
  margin-top: 4px;
}

.btn-icon {
  font-size: 20px;
  color: #D75670;
}

/* 动画效果 */
.animate-bounce {
  animation: bounce 2s infinite;
}

.animate-scale {
  transition: transform 0.2s ease;
}

.animate-scale:active {
  transform: scale(0.98);
}

.card-enter {
  animation: cardEnter 0.5s ease-out;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

@keyframes cardEnter {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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

/* 添加悬浮按钮样式 */
.floating-back-btn {
  position: fixed;
  z-index: 9999;
  bottom: 80px;
  right: 20px;
  background-color: #D75670;
  box-shadow: 0 4px 12px rgba(215, 86, 112, 0.3);
}

.floating-back-btn:active {
  transform: scale(0.95);
  transition: transform 0.2s;
}

/* 响应式调整 */
@media (max-width: 480px) {
  .floating-back-btn {
    bottom: 70px;
    right: 15px;
    transform: scale(0.9);
  }
}

:deep(.van-floating-bubble) {
  z-index: 9999;
  box-shadow: 0 4px 12px rgba(255, 154, 158, 0.5);
}

:deep(.van-floating-bubble__icon) {
  color: white;
  font-size: 20px;
}

.marital-toggle, .children-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  max-width: 320px;
  margin: 0 auto;
}

.marital-toggle span, .children-toggle span {
  font-size: 16px;
  font-weight: 500;
  color: #999;
  transition: color 0.3s;
}

.marital-toggle span.active, .children-toggle span.active {
  color: #D75670;
  font-weight: 600;
}

/* 自定义Switch样式 */
:deep(.van-switch) {
  background-color: #E0E0E0;
  border: 1px solid #E0E0E0;
}

:deep(.van-switch__node) {
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

:deep(.van-switch--on) {
  background-color: rgba(215, 86, 112, 0.2);
}

</style>