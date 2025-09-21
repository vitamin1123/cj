<template>
  <div class="profile-container">
    <div class="header">
      <van-icon name="arrow-left" class="back-icon" @click="goBack" />
      <span class="header-title">审核资料</span>
      <div class="header-right">
        <van-icon name="passed" class="audit-icon" @click="handleAudit" />
      </div>
    </div>

    <div v-if="userInfo" class="content">
      <!-- 个人资料卡片 -->
      <div class="profile-card">
        <div class="avatar-section">
          <img
            :src="userInfo.avatar ? `/avatars/${userInfo.avatar}` : defaultAvatar"
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
            <span class="label">年收入</span>
            <span class="value">{{ userInfo.income_level + "万元" }}</span>
          </div>
          <div class="info-item" @click.stop="copyPhone(userInfo.phone)">
            <span class="label">手机号码</span>
            <div class="value-container">
              <span class="value">{{ userInfo.phone || '未填写' }}</span>
            </div>
          </div>
          <!-- <div class="info-item">
            <span class="label">MBTI</span>
            <span class="value">{{ userInfo.mbti || '未填写' }}</span>
          </div> -->
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

      <!-- 底部审核按钮 -->
      <div class="audit-footer">
  <van-row gutter="12">
    <van-col span="12">
      <van-button color="#ff5e3a" block round @click="handleReject">
        驳回
      </van-button>
    </van-col>
    <van-col span="12">
      <van-button type="primary" block round @click="handleAudit">
        通过审核
      </van-button>
    </van-col>
  </van-row>
</div>
    </div>

    <!-- 加载/空状态 -->
    <div v-else class="loading">
      <van-loading size="24px">加载中...</van-loading>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '@/plugins/axios'
import { areaList } from '@vant/area-data'
import { showImagePreview, showToast, showDialog, Field  } from 'vant'
import { copyTextToClipboard } from '@/utils/clipboard';

const route = useRoute()
const router = useRouter()
const userInfo = ref<any>(null)
const rejectReason = ref('')
const id = String(route.params.id)

const defaultAvatar = computed(() =>
  userInfo.value?.gender === 'female'
    ? '/avatars/female_def.png'
    : '/avatars/male_def.png'
)

const photoList = computed(() =>
  userInfo.value?.photo
    ? userInfo.value.photo.split(',').filter((p: string) => p.trim()).map((p: string) => `/photo/${p.trim()}`)
    : []
)

const handleReject = async () => {
  try {
    showDialog({
      title: '驳回理由',
      message: () => h('div', { 
        style: 'padding: 16px;' 
      }, [
        // 使用导入的Field组件而不是字符串
        h(Field, {
          modelValue: rejectReason.value,
          'onUpdate:modelValue': (val: string) => rejectReason.value = val,
          placeholder: '请输入驳回原因...',
          type: 'textarea',
          rows: 3,
          autofocus: true,
          style: 'width: 100%; border: 1px solid #eee; border-radius: 4px; padding: 8px;' // 添加内边距
        })
      ]),
      showCancelButton: true,
      confirmButtonText: '确认驳回',
      cancelButtonText: '取消',
      beforeClose: (action) => {
        if (action === 'confirm' && !rejectReason.value.trim()) {
          showToast('理由不能为空');
          return false;
        }
        return true;
      }
    }).then(async () => {
      await apiClient.post(`/api/admin/audit-reject/${id}`, { 
        reason: rejectReason.value 
      });
      showToast('已驳回');
      router.replace('/moderation');
    }).catch(() => {
      rejectReason.value = '';
    });
  } catch (e) {
    if (e !== 'cancel') {
      showToast('操作失败');
    }
  }
}

const previewPhotos = (index: number) =>
  showImagePreview({ images: photoList.value, startPosition: index, closeable: true })

const goBack = () => router.replace('/moderation')

const handleAudit = () => {
  showDialog({
    title: '确认通过',
    message: '确定通过该用户资料审核吗？',
    confirmButtonText: '确认',
    cancelButtonText: '取消'
  }).then(async () => {
    try {
      await apiClient.post(`/api/admin/audit-pass/${id}`)
      showToast('审核通过')
      router.replace('/moderation')
    } catch {
      showToast('操作失败')
    }
  })
}

// 复制电话号码方法
const copyPhone = (phone: string) => {
  copyTextToClipboard(phone)
    .then(() => {
      showToast('电话号码已复制');
    })
    .catch(err => {
      console.error('复制失败:', err);
      showToast('复制失败');
    });
};

// 收入、学历、宗教信仰映射

const educationMap: Record<string, string> = {
  high_school: '高中及以下',
  college: '大专',
  bachelor: '本科',
  master: '硕士',
  phd: '博士'
}
const religionMap: Record<string, string> = {
  buddhism: '佛教',
  christianity: '基督教',
  islam: '伊斯兰教',
  taoism: '道教',
  none: '无宗教信仰',
  other: '其他'
}

// 计算属性

const displayEducation = computed(() => educationMap[userInfo.value?.education] || '未填写')
const displayReligion = computed(() => religionMap[userInfo.value?.religion] || '未填写')

const displayBirthYear = computed(() => {
  if (!userInfo.value?.birth_date) return '--'
  try {
    const date = new Date(userInfo.value.birth_date)
    return isNaN(date.getTime()) ? '--' : date.getFullYear() + '年'
  } catch {
    return '--'
  }
})

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

const displayRegion = computed(() => parseRegion(userInfo.value?.region_code))

const displayConstellation = computed(() => {
  if (!userInfo.value?.birth_date) return '';
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

onMounted(async () => {
  try {
    const userId = router.currentRoute.value.params.id;
    const { data } = await apiClient.get(`/api/admin/audit-detail/${userId}`)
    userInfo.value = data
  } catch {
    showToast('加载失败')
    router.replace('/moderation')
  }
})
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

.audit-icon {
  font-size: 20px;
  color: #333;
  cursor: pointer;
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

.value-container {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 底部审核按钮 */
.audit-footer {
  margin: 24px 16px;
  padding-bottom: env(safe-area-inset-bottom);
}

.van-button {
  height: 44px;
  font-size: 16px;
  font-weight: 500;
  /* background: linear-gradient(to right, #ff9500, #ff5e3a); */
  border: none;
}

/* 加载状态 */
.loading {
  display: flex;
  justify-content: center;
  padding-top: 100px;
}
</style>