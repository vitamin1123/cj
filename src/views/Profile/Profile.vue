<template>
  <div class="profile-container">
    <div class="header">
      <van-icon name="arrow-left" class="back-icon" @click="goBack" />
      <span class="header-title">编号{{ userInfo.id }}
        <span v-if="userInfo.gender === 'male'" class="gender-icon male">♂</span>
        <span v-else-if="userInfo.gender === 'female'" class="gender-icon female">♀</span>
      </span>
      <div class="header-right">
        <van-icon name="share" class="share-icon" @click="handleShare" />
      </div>
    </div>

    <div class="content">
      <!-- 统计卡片区域 - 修复对齐问题 -->
      <div class="stats-container">
        <div class="stat-card">
          <div class="stat-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/></svg>
          </div>
          <div class="stat-value">128</div>
          <div class="stat-label">访问统计</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M20 9c-1.31 0-2.42.83-2.83 2H2v2h15.17c.41 1.17 1.52 2 2.83 2 1.66 0 3-1.34 3-3s-1.34-3-3-3zm0 4c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zM4 5c1.31 0 2.42.83 2.83 2H22v2H6.83C6.42 10.83 5.31 11.66 4 11.66c-1.66 0-3-1.34-3-3s1.34-3 3-3zm0 4c.55 0 1-.45 1-1s-.45-1-1-1-1 .45-1 1 .45 1 1 1z"/></svg>
          </div>
          <div class="stat-value">89</div>
          <div class="stat-label">被访统计</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
          </div>
          <div class="stat-value">42</div>
          <div class="stat-label">点赞统计</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
          </div>
          <div class="stat-value">67</div>
          <div class="stat-label">被赞统计</div>
        </div>
      </div>

      <!-- 个人资料卡片 -->
      <div class="profile-card">
        <div class="avatar-section">
          <img
            :src="userInfo.avatar ? `/avatars/${userInfo.avatar}` : getDefaultAvatarUrl()"
            class="avatar"
          />
          <div class="basic-info">
            <h2 class="name">{{ userInfo.nickname || '未设置昵称' }}</h2>
            <div class="info-row">
              <span class="birth-year">{{ displayBirthYear }}</span>
              <span class="height">{{ userInfo.height || '--' }}cm</span>
              <span class="constellation">{{ displayConstellation }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 基本信息卡片 -->
      <div class="info-section">
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
          <div class="info-item">
            <span class="label">手机号码</span>
            <span class="value">{{ userInfo.phone || '未填写' }}</span>
          </div>
          <div class="info-item">
            <span class="label">MBTI</span>
            <span class="value">{{ userInfo.mbti || '未填写' }}</span>
          </div>
          <div class="info-item full-width">
            <span class="label">地区</span>
            <span class="value">{{ displayRegion }}</span>
          </div>
        </div>
      </div>
      
      <!-- 个人简介卡片 -->
      <div class="info-section" v-if="userInfo.mem">
        <h3 class="section-title">个人简介</h3>
        <p class="description">{{ userInfo.mem }}</p>
      </div>
      
      <!-- 隐私描述卡片 -->
      <div class="info-section" v-if="userInfo.mem_pri">
        <h3 class="section-title">隐私描述</h3>
        <p class="description">{{ userInfo.mem_pri }}</p>
      </div>

      <!-- 照片区域 -->
      <div class="info-section" v-if="userInfo.photo">
        <h3 class="section-title">照片</h3>
        <div class="photo-grid">
          <div 
            v-for="(photoUrl, index) in photoList" 
            :key="index" 
            class="photo-item"
            @click="previewPhotos(index)"
          >
            <img :src="photoUrl" :alt="'User photo ' + (index + 1)">
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { getPreviousRoute } from '@/utils/routeHistory';
import { showImagePreview, showToast } from 'vant';
import { areaList } from '@vant/area-data'; 
import apiClient from '@/plugins/axios';

const router = useRouter();
const route = useRoute();
const userInfo = ref<Record<string, any>>({});
const photoBaseUrl = '/photo/';

// 照片列表
const photoList = computed(() => {
  if (!userInfo.value.photo) return [];
  return userInfo.value.photo.split(',')
    .filter((p: string) => p.trim())
    .map((p: string) => `${photoBaseUrl}${p.trim()}`);
});

// 获取默认头像
const getDefaultAvatarUrl = () => {
  const gender = userInfo.value.gender || 'male';
  return gender === 'male' 
    ? '/avatars/male_def.png' 
    : '/avatars/female_def.png';
};

// 地区映射
const incomeMap: Record<string, string> = { 'below_3k': '3千元以下', '3k_5k': '3千-5千元', '5k_8k': '5千-8千元', '8k_12k': '8千-1.2万元', '12k_20k': '1.2万-2万元', 'above_20k': '2万元以上' };
const educationMap: Record<string, string> = { 'high_school': '高中及以下', 'college': '大专', 'bachelor': '本科', 'master': '硕士', 'phd': '博士' };
const religionMap: Record<string, string> = { 'buddhism': '佛教', 'christianity': '基督教', 'islam': '伊斯兰教', 'taoism': '道教', 'none': '无宗教信仰', 'other': '其他' };

// 解析地区
const parseRegion = (code: string) => {
  if (!code) return '未填写';
  try {
    const provinceCode = code.substring(0, 2) + '0000';
    const cityCode = code.substring(0, 4) + '00';
    const province = areaList.province_list[provinceCode];
    const city = areaList.city_list[cityCode];
    const county = areaList.county_list[code];
    if (province && city && county) return `${province} ${city} ${county}`;
    if (province && city) return `${province} ${city}`;
    if (province) return province;
    return '未知地区';
  } catch (e) {
    console.error('解析地区出错:', e);
    return '未知地区';
  }
};

// 计算属性
const displayRegion = computed(() => parseRegion(userInfo.value.region_code));
const displayIncome = computed(() => incomeMap[userInfo.value.income_level] || '未填写');
const displayEducation = computed(() => educationMap[userInfo.value.education] || '未填写');
const displayReligion = computed(() => religionMap[userInfo.value.religion] || '未填写');

const displayBirthYear = computed(() => {
  if (!userInfo.value.birth_date) return '--';
  try {
    const date = new Date(userInfo.value.birth_date);
    return isNaN(date.getTime()) ? '--' : date.getFullYear() + '年';
  } catch {
    return '--';
  }
});

const displayConstellation = computed(() => {
  if (!userInfo.value.birth_date) return '';
  try {
    const date = new Date(userInfo.value.birth_date);
    if (isNaN(date.getTime())) return '';
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const constellations = [ { name: '摩羯座', start: [1, 20] }, { name: '水瓶座', start: [2, 19] }, { name: '双鱼座', start: [3, 21] }, { name: '白羊座', start: [4, 20] }, { name: '金牛座', start: [5, 21] }, { name: '双子座', start: [6, 22] }, { name: '巨蟹座', start: [7, 23] }, { name: '狮子座', start: [8, 23] }, { name: '处女座', start: [9, 23] }, { name: '天秤座', start: [10, 24] }, { name: '天蝎座', start: [11, 23] }, { name: '射手座', start: [12, 22] }, ];
    for (let i = constellations.length - 1; i >= 0; i--) { 
      if (month > constellations[i].start[0] || (month === constellations[i].start[0] && day >= constellations[i].start[1])) { 
        return constellations[i].name; 
      } 
    }
    return '摩羯座';
  } catch {
    return '';
  }
});

// 预览照片
const previewPhotos = (index: number) => {
  showImagePreview({
    images: photoList.value,
    startPosition: index,
    closeable: true,
  });
};

// 分享功能
const handleShare = () => {
  showToast('分享功能已触发');
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
    router.replace({ path: previousRoute.path, query: previousRoute.query, params: previousRoute.params });
  } else {
    router.replace('/home');
  }
};

onMounted(() => {
  fetchUserData();
});
</script>

<style scoped>
/* 整体容器 */
.profile-container {
  background-color: #F2EEE8;
  min-height: 100vh;
  font-family: "Microsoft YaHei", sans-serif;
  font-size: 87.5%; /* 基础字体大小调整为3级 */
}

/* 头部样式 */
.header {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  background-color: #F2EEE8;
  position: sticky;
  top: 0;
  z-index: 10;
  backdrop-filter: blur(5px);
  background-color: rgba(242, 238, 232, 0.8);
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.back-icon {
  font-size: 20px;
  color: #333;
  margin-right: 12px;
}

.header-title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  flex: 1;
  display: flex;
  align-items: center;
}

.header-right {
  width: 24px;
}

.share-icon {
  font-size: 20px;
  color: #333;
}

/* 性别图标 */
.gender-icon {
  margin-left: 6px;
  font-weight: bold;
  font-size: 1.1em;
}

.male {
  color: #2c7be5; /* 男性蓝色 */
}

.female {
  color: #e83e8c; /* 女性粉色 */
}

/* 统计卡片容器 - 修复对齐问题 */
.stats-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  padding: 0 0 12px; /* 移除左右内边距 */
}

.stat-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 14px 8px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(217, 217, 217, 0.3);
  /* 确保卡片宽度一致 */
  min-width: 0;
  overflow: hidden;
}

.stat-icon {
  width: 28px;
  height: 28px;
  margin: 0 auto 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #F7F5F2;
  border-radius: 50%;
}

.stat-icon svg {
  width: 16px;
  height: 16px;
  color: #D9CBBF;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stat-label {
  font-size: 11px;
  color: #888;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 内容区域 */
.content {
  padding: 0 16px 24px;
}

/* 个人资料卡片 */
.profile-card {
  background-color: #FFFFFF;
  border-radius: 16px;
  padding: 18px;
  margin-bottom: 12px;
  border: 1px solid rgba(217, 217, 217, 0.3);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background-color: #D9D9D9;
  object-fit: cover;
  border: 3px solid #fff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.basic-info {
  flex: 1;
}

.name {
  font-size: 18px;
  font-weight: 500;
  color: #333;
  margin: 0 0 6px 0;
}

.info-row {
  display: flex;
  flex-wrap: nowrap;
  gap: 6px;
  overflow-x: auto;
  padding-bottom: 2px;
}

.birth-year, .height, .constellation {
  font-size: 13px;
  color: #6A6A6A;
  background-color: #F7F7F7;
  padding: 3px 8px;
  border-radius: 10px;
  white-space: nowrap;
}

/* 信息卡片 */
.info-section {
  background-color: #FFFFFF;
  border-radius: 16px;
  padding: 18px;
  margin-bottom: 12px;
  border: 1px solid rgba(217, 217, 217, 0.3);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
}

.section-title {
  font-size: 15px;
  font-weight: 500;
  color: #333;
  margin: 0 0 16px 0;
  position: relative;
  padding-left: 12px;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  height: 16px;
  width: 4px;
  background-color: #D9CBBF;
  border-radius: 2px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0; /* 防止内容溢出 */
}

.info-item.full-width {
  grid-column: span 2;
}

.label {
  font-size: 12px;
  color: #888;
  white-space: nowrap;
}

.value {
  font-size: 14px;
  color: #333;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.description {
  font-size: 14px;
  color: #444;
  line-height: 1.6;
  margin: 0;
}

/* 照片网格 */
.photo-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.photo-item {
  position: relative;
  aspect-ratio: 1 / 1;
  border-radius: 10px;
  overflow: hidden;
  background-color: #e9e5e0;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.photo-item:hover {
  transform: scale(1.03);
}

.photo-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
</style>