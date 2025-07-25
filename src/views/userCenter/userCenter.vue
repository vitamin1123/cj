<template>
  <div class="user-center-container">
    <!-- 页面内容 -->
    <div class="page-content">
      <!-- 顶部卡片 -->
      <div class="profile-card">
        <div class="profile-content">
          <div class="avatar-wrapper" @click="handleAvatarClick" :class="{ 'disabled-avatar': !paymentStore.isPaid }">
            <div class="avatar" :style="{ backgroundImage: `url(${user.avatarUrl})` }">
              <div v-if="!user.avatarUrl" class="avatar-placeholder">+</div>
            </div>
            <img
              class="level-below"
              :src="getLevelIcon(currentPoints)"
              alt="level"
              @click.stop="showLevelPopover = true"
            />

            <!-- <div v-if="!paymentStore.isPaid" class="edit-hint">升级会员解锁</div>
            <div v-else class="edit-hint">点击编辑</div> -->
          </div>
        <van-popup
          v-model:show="showLevelPopover"
          round
          position="center"
          :style="{ width: '280px', padding: '24px' }"
        >
          <div class="level-header">
            <span class="current-score">{{ currentPoints }} 分</span>
            
          </div>

          <div class="progress-bar">
            <img :src="getLevelIcon(prevLevel.points)" class="level-thumb" />
            <div class="track">
              <div class="fill" :style="{ width: progress + '%' }"></div>
            </div>
            <img :src="getLevelIcon(nextLevel.points)" class="level-thumb" />
          </div>

          <div class="level-list">
            <div
              v-for="item in levelList.slice(1)"
              :key="item.level"
              class="level-row"
              :class="{ active: item.level === curLevel }"
            >
              <img :src="getLevelIcon(item.points)" class="level-icon" />
              <span class="level-name">Lv.{{ item.level }}</span>
              <span class="level-points">{{ item.points }}分</span>
            </div>
          </div>
      </van-popup>
          <div class="profile-info">
            <div class="nickname-container">
              <div v-if="!isEditingNickname" class="nickname" :class="{ 'disabled-nickname': !paymentStore.isPaid }"
                @click="handleNicknameClick">
                {{ user.nickname }}
              </div>
              <div v-else class="nickname-edit">
                <input 
                  v-model="tempNickname" 
                  @blur="saveNickname" 
                  @keyup.esc="cancelEdit"
                  maxlength="10"
                  class="nickname-input"
                  ref="nicknameInput"
                />
                <div class="char-count">{{ tempNickname.length }}/10</div>
              </div>
            </div>
            <div class="stats">
              <div class="stat-item">
                <div class="stat-number">{{ likes.ilikeCount }}</div>
                <div class="stat-label">我喜欢的</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ likes.likemeCount }}</div>
                <div class="stat-label">喜欢我的</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ recentVisitorsCount  }}</div>
                <div class="stat-label">最近来访</div>
              </div>
            </div>
          </div>
        </div>
      </div>
        <van-notice-bar
          v-if="showRejectionNotice && rejectionInfo"
          left-icon="warning-o"
          color="#1989fa"
          background="#ecf9ff"
          mode="closeable"
          @close="markRejectionAsRead"
        >
          <span style="font-weight: bold; color: #ff6b6b;">资料审核未通过：</span>
          {{ rejectionInfo.reason }}
        </van-notice-bar>
      <!-- 管理菜单卡片 -->
      <div class="menu-card">
        <h2 class="section-title">管理</h2>
        <div class="menu-items">
          <div 
            v-for="item in menuItems" 
            :key="item.id" 
            class="menu-item"
            @click="item.route ? router.replace(item.route) : item.action && item.action()"
          >
            {{ item.label }}
          </div>
        </div>
      </div>
    </div>

    <!-- 底部TabBar -->
    <TabBar 
      :active-tab="activeTab" 
      @update:active-tab="activeTab = $event"
      :tabs="tabs"
    />
    
    <!-- 头像选择器 -->
    <input 
      ref="avatarInput" 
      type="file" 
      accept="image/*" 
      @change="handleAvatarChange" 
      style="display: none;"
    />

    <!-- 照片上传弹出层 -->
    <van-popup v-model:show="showPhotoPopup" round position="bottom" :style="{ height: '60%' }">
      <div class="photo-upload-container">
        <div class="popup-header">
          <h2>我的照片</h2>
          <van-button round type="primary" @click="showPhotoPopup = false">完成</van-button>
        </div>
        
        <div class="photos-container">
          <!-- 使用van-uploader的原始样式  @oversize="onOversize"-->
          <van-uploader
            v-model="fileList"
            :after-read="afterRead"
            :before-read="beforeRead"
            :max-count="6"
            :max-size="5 * 1024 * 1024"
            multiple
            
            @delete="deletePhoto"
          >
            <!-- 使用van-uploader默认的预览和删除按钮 -->
          </van-uploader>
        </div>
        
        <div class="upload-tips">
          <p>最多可上传6张照片</p>
          <p>第一张公开显示，剩下的展示给互相喜欢的用户</p>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { Toast, showToast, showLoadingToast, closeToast  } from 'vant';
import apiClient from '@/plugins/axios';
import { useAuthStore } from '@/store/authStore';
import { useUserInfoStore } from '@/store/userinfo';
import { useLikeStore } from '@/store/likeStore';
import TabBar from '@/components/TabBar.vue';
import Compressor from 'compressorjs';
import { usePaymentStore } from '@/store/paymentStore'; 
import { getLevelIcon } from '@/utils/levelIcon';

// 导入图标
import { ALL_TABS, ICON_MAP, type TabItem, type IconType, type DynamicTabItem } from '@/config/tabs'

// 定义 MenuItem 接口
interface MenuItem {
  id: string | number;
  label: string;
  action?: () => void; // 点击事件处理函数
  route?: string; // 路由路径
}

// 定义 User 接口
interface User {
  nickname: string; // 用户昵称
  avatarUrl?: string; // 可选的头像URL
  recentVisitorsCount: number;
}
const paymentStore = usePaymentStore();
const userInfoStore = useUserInfoStore();
const likeStore = useLikeStore();
const activeTab = ref('profile');
const authStore = useAuthStore();
const router = useRouter();
const avatarInput = ref<HTMLInputElement>();
const nicknameInput = ref<HTMLInputElement>();
const isEditingNickname = ref(false);
const tempNickname = ref('');
const showPhotoPopup = ref(false);
const fileList = ref<any[]>([]);
const userPhotos = ref<string[]>([]);
const recentVisitorsCount = ref(0);

const levelList = [
  { level: 1, points: 0 },
  { level: 2, points: 30 },
  { level: 3, points: 100 },
  { level: 4, points: 300 },
  { level: 5, points: 1000 },
  { level: 6, points: 3000 },
];

const currentPoints = computed(() => userInfoStore.profile?.points ?? 0);

const curLevel = computed(() => {
  const p = currentPoints.value;
  if (p >= 3000) return 6;
  if (p >= 1000) return 5;
  if (p >= 300)  return 4;
  if (p >= 100)  return 3;
  if (p >= 30)   return 2;
  return 1;            // 0 或 null 都归 Lv1
});


const prevLevel = computed(() => levelList[curLevel.value - 1]);
const nextLevel = computed(() => levelList[Math.min(curLevel.value, 5)]);
const progress = computed(() => {
  if (curLevel.value === 6) return 100;
  const prev = prevLevel.value.points;
  const next = nextLevel.value.points;
  return ((currentPoints.value - prev) / (next - prev)) * 100;
});
const showLevelPopover = ref(false);


const showRejectionNotice = ref(false);
const rejectionInfo = ref<{
  reason: string;
  created_at: string;
  is_read: boolean;
} | null>(null);

// 获取驳回信息
const fetchRejectionInfo = async () => {
  try {
    const response = await apiClient.get('/api/user/rejection');
    if (response.data.has_rejection && !response.data.is_read) {
      rejectionInfo.value = {
        reason: response.data.reason,
        created_at: response.data.created_at,
        is_read: response.data.is_read
      };
      showRejectionNotice.value = true;
    }
  } catch (error) {
    console.error('获取驳回信息失败', error);
  }
};

// 标记驳回为已读
const markRejectionAsRead = async () => {
  if (!rejectionInfo.value) return;
  
  try {
    await apiClient.post('/api/user/rejection/mark-read');
    showRejectionNotice.value = false;
    rejectionInfo.value = null;
  } catch (error) {
    console.error('标记已读失败', error);
    showToast('操作失败，请重试');
  }
};

// 从store中获取用户信息
const user = computed(() => {
  // 获取用户头像和性别
  const avatar = userInfoStore.profile?.avatar;
  const gender = userInfoStore.profile?.gender;
  
  // 设置默认头像路径
  let defaultAvatar = '';
  if (!avatar || avatar === '') {
    // 根据性别设置不同的默认头像
    defaultAvatar = gender === 'female'
      ? 'avatars/female_def.png' 
      : 'avatars/male_def.png';
  }
  
  return {
    nickname: userInfoStore.profile?.nickname || '用户昵称',
    avatarUrl: avatar ? 'avatars/' + avatar : defaultAvatar,
  };
});
const handleNicknameClick = () => {
  if (!paymentStore.isPaid) {
    // 未付费时显示提示信息
    showToast('请升级会员解锁编辑功能');
    return;
  }
  editNickname();
};

const handleAvatarClick = () => {
  if (!paymentStore.isPaid) {
    // 未付费时显示提示信息
    showToast('请升级会员解锁头像编辑功能');
    return;
  }
  editAvatar();
};

// 监听用户照片变化
watch(() => userInfoStore.profile?.photo, (newPhoto) => {
  if (newPhoto) {
    userPhotos.value = newPhoto.split(',').filter(p => p.trim());
    // 更新van-uploader的文件列表
    fileList.value = userPhotos.value.map(photo => ({
      url: 'photo/' + photo,
      status: 'done',
      message: '上传成功'
    }));
  } else {
    userPhotos.value = [];
    fileList.value = [];
  }
}, { immediate: true });

const likes = computed(() => {
  return {
    ilikeCount: likeStore.ilikeCount(),
    likemeCount: likeStore.likemeCount()
  };
});

const fetchVisitCount = async () => {
  try {
    const response = await apiClient.post('/api/visit-count',{});
    recentVisitorsCount.value = response.data.count;
  } catch (error) {
    console.error('获取最近来访数量失败', error);
    //showToast('获取数据失败');
  }
};

onMounted(async() => {
  // fetchUserProfile();
  await fetchVisitCount();
  await fetchRejectionInfo(); // 获取驳回信息
});

// 编辑头像
const editAvatar = () => {
  avatarInput.value?.click();
};

// 处理头像选择
const handleAvatarChange = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    // 显示压缩提示
    const toast = showLoadingToast({
      message: '图片压缩中...',
      duration: 0,
      forbidClick: true,
    });
    
    try {
      // 创建预览URL（立即显示预览）
      const previewUrl = URL.createObjectURL(file);
      user.value.avatarUrl = previewUrl;
      
      // 使用Compressor.js进行压缩
      const compressedFile = await new Promise<File>((resolve, reject) => {
        new Compressor(file, {
          quality: 0.8,           // 质量设置
          maxWidth: 1200,         // 最大宽度
          maxHeight: 1200,        // 最大高度
          convertSize: 1 * 1024 * 1024, // 超过1MB的图片进行格式转换
          success(result) {
            resolve(new File([result], file.name, {
              type: result.type,
              lastModified: Date.now(),
            }));
          },
          error(err) {
            reject(err);
          }
        });
      });
      
      // 创建FormData并上传文件
      const formData = new FormData();
      formData.append('file', compressedFile, file.name);
      
      const response = await apiClient.post('/api/upload-avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      showToast('头像更新成功');
      await userInfoStore.fetchUserProfile();
    } catch (error) {
      console.error('头像上传失败', error);
      showToast('头像上传失败');
    } finally {
      // 重置文件输入框
      target.value = '';
      closeToast();
    }
  }
};
// const handleAvatarChange = async (event: Event) => {
//   const target = event.target as HTMLInputElement;
//   const file = target.files?.[0];
//   if (file) {
//     // 检查文件大小（限制5MB）
//     if (file.size > 5 * 1024 * 1024) {
//       showToast('图片大小不能超过5MB');
//       return;
//     }
    
//     // 检查文件类型
//     if (!file.type.startsWith('image/')) {
//       showToast('请选择图片文件');
//       return;
//     }
    
//     // 创建预览URL
//     const previewUrl = URL.createObjectURL(file);
//     user.value.avatarUrl = previewUrl;
    
//     try {
//       // 创建FormData并上传文件
//       const formData = new FormData();
//       formData.append('file', file);
      
//       const response = await apiClient.post('/api/upload-avatar', formData, {
//         headers: {
//           'Content-Type': 'multipart/form-data',
//         },
//       });
      
//       // 更新头像URL为服务器返回的URL
//       // user.value.avatarUrl = response.data.avatar_url;
//       showToast('头像更新成功');
//       await userInfoStore.fetchUserProfile();
//     } catch (error) {
//       console.error('头像上传失败', error);
//       showToast('头像上传失败');
//     } finally {
//       // 重置文件输入框
//       target.value = '';
//     }
//   }
// };

// 编辑昵称
const editNickname = () => {
  isEditingNickname.value = true;
  tempNickname.value = user.value.nickname;
  nextTick(() => {
    nicknameInput.value?.focus();
  });
};

// 保存昵称
const saveNickname = async () => {
  if (tempNickname.value.trim()) {
    try {
      // 调用更新昵称API
      await apiClient.post('/api/update-nickname', {
        nickname: tempNickname.value.trim(),
      });
      
      user.value.nickname = tempNickname.value.trim();
      showToast('昵称更新成功');
      await userInfoStore.fetchUserProfile();
    } catch (error) {
      console.error('昵称更新失败', error);
      showToast('昵称更新失败');
    } finally {
      isEditingNickname.value = false;
    }
  } else {
    isEditingNickname.value = false;
  }
};

// 取消编辑
const cancelEdit = () => {
  isEditingNickname.value = false;
  tempNickname.value = '';
};

// 照片上传前的校验
const beforeRead = (file: any) => {
  if (!file.type.startsWith('image/')) {
    showToast('请上传图片文件');
    return false;
  }
  return true;
};

// 文件大小超过限制
const onOversize = () => {
  showToast('图片大小不能超过5MB');
};

// 照片上传处理
const afterRead = async (file: any) => {
  // 处理多文件上传情况
  const files = Array.isArray(file) ? file : [file];
  
  // 显示进度提示
  const toast = showLoadingToast({
    message: '照片处理中...',
    duration: 0,
    forbidClick: true,
  });
  
  try {
    for (const f of files) {
      f.status = 'uploading';
      f.message = '处理中...';
      
      try {
        // 使用Compressor.js压缩照片
        const compressedFile = await new Promise<File>((resolve, reject) => {
          new Compressor(f.file, {
            quality: 0.75,           // 稍低的质量设置（照片比头像要求低）
            maxWidth: 1200,          // 更大的宽度（照片可能需要更多细节）
            maxHeight: 1600,
            convertSize: 1 * 1024 * 1024, // 超过1.5MB的图片进行格式转换
            success(result) {
              resolve(new File([result], f.file.name, {
                type: result.type,
                lastModified: Date.now(),
              }));
            },
            error(err) {
              reject(err);
            }
          });
        });
        
        const formData = new FormData();
        formData.append('file', compressedFile, f.file.name);
        
        // 调用上传照片接口
        const response = await apiClient.post('/api/upload-photo', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        
        // 更新照片列表
        userPhotos.value.push(response.data.filename);
        
        f.status = 'done';
        f.message = '上传成功';
        
        // 更新进度提示
        toast.message = `已处理 ${userPhotos.value.length} 张照片`;
        
      } catch (error) {
        console.error('照片处理失败', error);
        f.status = 'failed';
        f.message = '处理失败';
      }
    }
    
    // 保存到用户资料
    await savePhotos();
    showToast('照片上传完成');
    
  } catch (error) {
    console.error('照片上传失败', error);
    showToast('照片上传失败');
  } finally {
    closeToast();
  }
};
// const afterRead = async (file: any) => {
//   file.status = 'uploading';
//   file.message = '上传中...';
  
//   try {
//     const formData = new FormData();
//     formData.append('file', file.file);
    
//     // 调用上传照片接口
//     const response = await apiClient.post('/api/upload-photo', formData, {
//       headers: {
//         'Content-Type': 'multipart/form-data',
//       },
//     });
    
//     // 更新照片列表
//     userPhotos.value.push(response.data.filename);
    
//     // 保存到用户资料
//     await savePhotos();
    
//     file.status = 'done';
//     file.message = '上传成功';
//   } catch (error) {
//     console.error('照片上传失败', error);
//     file.status = 'failed';
//     file.message = '上传失败';
//     showToast('error');
//   }
// };

// 更新删除照片函数
const deletePhoto = async (file: any) => {
  try {
    // 获取要删除的照片名称
    const photoName = file.file?.name || file.url?.split('/').pop();
    if (!photoName) {
      showToast('无法获取照片信息');
      return;
    }

    // 发送删除请求 - 确保包含正确的请求体
    await apiClient.post('/api/delete-photo', { 
      photo_name: photoName 
    });

        // 直接更新 store 中的 photo 信息
    if (userInfoStore.profile?.photo) {
      // 分割照片字符串为数组
      const photos = userInfoStore.profile.photo.split(',');
      // 过滤掉被删除的照片
      const updatedPhotos = photos.filter(p => p !== photoName);
      // 更新 store 中的 photo 字段
      userInfoStore.profile.photo = updatedPhotos.join(',');
    }

    // 更新本地状态
    const index = fileList.value.findIndex(f => f.url.includes(photoName));
    if (index !== -1) {
      fileList.value.splice(index, 1);
      userPhotos.value = fileList.value.map(f => f.url.split('/').pop());
      await savePhotos();
    }

    showToast('照片删除成功');
  } catch (error) {
    console.error('照片删除失败', error);
    showToast('照片删除失败');
  }
};

// 保存照片到用户资料
const savePhotos = async () => {
  try {
    await apiClient.post('/api/save-photos', {
      photos: userPhotos.value
    });
    
    // 更新用户信息
    await userInfoStore.fetchUserProfile();
  } catch (error) {
    console.error('保存照片失败', error);
    showToast('保存照片失败');
  }
};

// const menuItems = ref<MenuItem[]>([
//   { id: 'profile-maintenance', label: '资料维护', route: '/profile-setup' },
//   { id: 'photos', label: '我的照片', action: () => showPhotoPopup.value = true },

// ]);
const menuItems = computed<MenuItem[]>(() => {
  const items: MenuItem[] = [
    { id: 'profile-maintenance', label: '资料登记', route: '/profile-setup' }
  ];
  
  // 仅当用户已付费时才显示"我的照片"选项
  if (paymentStore.isPaid) {
    items.push({ 
      id: 'photos', 
      label: '我的照片', 
      action: () => showPhotoPopup.value = true 
    });
  }
  
  return items;
});

const tabs = computed(() => [...ALL_TABS, ...authStore.menuItems]);

</script>

<style scoped>

.disabled-nickname {
  cursor: not-allowed !important;
  opacity: 0.7;
}
.user-center-container {
  background-color: #F2EEE8;
  min-height: 100vh;
  padding: 16px;
  font-family: "Microsoft YaHei", sans-serif;
  display: flex;
  flex-direction: column;
  padding-bottom: 100px; /* 为底部TabBar留出空间，包含iOS安全区域 */
}

.page-content {
  flex: 1;
  margin-bottom: 60px;
}

.profile-card {
  background-color: #FFFFFF;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 8px;
  border: 1px solid #D9D9D9;
}

.profile-content {
  display: flex;
  align-items: flex-start;
}

.avatar-wrapper {
  margin-right: 16px;
  position: relative;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.avatar-wrapper:hover {
  transform: scale(1.05);
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: #D9D9D9;
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.avatar-placeholder {
  font-size: 24px;
  color: white;
  font-weight: bold;
}

.edit-hint {
  position: absolute;
  bottom: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 10px;
  color: #666;
  white-space: nowrap;
}

.profile-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.nickname-container {
  text-align: right;
  margin-bottom: 8px;
}

.nickname {
  font-size: 20px;
  color: #333;
  font-weight: 500;
  margin-bottom: 16px;
  align-self: flex-start;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
  display: inline-block;
}

.nickname:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.nickname-edit {
  position: relative;
  display: inline-block;
}

.nickname-input {
  font-size: 20px;
  font-weight: 500;
  color: #333;
  border: 2px solid #D75670;
  border-radius: 4px;
  padding: 4px 8px;
  background: white;
  outline: none;
  text-align: right;
  min-width: 120px;
}

.char-count {
  position: absolute;
  top: -20px;
  right: 0;
  font-size: 10px;
  color: #666;
}

.stats {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 60px;
}

.stat-number {
  font-size: 20px;
  color: #333;
  margin-bottom: 8px;
  font-weight: 700;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
}

.stat-label {
  font-size: 12px;
  color: #6A6A6A;
}

.section-title {
  color: #6A6A6A;
  font-size: 16px;
  margin-bottom: 16px;
  font-weight: normal;
}

.menu-card {
  background-color: #FFFFFF;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #D9D9D9;
}

.menu-items {
  display: flex;
  flex-direction: column;
}

.menu-item {
  padding: 12px 0;
  font-size: 14px;
  color: #333;
  border-bottom: 1px solid #F0F0F0;
  cursor: pointer;
}

.menu-item:last-child {
  border-bottom: none;
}

/* 照片上传弹出层样式 */
.photo-upload-container {
  padding: 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 16px;
}

.popup-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.photos-container {
  flex: 1;
  overflow-y: auto;
  padding: 0 16px;
}

/* 调整van-uploader默认样式 - 三等分宽度 */
:deep(.van-uploader) {
  width: 100%;
}

:deep(.van-uploader__wrapper) {
  display: grid;
  grid-template-columns: repeat(3, 1fr); /* 三等分 */
  gap: 8px; /* 间距8px */
}

:deep(.van-uploader__upload),
:deep(.van-uploader__preview) {
  width: 100% !important;
  height: 0 !important;
  padding-bottom: 100% !important; /* 保持正方形 */
  position: relative !important;
  margin: 0 !important;
}

:deep(.van-uploader__preview-image),
:deep(.van-uploader__upload-icon),
:deep(.van-uploader__upload-text) {
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  width: 100% !important;
  height: 100% !important;
  object-fit: cover !important;
}

:deep(.van-uploader__preview-image) {
  border-radius: 8px;
}

:deep(.van-uploader__upload) {
  background-color: #f9f9f9;
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
}

:deep(.van-uploader__preview-delete) {
  background-color: rgba(0, 0, 0, 0.5);
  top: 4px !important;
  right: 4px !important;
  width: 20px !important;
  height: 20px !important;
}

:deep(.van-uploader__file) {
  border-radius: 8px;
}

.upload-tips {
  text-align: center;
  font-size: 12px;
  color: #999;
  padding: 16px 0;
  border-top: 1px solid #f0f0f0;
  margin-top: auto;
}

.van-notice-bar {
  margin-bottom: 8px;
  border-radius: 8px;
}

.level-below {
  display: block;
  width: 48px;
  height: 30px;
  margin: 6px auto 0;
  filter: drop-shadow(0 1px 2px rgba(0,0,0,.2));
  cursor: pointer;
}

.level-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.current-score {
  font-size: 18px;
  font-weight: 700;
  color: #333;
}
.level-range {
  font-size: 13px;
  color: #666;
}

.progress-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
}
.level-thumb {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 0 4px rgba(0,0,0,.1);
}
.track {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: #f0f0f0;
  position: relative;
  overflow: hidden;
}
.fill {
  height: 100%;
  background: linear-gradient(90deg, #ff9a9e 0%, #fad0c4 100%);
  border-radius: 3px;
  transition: width .3s ease;
}

.level-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.level-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  border-radius: 4px;
}
.level-row.active {
  background: #ffecef;
}
.level-icon {
  width: 20px;
  height: 20px;
}
.level-name {
  flex: 1;
  font-size: 14px;
}
.level-points {
  font-size: 12px;
  color: #888;
}
</style>