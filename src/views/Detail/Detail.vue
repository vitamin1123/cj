<template>
  <div class="detail-container">
    <div class="header">
      <van-icon name="arrow-left" class="back-icon" @click="goBack" />
      <span class="header-title">编号{{ userInfo.id }}
        <!-- 新增性别图标 -->
        <span v-if="userInfo.gender === 'male'" class="gender-icon male">♂</span>
        <span v-else-if="userInfo.gender === 'female'" class="gender-icon female">♀</span>
      </span>
      <div class="header-right">
        <van-icon name="like" class="heart-icon" :class="{ liked: isLocalLiked }" @click="toggleLike" />
      </div>
    </div>

    <div class="content">
      <div class="profile-card scroll-animate">
        <div class="avatar-section">
  <div class="avatar-container">
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
    <!-- 等级徽章：以头像为参照 -->
    <img
      class="level-badge"
      :src="getLevelIcon(userInfo.points ?? 0)"
      alt="level"
    />
  </div>

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
            <div class="mbti-dimensions">
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

      <div class="info-section scroll-animate" v-if="userInfo.first_photo">
        <h3 class="section-title">照片</h3>
        
        <div class="photo-gallery-container">
          <div v-if="!isUnlocked" class="glass-overlay">
            <div class="gradient-border"></div>
            <div class="unlock-status">
              <div class="heart-status">
                <span :class="{ 'liked': userInfo.they_liked }">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="like-heart-icon"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
                  对方{{ userInfo.they_liked ? '已' : '未' }}解锁
                </span>
                <span :class="{ 'liked': userInfo.i_liked }">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="like-heart-icon"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
                  我{{ userInfo.i_liked ? '已' : '未' }}解锁
                </span>
              </div>
 
            </div>

            <!-- 新增：毛玻璃中的照片孔洞 -->
            <div class="photo-hole" :style="holePositionStyle">
              <img :src="photoBaseUrl + userInfo.first_photo" alt="User photo 1">
              <div class="photo-vignette"></div>
            </div>
          </div>

          <div class="new-photo-grid">
            <template v-if="!isUnlocked">
              
              <div v-for="i in 6" :key="'placeholder-' + i" class="new-photo-item placeholder"></div>
            </template>
            <template v-else>
              <div v-for="(photoUrl, index) in unlockedPhotoList" :key="index" class="new-photo-item" @click="previewUnlockedPhotos(index)">
                <img :src="photoUrl" :alt="'User photo ' + (index + 1)">
              </div>
            </template>
          </div>
        </div>
      </div>

    </div>
    <van-floating-bubble
      v-model:offset="bubbleOffset"
      icon="share"
      magnetic="x"
      @click="handleShare"
      style="--van-floating-bubble-background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);"
    />
    <div v-if="showShareGuide" class="share-guide-overlay" @click="showShareGuide = false">
      <!-- 扇形遮罩 -->
      <div class="sector-mask"></div>
      
      <!-- 右上角高亮区域 -->
      <div class="highlight-area">
        <div class="dot-animation"></div>
      </div>
      
      <!-- 提示文字 -->
      <div class="guide-text">
        点击右上角<span class="icon-more"></span><br>
        分享给朋友
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute  } from 'vue-router';
import { getPreviousRoute } from '@/utils/routeHistory';
import { showImagePreview, showToast, ShareSheet   } from 'vant';
import { areaList } from '@vant/area-data'; 
import apiClient from '@/plugins/axios';
import { likeUser } from '@/api/like';
import { useLikeStore } from '@/store/likeStore';
import { useUrlStore } from '@/store/urlStore'
import { initWechatSDK, setWechatShareInfo } from '@/utils/wechat';
import { getLevelIcon } from '@/utils/levelIcon';

const showShareGuide = ref(false); // 控制扇形遮罩引导
const likeStore = useLikeStore();
const router = useRouter();
const route = useRoute();
const userInfo = ref<Record<string, any>>({});
const photoBaseUrl = '/photo/'; // 统一的照片基础路径
const bubbleOffset = ref({ x: 0.85 * window.innerWidth, y: 0.8 * window.innerHeight });
// --- 核心修改：照片墙相关计算属性 ---

// 判断照片墙是否解锁
const isUnlocked = computed(() => {
  // 使用 ?. 可选链操作符防止 userInfo 为空时报错
  return userInfo.value?.they_liked && userInfo.value?.i_liked;
});

// 解锁后要展示的照片列表
const unlockedPhotoList = computed(() => {
  if (!userInfo.value.photo) return [];
  return userInfo.value.photo.split(',')
    .filter((p: string) => p.trim())
    .map((p: string) => `${photoBaseUrl}${p.trim()}`);
});

// --- 原始脚本内容 (保留) ---
const holePositionStyle = computed(() => {
  return {
    'grid-row': '1',
    'grid-column': '1'
  };
});
const isLocalLiked = computed(() => {
  const userId = parseInt(router.currentRoute.value.params.id as string);
  return likeStore.hasLiked(userId);
});


const isWechatInitialized = ref(false);
// 新增：处理分享
const handleShare = async () => {
  try {
    // 防止重复初始化
    if (isWechatInitialized.value) {
      showShareGuide.value = true;
      return;
    }
    
    
    
    // 2. 初始化微信SDK
    await initWechatSDK();
    isWechatInitialized.value = true;
    // 3. 设置分享内容
    const shareTitle = `编号${userInfo.value.id} ${userInfo.value.birth_date ? new Date(userInfo.value.birth_date).getFullYear() : ''}年`;
    let shareDesc = userInfo.value.mem || '暂无个人简介';
    if (shareDesc.length > 20) {
      shareDesc = shareDesc.substring(0, 20) + '...';
    }
    const shareImg = userInfo.value.first_photo 
      ? `${window.location.origin}/photo/${userInfo.value.first_photo}`
      : `${window.location.origin}/tianshun.jpg`;
    const urlStore = useUrlStore()
    const shareLink = urlStore.currentUrl
    // const shareLink = `${window.location.origin}/detail/${route.params.id}`;
    console.log('shareLink', shareLink,shareImg)
    setWechatShareInfo({
      title: shareTitle,
      desc: shareDesc,
      link: shareLink,
      imgUrl: shareImg,
      // success: () => showToast('分享成功'),
      // cancel: () => showToast('分享已取消')
    });
    showShareGuide.value = true;
    // showToast('点击右上角分享给朋友');
  } catch (error) {
    console.error('微信分享失败:', error);
    showToast('分享功能初始化失败，请再次尝试');
  }
};


const getDefaultAvatarUrl = () => {
  const gender = userInfo.value.gender || 'male';
  return gender === 'male' 
    ? '/avatars/male_def.png' 
    : '/avatars/female_def.png';
};

const incomeMap: Record<string, string> = { 'below_3k': '3千元以下', '3k_5k': '3千-5千元', '5k_8k': '5千-8千元', '8k_12k': '8千-1.2万元', '12k_20k': '1.2万-2万元', 'above_20k': '2万元以上' };
const educationMap: Record<string, string> = { 'high_school': '高中及以下', 'college': '大专', 'bachelor': '本科', 'master': '硕士', 'phd': '博士' };
const religionMap: Record<string, string> = { 'buddhism': '佛教', 'christianity': '基督教', 'islam': '伊斯兰教', 'taoism': '道教', 'none': '无宗教信仰', 'other': '其他' };

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
    for (let i = constellations.length - 1; i >= 0; i--) { if (month > constellations[i].start[0] || (month === constellations[i].start[0] && day >= constellations[i].start[1])) { return constellations[i].name; } }
    return '摩羯座';
  } catch {
    return '';
  }
});

const mbtiChineseName = computed(() => {
  if (!userInfo.value.mbti) return '';
  const mbtiMap: Record<string, string> = { 'INTJ': '建筑师', 'INTP': '逻辑学家', 'ENTJ': '指挥官', 'ENTP': '辩论家', 'INFJ': '倡导者', 'INFP': '调停者', 'ENFJ': '主人公', 'ENFP': '竞选者', 'ISTJ': '物流师', 'ISFJ': '守卫者', 'ESTJ': '总经理', 'ESFJ': '执政官', 'ISTP': '鉴赏家', 'ISFP': '探险家', 'ESTP': '企业家', 'ESFP': '表演者' };
  return mbtiMap[userInfo.value.mbti.toUpperCase()] || userInfo.value.mbti;
});

const mbtiDescription = computed(() => {
  if (!userInfo.value.mbti) return '';
  const descMap: Record<string, string> = { 'INTP': '充满奇思妙想的革新者，对知识有着永不满足的渴望。', 'INTJ': '富有远见的战略家，擅长系统性地规划未来方向。', 'INFJ': '富有同理心的引导者，善于理解他人并推动积极改变。', 'INFP': '充满诗意的理想主义者，始终追寻内心的价值与意义。', 'ENTJ': '果敢的领导者，热衷于制定宏大目标并推动团队达成。', 'ENTP': '机智的挑战者，喜欢用创新思维解决复杂问题。', 'ENFJ': '热情的催化剂，擅长激励他人并建立和谐的合作关系。', 'ENFP': '充满活力的探索者，凭借创造力与热情感染周围的人。', 'ISTJ': '严谨的守护者，以责任感与专注度确保任务高质量完成。', 'ISTP': '务实的行动派，擅长通过实践探索解决问题的最佳路径。', 'ISFJ': '温暖的支持者，默默为他人提供细致入微的关怀。', 'ISFP': '敏感的艺术家，善于用美感与情感创造独特体验。', 'ESTJ': '高效的组织者，以强大的执行力维持系统的有序运行。', 'ESTP': '大胆的冒险者，在挑战与变化中展现卓越的适应能力。', 'ESFJ': '亲切的协调者，致力于维护和谐的人际关系与社会联结。', 'ESFP': '活力四射的表演者，享受与人互动并创造欢乐氛围。' };
  return descMap[userInfo.value.mbti.toUpperCase()] || '富有洞察力与好奇心的思考者。';
});

const mbtiFirstChar = computed(() => userInfo.value.mbti?.charAt(0).toUpperCase() || '');
const mbtiSecondChar = computed(() => userInfo.value.mbti?.charAt(1).toUpperCase() || '');
const mbtiThirdChar = computed(() => userInfo.value.mbti?.charAt(2).toUpperCase() || '');
const mbtiFourthChar = computed(() => userInfo.value.mbti?.charAt(3).toUpperCase() || '');

const getMbtiImage = (mbti: string) => `/mbti-images/${mbti.toLowerCase()}.png`;

// --- 方法 (Methods) ---

// 新增：预览单张被提升的照片
const previewSinglePhoto = (photoUrl: string) => {
  showImagePreview({
    images: [photoUrl],
    startPosition: 0,
    closeable: true,
  });
};

// 修改：预览解锁后的照片列表
const previewUnlockedPhotos = (index: number) => {
  showImagePreview({
    images: unlockedPhotoList.value,
    startPosition: index,
    closeable: true,
  });
};

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

const goBack = () => {
  const previousRoute = getPreviousRoute();
  if (previousRoute) {
    router.replace({ path: previousRoute.path, query: previousRoute.query, params: previousRoute.params });
  } else {
    router.replace('/home');
  }
};

const toggleLike = async () => {
  try {
    const userId = parseInt(router.currentRoute.value.params.id as string);
    const action = isLocalLiked.value ? 'unlike' : 'like';
    await likeUser(userId, action);
    if (action === 'like') {
      likeStore.addLike(userId);
    } else {
      likeStore.removeLike(userId);
    }
    showToast(isLocalLiked.value ? '已喜欢' : '已取消');
    await fetchUserData();
  } catch (error) {
    console.error('操作失败:', error);
    showToast('操作失败');
  }
};

onMounted(() => {
  fetchUserData();
  const observer = new IntersectionObserver( (entries) => { entries.forEach((entry) => { if (entry.isIntersecting) { entry.target.classList.add('is-visible'); observer.unobserve(entry.target); } }); }, { rootMargin: '0px', threshold: 0.1, } );
  setTimeout(() => {
    const elementsToAnimate = document.querySelectorAll('.scroll-animate');
    elementsToAnimate.forEach((el) => { observer.observe(el); });
  }, 100);
});
</script>

<style scoped>
/* --- 原始样式 (大部分保留) --- */
.detail-container { background-color: #F2EEE8; min-height: 100vh; font-family: "Microsoft YaHei", sans-serif; }
.header { display: flex; align-items: center; justify-content: space-between; padding: 16px; background-color: #F2EEE8; position: sticky; top: 0; z-index: 10; backdrop-filter: blur(5px); background-color: rgba(242, 238, 232, 0.8); border-bottom: 1px solid rgba(0,0,0,0.05); }
.back-icon { font-size: 24px; color: #333; }
.header-title { font-size: 18px; font-weight: 500; color: #333; }
.header-right { width: 24px; }
.heart-icon { font-size: 24px; color: #ccc; transition: color 0.3s ease, transform 0.3s ease; }
.heart-icon.liked { color: #ff4757; transform: scale(1.1); }
.content { padding: 8px 16px 24px; }
.scroll-animate { opacity: 0; transform: translateY(40px); transition: opacity 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94), transform 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94); }
.scroll-animate:nth-child(2) { transition-delay: 0.1s; }
.scroll-animate:nth-child(3) { transition-delay: 0.2s; }
.scroll-animate:nth-child(4) { transition-delay: 0.3s; }
.scroll-animate.is-visible { opacity: 1; transform: translateY(0); }
.info-section, .profile-card { background-color: #FFFFFF; border-radius: 16px; padding: 24px; margin-bottom: 16px; border: 1px solid rgba(217, 217, 217, 0.5); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05); overflow: hidden; }
.profile-card { background: linear-gradient(135deg, #ffffff 0%, #fdfcfb 100%); }
.avatar-section { display: flex; align-items: center; gap: 20px; }
.avatar { width: 80px; height: 80px; border-radius: 50%; background-color: #D9D9D9; object-fit: cover; border: 3px solid #fff; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.basic-info { flex: 1; }
.name { font-size: 22px; font-weight: 500; color: #333; margin: 0 0 8px 0; }
.info-row { display: flex; flex-wrap: nowrap; gap: 8px; overflow-x: auto; padding-bottom: 4px; }
.birth-year, .height, .constellation { font-size: 16px; color: #6A6A6A; background-color: #F7F7F7; padding: 4px 10px; border-radius: 12px; white-space: nowrap; }
.section-title { font-size: 18px; font-weight: 500; color: #333; margin: 0 0 20px 0; position: relative; padding-left: 14px; }
.section-title::before { content: ''; position: absolute; left: 0; top: 50%; transform: translateY(-50%); height: 18px; width: 5px; background-color: #D9CBBF; border-radius: 3px; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px 16px; }
.info-item { display: flex; flex-direction: column; gap: 6px; }
.info-item.full-width { grid-column: span 2; }
.label { font-size: 14px; color: #888; }
.value { font-size: 16px; color: #333; font-weight: 500; }
.description { font-size: 16px; color: #444; line-height: 1.8; margin: 0; }
.mbti-card { position: relative; background: linear-gradient(135deg, #f5f7fa 0%, #e6e9f0 100%); border-radius: 12px; padding: 20px; overflow: hidden; border: 1px solid rgba(0,0,0,0.05); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.mbti-character-wrapper { position: absolute; right: 15px; top: 15px; z-index: 1; filter: drop-shadow(0 6px 12px rgba(0,0,0,0.15)); transform: translateY(0) rotate(0); transition: transform 0.4s ease-out; }
.mbti-card:hover .mbti-character-wrapper { transform: translateY(-8px) rotate(5deg); }
.mbti-character { height: 120px; object-fit: contain; }
.mbti-content { position: relative; z-index: 2; max-width: 70%; }
.mbti-title { font-size: 22px; font-weight: 600; color: #2c3e50; margin: 0; }
.mbti-subtitle { font-size: 14px; font-weight: 500; color: #7f8c8d; margin: 4px 0 12px 0; letter-spacing: 1px; }
.mbti-description { font-size: 14px; color: #555; line-height: 1.6; margin: 0 0 16px 0; min-height: 40px; }
.mbti-dimensions { margin-top: 20px; }
.dimension-row { display: flex; gap: 12px; margin-bottom: 12px; }
.dimension { flex: 1; background: rgba(255, 255, 255, 0.7); border-radius: 16px; padding: 12px; border: 1px solid rgba(0,0,0,0.05); box-shadow: 0 2px 4px rgba(0,0,0,0.05); min-height: 70px; display: flex; align-items: center; justify-content: center; }
.dimension-options { display: flex; justify-content: space-between; width: 100%; }
.option { font-size: 13px; font-weight: 400; color: #999; padding: 6px 8px; border-radius: 12px; transition: all 0.3s ease; white-space: nowrap; }
.option.active { font-weight: bold; color: #333; background-color: rgba(255, 255, 255, 0.9); box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.dimension:nth-child(1) .option.active { color: #FFB344; }
.dimension:nth-child(2) .option.active { color: #4A9FF5; }
.dimension:nth-child(3) .option.active { color: #FF6B6B; }
.dimension:nth-child(4) .option.active { color: #9B59B6; }
/* 新增性别图标样式 */
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

/* === 照片边缘透明效果 === */
.lift-up {
  position: relative;
  overflow: hidden;
  z-index: 20;
  transform: scale(1.05);
  box-shadow: none !important;
}

.edge-blur {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(
    circle at center, 
    rgba(255, 255, 255, 0) 0%, 
    rgba(255, 255, 255, 0) 40%, 
    rgba(255, 255, 255, 0.85) 100%
  );
  pointer-events: none;
  border-radius: 12px;
}

.lift-up:hover .edge-blur {
  background: radial-gradient(
    circle at center, 
    rgba(255, 255, 255, 0) 0%, 
    rgba(255, 255, 255, 0) 30%, 
    rgba(255, 255, 255, 0.92) 100%
  );
}

/* === 全新照片墙部分的专属样式 === */

.photo-gallery-container {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
}

.glass-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 10;
  background-color: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(25px);
  -webkit-backdrop-filter: blur(25px);
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 8px;
  padding: 0;
  clip-path: none;
  border-radius: 16px;
}

.photo-hole {
  position: relative;
  aspect-ratio: 1 / 1;
  border-radius: 12px;
  overflow: hidden;
  background-color: transparent;
  z-index: 15;
}

.photo-hole img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.photo-vignette {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(
    circle at center, 
    rgba(255, 255, 255, 0) 0%, 
    rgba(255, 255, 255, 0) 40%, 
    rgba(255, 255, 255, 0.9) 100%
  );
  pointer-events: none;
  border-radius: 12px;
}

.unlock-status {
  position: absolute;
  bottom: 40px;
  left: 0;
  right: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  z-index: 20;
}

.glass-overlay-bak {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 10;
  overflow: hidden;
  background-color: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(25px);
  -webkit-backdrop-filter: blur(25px);
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
  
  /* 新增：异型遮罩裁剪 */
  clip-path: polygon(
    0 0, 100% 0, 100% 100%, 0 100%, 0 0,
    calc(33.33% + 8px) 0, 
    calc(33.33% + 8px) calc(33.33% + 8px),
    calc(100% - 8px) calc(33.33% + 8px),
    calc(100% - 8px) 100%, 
    8px 100%, 
    8px calc(33.33% + 8px), 
    calc(33.33% + 8px) calc(33.33% + 8px),
    calc(33.33% + 8px) 0
  );
  
  /* 圆角效果 */
  border-radius: 16px;
}

/* 新增流光边框 */
.gradient-border {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, 
    #ff9a9e, #fad0c4, #fad0c4, 
    #a18cd1, #fbc2eb, #ff9a9e,
    #a1c4fd, #c2e9fb, #c2e9fb);
  background-size: 300% 300%;
  z-index: -1;
  animation: gradientShift 64s ease infinite;
  border-radius: 18px;
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.unlock-status {
  display: flex;
  flex-direction: column;
  gap: 16px;
  /* 下移文字 */
  margin-top: 80px;
}

.heart-status {
  display: flex;
  justify-content: center;
  gap: 24px;
  font-size: 1rem;
  font-weight: 600;
}

.heart-status span {
  display: flex;
  align-items: center;
  gap: 6px;
  color: rgba(0, 0, 0, 0.4);
}

.heart-status span.liked {
  color: #ff3b30;
}

.like-heart-icon {
  width: 20px;
  height: 20px;
}



.new-photo-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 8px;
}

.new-photo-item {
  position: relative;
  aspect-ratio: 1 / 1;
  border-radius: 12px;
  background-color: #e9e5e0; /* 占位符颜色与背景更协调 */
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.new-photo-item:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
}

.new-photo-item.lift-up {
  box-shadow: none;
  transform: scale(1.05);
}

.new-photo-item.placeholder {
  background-color: #e9e5e0;
  opacity: 0.65;
  position: relative;
}

.new-photo-item.placeholder::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(
    circle at center, 
    rgba(255, 255, 255, 0) 0%, 
    rgba(255, 255, 255, 0) 30%, 
    rgba(255, 255, 255, 0.8) 100%
  );
  pointer-events: none;
  border-radius: 12px;
}
.new-photo-item.placeholder:hover {
  transform: none;
  box-shadow: none;
}



.new-photo-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* 新增：照片透出效果样式 */
.lightbox-effect {
  position: relative;
  overflow: hidden;
}

.lightbox-effect::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
  background: radial-gradient(
    circle at center, 
    rgba(255, 255, 255, 0) 0%, 
    rgba(255, 255, 255, 0) 40%, 
    rgba(255, 255, 255, 0.8) 100%
  );
  pointer-events: none;
}

.lightbox-effect:hover::before {
  background: radial-gradient(
    circle at center, 
    rgba(255, 255, 255, 0) 0%, 
    rgba(255, 255, 255, 0) 30%, 
    rgba(255, 255, 255, 0.9) 100%
  );
}

/* 调整照片的层级关系 */
.new-photo-item.lightbox-effect {
  z-index: 20;
  box-shadow: none;
  transform: scale(1.05);
}

/* 新增：浮动气泡样式调整 */
:deep(.van-floating-bubble) {
  z-index: 9999;
  box-shadow: 0 4px 12px rgba(255, 154, 158, 0.5);
}

:deep(.van-floating-bubble__icon) {
  color: white;
  font-size: 20px;
}

/* 扇形遮罩引导样式 */
.share-guide-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  z-index: 9998;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  padding: 20px;
}

.sector-mask {
  position: absolute;
  top: 0;
  right: 0;
  width: 150px;
  height: 150px;
 
  pointer-events: none;
}

.highlight-area {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: pulse 2s infinite;
}

.dot-animation {
  width: 20px;
  height: 20px;
  background: #ff4757;
  border-radius: 50%;
  animation: bounce 1.5s infinite;
}

.guide-text {
  position: absolute;
  top: 70px;
  right: 20px;
  color: white;
  font-size: 18px;
  font-weight: bold;
  text-align: right;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  animation: fadeInOut 2s infinite;
}

.icon-more {
  display: inline-block;
  font-size: 24px;
  font-weight: bold;
  transform: rotate(90deg);
  margin: 0 5px;
}

/* 动画效果 */
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(255, 71, 87, 0.4);
  }
  70% {
    box-shadow: 0 0 0 20px rgba(255, 71, 87, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(255, 71, 87, 0);
  }
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-15px);
  }
}

@keyframes fadeInOut {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.avatar-container {
  position: relative;
  width: 80px;      /* 与头像同宽高 */
  height: 80px;
  flex-shrink: 0;
}

.level-badge {
  position: absolute;
  top: -4px;        /* 向上微移，叠出边缘 */
  right: -4px;      /* 向右微移，叠出边缘 */
  width: 36px;
  height: 20px;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(0,0,0,.2);
  z-index: 2;
  pointer-events: none;
}

</style>