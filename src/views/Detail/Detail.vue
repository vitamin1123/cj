<template>
  <div class="detail-container">
    <!-- 返回按钮 -->
    <div class="header">
      <van-icon name="arrow-left" class="back-icon" @click="goBack" />
      <span class="header-title">详细信息</span>
      <div class="header-right">
        <van-icon name="like" class="heart-icon" :class="{ liked: isLiked }" @click="toggleLike" />
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="content">
      <!-- 头像和基本信息 -->
      <div class="profile-card">
        <div class="avatar-section">
          <div class="avatar"></div>
          <div class="basic-info">
            <h2 class="name">{{ userInfo.name }}</h2>
            <div class="age-height">
              <span class="age">{{ userInfo.age }}岁</span>
              <span class="height">{{ userInfo.height }}cm</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 详细信息标签 -->
      <div class="info-section">
        <h3 class="section-title">基本信息</h3>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">职业</span>
            <span class="value">{{ userInfo.occupation }}</span>
          </div>
          <div class="info-item">
            <span class="label">学历</span>
            <span class="value">{{ userInfo.education }}</span>
          </div>
          <div class="info-item">
            <span class="label">地区</span>
            <span class="value">{{ userInfo.location }}</span>
          </div>
          <div class="info-item">
            <span class="label">星座</span>
            <span class="value">{{ userInfo.constellation }}</span>
          </div>
        </div>
      </div>

      <!-- 兴趣爱好 -->
      <div class="info-section">
        <h3 class="section-title">兴趣爱好</h3>
        <div class="tags">
          <span v-for="hobby in userInfo.hobbies" :key="hobby" class="tag">{{ hobby }}</span>
        </div>
      </div>

      <!-- 个人简介 -->
      <div class="info-section">
        <h3 class="section-title">个人简介</h3>
        <p class="description">{{ userInfo.description }}</p>
      </div>

      <!-- 照片展示 -->
      <div class="info-section">
        <h3 class="section-title">照片</h3>
        <div class="photo-grid">
          <div v-for="i in 6" :key="i" class="photo-item"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isLiked = ref(false);

// 模拟用户数据
const userInfo = ref({
  name: '张小美',
  age: 25,
  height: 165,
  occupation: '设计师',
  education: '本科',
  location: '北京朝阳区',
  constellation: '天秤座',
  hobbies: ['旅行', '摄影', '美食', '读书', '瑜伽'],
  description: '热爱生活，喜欢探索新鲜事物。工作之余喜欢旅行和摄影，记录生活中的美好瞬间。希望能遇到志同道合的朋友一起分享生活的点点滴滴。'
});

const goBack = () => {
  router.replace('/explore');
};

const toggleLike = () => {
  isLiked.value = !isLiked.value;
};
</script>

<style scoped>
.detail-container {
  background-color: #F2EEE8;
  min-height: 100vh;
  font-family: "Microsoft YaHei", sans-serif;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background-color: #F2EEE8;
  position: sticky;
  top: 0;
  z-index: 10;
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
  transition: color 0.3s;
}

.heart-icon.liked {
  color: #ff4757;
}

.content {
  padding: 0 16px 16px;
}

.profile-card {
  background-color: #FFFFFF;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  border: 1px solid #D9D9D9;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: #D9D9D9;
}

.basic-info {
  flex: 1;
}

.name {
  font-size: 24px;
  font-weight: 500;
  color: #333;
  margin: 0 0 8px 0;
}

.age-height {
  display: flex;
  gap: 16px;
}

.age, .height {
  font-size: 16px;
  color: #6A6A6A;
}

.info-section {
  background-color: #FFFFFF;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  border: 1px solid #D9D9D9;
}

.section-title {
  font-size: 18px;
  font-weight: 500;
  color: #333;
  margin: 0 0 16px 0;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.label {
  font-size: 14px;
  color: #6A6A6A;
}

.value {
  font-size: 16px;
  color: #333;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  background-color: #EBE3D7;
  color: #333;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 14px;
}

.description {
  font-size: 16px;
  color: #333;
  line-height: 1.6;
  margin: 0;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.photo-item {
  aspect-ratio: 1;
  background-color: #D9D9D9;
  border-radius: 8px;
}
</style>