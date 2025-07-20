<template>
  <div class="settings-container">
    <van-nav-bar title="系统设置" left-arrow @click-left="goBack" />
    
    <van-cell-group>
      <van-cell
        title="标语设置"
        is-link
        @click="showSloganPopup = true"
      />
    </van-cell-group>

    <!-- 标语设置弹窗 -->
    <van-popup
      v-model:show="showSloganPopup"
      round
      position="bottom"
      :style="{ height: '30%' }"
    >
      <div class="popup-content">
        <van-field
          v-model="sloganInput"
          rows="2"
          autosize
          label="标语"
          type="textarea"
          maxlength="255"
          placeholder="请输入标语内容"
          show-word-limit
        />
        <div class="popup-actions">
          <van-button type="primary" block @click="submitSlogan">保存</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import apiClient from '@/plugins/axios';

const router = useRouter();
const showSloganPopup = ref(false);
const sloganInput = ref('');

const goBack = () => router.back();

const submitSlogan = async () => {
  if (!sloganInput.value.trim()) {
    showToast('请输入标语内容');
    return;
  }

  try {
    await apiClient.post('/api/admin/slogan', {
      content: sloganInput.value.trim()
    });
    showToast('保存成功');
    showSloganPopup.value = false;
    sloganInput.value = '';
  } catch (error) {
    console.error('提交失败:', error);
    showToast('保存失败，请重试');
  }
};
</script>

<style scoped>
.settings-container {
  min-height: 100vh;
  background-color: #f7f7f7;
}

.popup-content {
  padding: 16px;
}

.popup-actions {
  margin-top: 24px;
}
</style>