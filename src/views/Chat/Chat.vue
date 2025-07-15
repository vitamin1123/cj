<template>
  <div class="chat-container">
    <!-- 顶部导航栏 -->
    <div class="chat-header">
      <van-icon name="arrow-left" class="back-icon" @click="goBack" />
      <div class="header-info">
        <img :src="adminAvatar" alt="陈姐头像" class="admin-avatar" />
        <div>
          <div class="admin-name">陈姐</div>
          <div class="status">在线</div>
        </div>
      </div>
    </div>
    
    <!-- 聊天消息区域 -->
    <div ref="messagesContainer" class="messages-container">
      <div v-for="(message, index) in messages" :key="index" 
           :class="['message', message.isSent ? 'sent' : 'received']">
        <div class="message-content">
          {{ message.text }}
        </div>
        <div class="message-time">
          {{ formatTime(message.time) }}
        </div>
      </div>
    </div>
    
    <!-- 输入区域 -->
    <div class="input-container">
      <input 
        v-model="newMessage" 
        type="text" 
        placeholder="输入消息..."
        @keyup.enter="sendMessage"
        class="message-input"
      />
      <van-button
      @click="sendMessage"
      class="send-button"
      :icon="sendIcon"

    >
 
    </van-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue';
import { useWebSocket } from '@vueuse/core';
import { useRouter } from 'vue-router';
import { useUserInfoStore } from '@/store/userinfo';
import { useAuthStore } from '@/store/authStore';
import dayjs from 'dayjs';
import sendIcon from '@/assets/icons/send.svg';

const authStore = useAuthStore();
const router = useRouter();
const userStore = useUserInfoStore();

// 管理员信息
const adminAvatar = ref('/avatars/admin_avatar.png');
const adminName = ref('陈姐');

// 消息数据
const messages = ref<any[]>([]);
const newMessage = ref('');
const messagesContainer = ref<HTMLElement | null>(null);

// WebSocket连接
// const WS_URL = `ws://${location.host}/ws/user/${userStore.profile?.id}`;
const token = authStore.token;
// const WS_URL = `wss://${location.host}/ws/user?token=${token}`;
const WS_URL = `${import.meta.env.VITE_WS_BASE_URL}/ws/user?token=${token}`
const { data, send, open, close } = useWebSocket(WS_URL, {
  autoReconnect: {
    retries: 3,
    delay: 3000,
    onFailed() {
      console.error('WebSocket连接失败');
    }
  },
  heartbeat: true,
  immediate: true,
});

// 监听WebSocket消息
watch(data, (newData) => {
  if (newData) {
    try {
      const message = JSON.parse(newData);
      addMessage(message.text, false);
    } catch (e) {
      console.error('解析消息失败', e);
    }
  }
});

// 添加消息
const addMessage = (text: string, isSent: boolean) => {
  messages.value.push({
    id: Date.now(),
    text,
    isSent,
    time: new Date()
  });
  
  // 滚动到底部
  scrollToBottom();
};

// 发送消息
const sendMessage = () => {
  if (newMessage.value.trim()) {
    const messageData = {
      text: newMessage.value.trim(),
      sender_id: userStore.profile?.id
    };
    
    // 发送WebSocket消息
    send(JSON.stringify(messageData));
    
    // 添加到本地消息列表
    addMessage(newMessage.value.trim(), true);
    
    // 清空输入框
    newMessage.value = '';
  }
};

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

// 格式化时间
const formatTime = (time: Date) => {
  return dayjs(time).format('HH:mm');
};

// 返回上一页
const goBack = () => {
  router.back();
};

// 加载历史消息
const loadHistory = async () => {
  try {
    // 模拟API调用
    const mockHistory = [
      { id: 1, text: '您好，我是陈姐，有什么可以帮您的吗？', isSent: false, time: new Date(Date.now() - 3600000) },
      { id: 2, text: '我想咨询一下会员服务', isSent: true, time: new Date(Date.now() - 3500000) },
      { id: 3, text: '好的，请描述一下您的需求', isSent: false, time: new Date(Date.now() - 3400000) },
    ];
    
    messages.value = mockHistory;
    scrollToBottom();
  } catch (error) {
    console.error('加载历史消息失败', error);
  }
};

onMounted(() => {
  open();
  loadHistory();
});

onBeforeUnmount(() => {
  close();
});
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f8f8f8;
  font-family: "Microsoft YaHei", sans-serif;
}

.chat-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background-color: #4f8ef7;
  color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: relative;
}

.back-icon {
  font-size: 20px;
  margin-right: 12px;
  cursor: pointer;
}

.header-info {
  display: flex;
  align-items: center;
}

.admin-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 12px;
  border: 2px solid white;
}

.admin-name {
  font-size: 16px;
  font-weight: 500;
}

.status {
  font-size: 12px;
  opacity: 0.8;
}

.messages-container {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background-color: #F2EEE8;
  display: flex;
  flex-direction: column;
}

.message {
  max-width: 80%;
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
}

.message.received {
  align-self: flex-start;
}

.message.sent {
  align-self: flex-end;
}

.message-content {
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 15px;
  line-height: 1.4;
  position: relative;
  word-wrap: break-word;
}

.message.received .message-content {
  background-color: white;
  border: 1px solid #e6e6e6;
  box-shadow: 0 1px 1px rgba(0,0,0,0.05);
  border-top-left-radius: 4px;
}

.message.sent .message-content {
  background-color: #4f8ef7;
  color: white;
  border-top-right-radius: 4px;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  text-align: right;
}

.message.received .message-time {
  text-align: left;
}

.input-container {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background-color: white;
  border-top: 1px solid #e6e6e6;
}

.message-input {
  flex: 1;
  padding: 10px 16px;
  border-radius: 24px;
  border: 1px solid #e6e6e6;
  font-size: 15px;
  background-color: #f4f7f9;
  outline: none;
}

.send-button {
  color: #f2eee8;
  margin-left: 12px;
  padding: 0 12px;
  height: 40px;
  width: 60px;
  border-radius: 18px;
}

.send-button :deep(.van-icon) {
  width: 20px;
  height: 20px;
}
</style>