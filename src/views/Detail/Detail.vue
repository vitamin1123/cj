<template>
  <div class="detail-container">
    <div class="header">
      <van-icon name="arrow-left" class="back-icon" @click="goBack" />
      <span class="header-title">详细信息</span>
      <div class="header-right">
        <van-icon name="like" class="heart-icon" :class="{ liked: isLiked }" @click="toggleLike" />
      </div>
    </div>

    <div class="content">
      <div class="profile-card scroll-animate">
        <div class="avatar-section">
          <img 
            v-if="userInfo.avatar" 
            :src="`/avatars/${userInfo.avatar}`" 
            class="avatar" 
          />
          <img 
            v-else 
            :src="getDefaultAvatarUrl()" 
            class="avatar" 
          />
          
          <div class="basic-info">
            <h2 class="name">{{ userInfo.nickname || '未设置昵称' }}</h2>
            <!-- 修改：确保年龄、身高、星座在同一行 -->
            <div class="info-row">
              <span class="birth-year">{{ displayBirthYear }}</span>
              <span class="height">{{ userInfo.height || '--' }}cm</span>
              <span class="constellation">{{ displayConstellation }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="info-section scroll-animate">
        <h3 class="section-title">基本信息</h3>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">职业</span>
            <span class="value">{{ userInfo.occupation || '未填写' }}</span>
          </div>
          <div class="info-item">
            <span class="label">学历</span>
            <span class="value">{{ displayEducation }}</span>
          </div>
          <div class="info-item">
            <span class="label">宗教信仰</span>
            <span class="value">{{ displayReligion }}</span>
          </div>
          <div class="info-item">
            <span class="label">月收入</span>
            <span class="value">{{ displayIncome }}</span>
          </div>
          <!-- 地区信息占据两列宽度 -->
          <div class="info-item full-width">
            <span class="label">地区</span>
            <span class="value">{{ displayRegion }}</span>
          </div>
        </div>
      </div>
      
      <div class="info-section scroll-animate" v-if="userInfo.mem">
        <h3 class="section-title">个人简介</h3>
        <p class="description">{{ userInfo.mem }}</p>
      </div>

      <div class="info-section scroll-animate" v-if="userInfo.mbti">
        <h3 class="section-title">MBTI性格类型</h3>
        <div class="mbti-card">
          <div class="mbti-character-wrapper">
            <img :src="getMbtiImage(userInfo.mbti)" class="mbti-character" />
          </div>
          <div class="mbti-content">
            <h3 class="mbti-title">{{ mbtiChineseName }}</h3>
            <p class="mbti-subtitle">{{ userInfo.mbti.toUpperCase() }}</p>
            <p class="mbti-description">{{ mbtiDescription }}</p>
            <!-- 修改：重新设计MBTI展示为两行，去掉标题 -->
            <div class="mbti-dimensions">
              <!-- 第一行：外向/内向，直觉/实感 -->
              <div class="dimension-row">
                <div class="dimension">
                  <div class="dimension-options">
                    <span :class="['option', { active: mbtiFirstChar === 'E' }]">E外向</span>
                    <span :class="['option', { active: mbtiFirstChar === 'I' }]">I内向</span>
                  </div>
                </div>
                <div class="dimension">
                  <div class="dimension-options">
                    <span :class="['option', { active: mbtiSecondChar === 'N' }]">N直觉</span>
                    <span :class="['option', { active: mbtiSecondChar === 'S' }]">S实感</span>
                  </div>
                </div>
              </div>
              <!-- 第二行：思考/情感，判断/感知 -->
              <div class="dimension-row">
                <div class="dimension">
                  <div class="dimension-options">
                    <span :class="['option', { active: mbtiThirdChar === 'T' }]">T思考</span>
                    <span :class="['option', { active: mbtiThirdChar === 'F' }]">F情感</span>
                  </div>
                </div>
                <div class="dimension">
                  <div class="dimension-options">
                    <span :class="['option', { active: mbtiFourthChar === 'J' }]">J计划</span>
                    <span :class="['option', { active: mbtiFourthChar === 'P' }]">P随性</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="info-section scroll-animate" v-if="photoList.length > 0">
        <h3 class="section-title">照片({{ photoList.length }})</h3>
        <div class="photo-grid">
          <img v-for="(photo, index) in photoList" 
               :key="index" 
               :src="photo.trim()" 
               class="photo-item"
               @click="previewPhoto(index)" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter   } from 'vue-router';
import { getPreviousRoute } from '@/utils/routeHistory';
import { showImagePreview, showToast } from 'vant';
import { areaList } from '@vant/area-data'; 
import apiClient from '@/plugins/axios';
import { likeUser } from '@/api/like';
import { useLikeStore } from '@/store/likeStore';
const likeStore = useLikeStore();
const router = useRouter();
const isLiked = computed(() => {
  const userId = parseInt(router.currentRoute.value.params.id as string);
  return likeStore.hasLiked(userId);
});
const userInfo = ref<Record<string, any>>({});

// 计算默认头像URL，包含性别默认值处理
const getDefaultAvatarUrl = () => {
  const gender = userInfo.value.gender || 'male'; // 设置默认性别为male
  return gender === 'male' 
    ? '/avatars/male_def.png' 
    : '/avatars/female_def.png';
};

const incomeMap: Record<string, string> = {
  'below_3k': '3千元以下',
  '3k_5k': '3千-5千元',
  '5k_8k': '5千-8千元',
  '8k_12k': '8千-1.2万元',
  '12k_20k': '1.2万-2万元',
  'above_20k': '2万元以上'
};

// 学历 -> 中文名称 映射
const educationMap: Record<string, string> = {
  'high_school': '高中及以下',
  'college': '大专',
  'bachelor': '本科',
  'master': '硕士',
  'phd': '博士'
};

// 宗教 -> 中文名称 映射
const religionMap: Record<string, string> = {
  'buddhism': '佛教',
  'christianity': '基督教',
  'islam': '伊斯兰教',
  'taoism': '道教',
  'none': '无宗教信仰',
  'other': '其他'
};

// 地区代码解析函数
const parseRegion = (code: string) => {
  if (!code) return '未填写';
  
  try {
    // 省级代码 (前2位)
    const provinceCode = code.substring(0, 2) + '0000';
    // 市级代码 (前4位)
    const cityCode = code.substring(0, 4) + '00';
    
    const province = areaList.province_list[provinceCode];
    const city = areaList.city_list[cityCode];
    const county = areaList.county_list[code];
    
    if (province && city && county) {
      return `${province} ${city} ${county}`;
    }
    if (province && city) {
      return `${province} ${city}`;
    }
    if (province) {
      return province;
    }
    return '未知地区';
  } catch (e) {
    console.error('解析地区出错:', e);
    return '未知地区';
  }
};

// --- 计算属性 (Computed Properties) ---

// 照片列表处理
const photoList = computed(() => {
  if (!userInfo.value.photo) return [];
  // 假设照片路径需要拼接服务器地址
  const baseUrl = '/photo/'; 
  return userInfo.value.photo.split(',')
    .filter((p: string) => p.trim())
    .map((p: string) => `${baseUrl}${p.trim()}`);
});

// 显示处理后的地区
const displayRegion = computed(() => {
  return parseRegion(userInfo.value.region_code);
});

// 显示处理后的收入
const displayIncome = computed(() => {
  return incomeMap[userInfo.value.income_level] || '未填写';
});

// 显示处理后的学历
const displayEducation = computed(() => {
  return educationMap[userInfo.value.education] || '未填写';
});

// 显示处理后的宗教
const displayReligion = computed(() => {
  return religionMap[userInfo.value.religion] || '未填写';
});

// 出生年份显示
const displayBirthYear = computed(() => {
  if (!userInfo.value.birth_date) return '--';
  try {
    const date = new Date(userInfo.value.birth_date);
    return isNaN(date.getTime()) ? '--' : date.getFullYear() + '年';
  } catch {
    return '--';
  }
});

// 星座计算
const displayConstellation = computed(() => {
  if (!userInfo.value.birth_date) return '';
  try {
    const date = new Date(userInfo.value.birth_date);
    if (isNaN(date.getTime())) return '';
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const constellations = [
      { name: '摩羯座', start: [1, 20] }, { name: '水瓶座', start: [2, 19] },
      { name: '双鱼座', start: [3, 21] }, { name: '白羊座', start: [4, 20] },
      { name: '金牛座', start: [5, 21] }, { name: '双子座', start: [6, 22] },
      { name: '巨蟹座', start: [7, 23] }, { name: '狮子座', start: [8, 23] },
      { name: '处女座', start: [9, 23] }, { name: '天秤座', start: [10, 24] },
      { name: '天蝎座', start: [11, 23] }, { name: '射手座', start: [12, 22] },
    ];
    for (let i = constellations.length - 1; i >= 0; i--) {
        if (month > constellations[i].start[0] || (month === constellations[i].start[0] && day >= constellations[i].start[1])) {
            return constellations[i].name;
        }
    }
    return '摩羯座'; // 兜底
  } catch {
    return '';
  }
});

// MBTI相关计算属性
const mbtiChineseName = computed(() => {
  if (!userInfo.value.mbti) return '';
  const mbtiMap: Record<string, string> = {
    'INTJ': '建筑师', 'INTP': '逻辑学家', 'ENTJ': '指挥官', 'ENTP': '辩论家',
    'INFJ': '倡导者', 'INFP': '调停者', 'ENFJ': '主人公', 'ENFP': '竞选者',
    'ISTJ': '物流师', 'ISFJ': '守卫者', 'ESTJ': '总经理', 'ESFJ': '执政官',
    'ISTP': '鉴赏家', 'ISFP': '探险家', 'ESTP': '企业家', 'ESFP': '表演者'
  };
  return mbtiMap[userInfo.value.mbti.toUpperCase()] || userInfo.value.mbti;
});

const mbtiDescription = computed(() => {
  if (!userInfo.value.mbti) return '';
  const descMap: Record<string, string> = {
    'INTP': '充满奇思妙想的革新者，对知识有着永不满足的渴望。',
    'INTJ': '富有远见的战略家，擅长系统性地规划未来方向。',
    'INFJ': '富有同理心的引导者，善于理解他人并推动积极改变。',
    'INFP': '充满诗意的理想主义者，始终追寻内心的价值与意义。',
    'ENTJ': '果敢的领导者，热衷于制定宏大目标并推动团队达成。',
    'ENTP': '机智的挑战者，喜欢用创新思维解决复杂问题。',
    'ENFJ': '热情的催化剂，擅长激励他人并建立和谐的合作关系。',
    'ENFP': '充满活力的探索者，凭借创造力与热情感染周围的人。',
    'ISTJ': '严谨的守护者，以责任感与专注度确保任务高质量完成。',
    'ISTP': '务实的行动派，擅长通过实践探索解决问题的最佳路径。',
    'ISFJ': '温暖的支持者，默默为他人提供细致入微的关怀。',
    'ISFP': '敏感的艺术家，善于用美感与情感创造独特体验。',
    'ESTJ': '高效的组织者，以强大的执行力维持系统的有序运行。',
    'ESTP': '大胆的冒险者，在挑战与变化中展现卓越的适应能力。',
    'ESFJ': '亲切的协调者，致力于维护和谐的人际关系与社会联结。',
    'ESFP': '活力四射的表演者，享受与人互动并创造欢乐氛围。'
  };
  return descMap[userInfo.value.mbti.toUpperCase()] || '富有洞察力与好奇心的思考者。';
});

// 新增：提取MBTI的四个字符
const mbtiFirstChar = computed(() => {
  return userInfo.value.mbti?.charAt(0).toUpperCase() || '';
});

const mbtiSecondChar = computed(() => {
  return userInfo.value.mbti?.charAt(1).toUpperCase() || '';
});

const mbtiThirdChar = computed(() => {
  return userInfo.value.mbti?.charAt(2).toUpperCase() || '';
});

const mbtiFourthChar = computed(() => {
  return userInfo.value.mbti?.charAt(3).toUpperCase() || '';
});

const getMbtiImage = (mbti: string) => {
  // 这里应该是你的MBTI人物图片路径, 请确保路径正确
  return `/mbti-images/${mbti.toLowerCase()}.png`;
};

// --- 方法 (Methods) ---

// 照片预览
const previewPhoto = (index: number) => {
  showImagePreview({
    images: photoList.value,
    startPosition: index,
    closeable: true,
  });
};

// 获取用户数据
const fetchUserData = async () => {
  try {
    const userId = router.currentRoute.value.params.id;
    const response = await apiClient.get(`/api/user/${userId}`);
    
    if (response.data) {
      userInfo.value = response.data;
    } else {
      showToast('用户数据为空');
    }
  } catch (error: any) {
    console.error('获取用户数据失败:', error);
    showToast(error?.response?.data?.detail || '加载用户信息失败');
  }
};

// 返回上一页
const goBack = () => {
  const previousRoute = getPreviousRoute();
  
  if (previousRoute) {
    // 使用 replace 方法返回上一个页面
    router.replace({
      path: previousRoute.path,
      query: previousRoute.query,
      params: previousRoute.params
    });
  } else {
    // 如果没有历史记录，则返回首页
    router.replace('/home');
  }
};



const toggleLike = async () => {
  try {
    const userId = parseInt(router.currentRoute.value.params.id as string);
    const action = isLiked.value ? 'unlike' : 'like';
    await likeUser(userId, action);
    
    if (action === 'like') {
      likeStore.addLike(userId);
    } else {
      likeStore.removeLike(userId);
    }
    showToast(isLiked.value ? '已喜欢' : '已取消');
  } catch (error) {
    console.error('操作失败:', error);
    showToast('操作失败');
  }
};

// --- 生命周期钩子 (Lifecycle Hooks) ---

onMounted(() => {
  fetchUserData();

  // 设置滚动动画监听
  // IntersectionObserver是一个现代API，用于观察元素是否进入视口
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        // 当元素进入视口时
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          // (可选) 动画触发后停止观察，以提高性能
          observer.unobserve(entry.target);
        }
      });
    },
    {
      rootMargin: '0px', // 视口的外边距
      threshold: 0.1,   // 元素可见度达到10%时触发
    }
  );

  // 延迟一小段时间，确保DOM元素已渲染
  setTimeout(() => {
    const elementsToAnimate = document.querySelectorAll('.scroll-animate');
    elementsToAnimate.forEach((el) => {
      observer.observe(el);
    });
  }, 100);
});

</script>

<style scoped>
/* 全局容器和字体设置 */
.detail-container {
  background-color: #F2EEE8;
  min-height: 100vh;
  /* 字体保持不变 */
  font-family: "Microsoft YaHei", sans-serif;
}

/* 吸顶头部 */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background-color: #F2EEE8;
  /* 吸顶关键属性 */
  position: sticky;
  top: 0;
  z-index: 10;
  /* 添加一点底部模糊，增强层次感 */
  backdrop-filter: blur(5px);
  background-color: rgba(242, 238, 232, 0.8);
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.back-icon {
  font-size: 24px;
  color: #333;
}

.header-title {
  font-size: 18px;
  font-weight: 500;
  color: #333;
}

.header-right {
  width: 24px;
}

.heart-icon {
  font-size: 24px;
  color: #ccc;
  transition: color 0.3s ease, transform 0.3s ease;
}

.heart-icon.liked {
  color: #ff4757;
  transform: scale(1.1);
}

/* 内容区域 */
.content {
  padding: 8px 16px 24px;
}

/* --- 滚动出现动画 --- */
.scroll-animate {
  opacity: 0;
  transform: translateY(40px);
  transition: opacity 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94), 
              transform 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

/* 为后续卡片添加入场延迟，营造错落感 */
.scroll-animate:nth-child(2) { transition-delay: 0.1s; }
.scroll-animate:nth-child(3) { transition-delay: 0.2s; }
.scroll-animate:nth-child(4) { transition-delay: 0.3s; }

.scroll-animate.is-visible {
  opacity: 1;
  transform: translateY(0);
}

/* 通用卡片基类 */
.info-section, .profile-card {
  background-color: #FFFFFF;
  border-radius: 16px; /* 更大的圆角 */
  padding: 24px;
  margin-bottom: 16px;
  border: 1px solid rgba(217, 217, 217, 0.5); /* 边框更柔和 */
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05); /* 更柔和的阴影 */
  overflow: hidden; /* 防止内部元素溢出 */
}

/* 个人信息卡片 (顶层) */
.profile-card {
  background: linear-gradient(135deg, #ffffff 0%, #fdfcfb 100%);
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: #D9D9D9;
  object-fit: cover;
  border: 3px solid #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.basic-info {
  flex: 1;
}

/* 修改：缩小名称字体 */
.name {
  font-size: 22px; /* 从24px改为22px */
  font-weight: 500;
  color: #333;
  margin: 0 0 8px 0;
}

/* 确保年份、身高、星座在同一行，缩小间距 */
.info-row {
  display: flex;
  flex-wrap: nowrap; /* 禁止换行 */
  gap: 8px; /* 从12px改为8px */
  overflow-x: auto; /* 允许横向滚动 */
  padding-bottom: 4px; /* 给滚动条留空间 */
}

.birth-year, .height, .constellation {
  font-size: 16px;
  color: #6A6A6A;
  background-color: #F7F7F7;
  padding: 4px 10px;
  border-radius: 12px;
  white-space: nowrap; /* 禁止文字换行 */
}

/* 通用区块标题 */
.section-title {
  font-size: 18px;
  font-weight: 500;
  color: #333;
  margin: 0 0 20px 0;
  position: relative;
  padding-left: 14px;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  height: 18px;
  width: 5px;
  background-color: #D9CBBF; /* 调整为更匹配的颜色 */
  border-radius: 3px;
}

/* 信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* 地区信息占据两列宽度 */
.info-item.full-width {
  grid-column: span 2;
}

.label {
  font-size: 14px;
  color: #888; /* 标签颜色变浅 */
}

.value {
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

/* 个人简介 */
.description {
  font-size: 16px;
  color: #444;
  line-height: 1.8; /* 增加行高，提升可读性 */
  margin: 0;
}

/* 照片墙 */
.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(90px, 1fr)); /* 自适应列 */
  gap: 12px;
}

.photo-item {
  aspect-ratio: 1;
  background-color: #D9D9D9;
  border-radius: 12px;
  object-fit: cover;
  width: 100%;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
}

.photo-item:hover {
  transform: scale(1.05); /* 悬浮放大效果 */
  box-shadow: 0 6px 16px rgba(0,0,0,0.15);
}

/* MBTI卡片样式 */
.mbti-card {
  position: relative;
  background: linear-gradient(135deg, #f5f7fa 0%, #e6e9f0 100%);
  border-radius: 12px;
  padding: 20px;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,0.05);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.mbti-character-wrapper {
  position: absolute;
  right: 15px;
  top: 15px;
  z-index: 1;
  filter: drop-shadow(0 6px 12px rgba(0,0,0,0.15));
  transform: translateY(0) rotate(0);
  transition: transform 0.4s ease-out;
}

.mbti-card:hover .mbti-character-wrapper {
  transform: translateY(-8px) rotate(5deg);
}

.mbti-character {
  height: 120px;
  object-fit: contain;
}

.mbti-content {
  position: relative;
  z-index: 2;
  max-width: 70%;
}

.mbti-title {
  font-size: 22px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

/* 新增：MBTI原始类型小字 */
.mbti-subtitle {
  font-size: 14px;
  font-weight: 500;
  color: #7f8c8d;
  margin: 4px 0 12px 0;
  letter-spacing: 1px;
}

.mbti-description {
  font-size: 14px;
  color: #555;
  line-height: 1.6;
  margin: 0 0 16px 0;
  min-height: 40px; /* 保证有足够空间 */
}

/* 修改：重新设计MBTI维度展示 */
.mbti-dimensions {
  margin-top: 20px;
}

.dimension-row {
  display: flex;
  gap: 12px; /* 缩小间距 */
  margin-bottom: 12px; /* 缩小行距 */
}

.dimension {
  flex: 1;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 16px;
  padding: 12px; /* 减少内边距 */
  border: 1px solid rgba(0,0,0,0.05);
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  min-height: 70px; /* 固定高度 */
  display: flex;
  align-items: center;
  justify-content: center;
}

.dimension-options {
  display: flex;
  justify-content: space-between;
  width: 100%;
}

.option {
  font-size: 13px; /* 缩小字体 */
  font-weight: 400;
  color: #999; /* 默认灰色 */
  padding: 6px 8px; /* 调整内边距 */
  border-radius: 12px;
  transition: all 0.3s ease;
  white-space: nowrap; /* 防止文字换行 */
}

.option.active {
  font-weight: bold;
  color: #333; /* 激活状态深色 */
  background-color: rgba(255, 255, 255, 0.9);
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

/* 为不同维度设置不同的激活颜色 */
.dimension:nth-child(1) .option.active {
  color: #FFB344; /* 橙色 */
}
.dimension:nth-child(2) .option.active {
  color: #4A9FF5; /* 蓝色 */
}
.dimension:nth-child(3) .option.active {
  color: #FF6B6B; /* 红色 */
}
.dimension:nth-child(4) .option.active {
  color: #9B59B6; /* 紫色 */
}
</style>