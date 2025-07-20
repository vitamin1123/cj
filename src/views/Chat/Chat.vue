<template>
  <div class="chat-container">
    
    <!-- 顶部导航栏 -->
    <div class="chat-header">
      <van-icon name="arrow-left" class="back-icon" @click="goBack" />
      <div class="header-info">
        <img :src="adminAvatar" alt="陈姐头像" class="admin-avatar" />
        <div>
          <div class="admin-name">陈姐</div>
          <!-- <div class="status">在线</div> -->
        </div>
      </div>
    </div>
    
    <!-- 聊天消息区域 -->
    <div ref="messagesContainer" class="messages-container">

      <div v-for="(message, index) in messages" :key="index" 
           :class="['message', message.isSent ? 'sent' : 'received']"
           @touchstart="startLongPress(message, $event)"
            @touchend="endLongPress"
           >
        <div class="message-content">
          {{ message.text }}
        </div>
        <div class="message-time">
          {{ formatTime(message.time) }}
        </div>
      </div>
      <van-popup
        v-model:show="showRevokeConfirm"
        position="bottom"
        round
        :style="{ height: '15%', paddingBottom: '20px' }"
      >
        <div class="revoke-popup">
          
          <van-button 
            color="#d75670"
            block 
            @click="confirmRevoke"
            class="revoke-btn-confirm"
          >
            撤回
          </van-button>
          <van-button 
            block 
            @click="cancelRevoke"
            class="revoke-btn-cancel"
          >
            取消
          </van-button>
        </div>
      </van-popup>

    </div>
    
    <!-- 输入区域 -->
    <div class="input-container">
      <van-field
          v-model="newMessage"
          type="textarea"
          rows="1"
          autosize
          placeholder="输入消息..."
          @keyup.enter="sendMessage"
          class="message-input"
        />
      <van-button
      @click="sendMessage"
      class="send-button"
      :icon="sendIcon"
      :disabled="isSendingBlocked"
    >
      {{ isSendingBlocked ? `${countdown}s` : '' }}
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
import apiClient from '@/plugins/axios';
import dayjs from 'dayjs';
import sendIcon from '@/assets/icons/send.svg';
import { showFailToast } from 'vant';
import { v4 as uuidv4 } from 'uuid';
const lastSendTime = ref(0);
const isSendingBlocked = ref(false);
const countdown = ref(0);
let countdownInterval: ReturnType<typeof setInterval> | null = null;

const startCountdown = () => {
  countdown.value = 2;
  if (countdownInterval) clearInterval(countdownInterval);
  countdownInterval = setInterval(() => {
    countdown.value--;
    if (countdown.value <= 0) {
      clearInterval(countdownInterval!);
      countdownInterval = null;
    }
  }, 1000);
};

const showRevokeConfirm = ref(false);
const selectedMessage = ref<any>(null);
let longPressTimer: number | null = null;

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

// 修改撤回函数
const confirmRevoke = async () => {
  if (!selectedMessage.value) return;
  
  try {
    const response = await apiClient.post('/api/user/chat/revoke', {
      message_id: selectedMessage.value.id
    });
    
    if (response.status === 200) {
      messages.value = messages.value.filter(msg => msg.id !== selectedMessage.value.id);
      showRevokeConfirm.value = false;
      selectedMessage.value = null;
    }
  } catch (error) {
    console.error('撤回消息失败:', error);
    // 可以添加错误提示
    showFailToast('撤回失败，请重试');
  }
};

// 修改长按事件处理（只保留移动端）
const startLongPress = (message: any, event: Event) => {
  if (!message.isSent || !isWithinTwoMinutes(message.time)) {
    return;
  }
  
  event.preventDefault();
  
  longPressTimer = window.setTimeout(() => {
    selectedMessage.value = message;
    showRevokeConfirm.value = true;
  }, 800);
};

const endLongPress = () => {
  if (longPressTimer !== null) {
    clearTimeout(longPressTimer);
    longPressTimer = null;
  }
};



const cancelRevoke = () => {
  showRevokeConfirm.value = false;
  selectedMessage.value = null;
};

// 修改 isWithinTwoMinutes 函数
const isWithinTwoMinutes = (time: Date) => {
  return new Date().getTime() - new Date(time).getTime() < 2 * 60 * 1000;
};

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
  if (!newData || typeof newData !== 'string') return;
  // 跳过心跳消息
  if (newData === 'ping' || newData === 'pong') return;
  if (newData) {
    try {
      const message = JSON.parse(newData);
      if (message.type === 'revoke_message') {
      // 处理撤回消息
      messages.value = messages.value.filter(msg => msg.id !== message.id);
    } else if ( message.type === 'user_message' || message.text) {
      // 处理普通消息
      addMessage(message.text, false, message.id);
    }
    } catch (e) {
      console.error('解析消息失败', e);
    }
  }
});

// 添加消息
const addMessage = (text: string, isSent: boolean, id: string) => {
 
  messages.value.push({
    id: id,
    text,
    isSent,
    time: new Date(),
    read: isSent ? false : true
  });
  scrollToBottom();

  // 滚动到底部
  
};

// 发送消息
const sendMessage = () => {
const now = Date.now();
  if (now - lastSendTime.value < 2000) return;
  if (newMessage.value.trim()) {
    const messageId = uuidv4();

    const messageData = {
      id: messageId,
      text: newMessage.value.trim(),
      sender_id: userStore.profile?.id
    };
    
    // 发送WebSocket消息
    
    // 添加到本地消息列表
    addMessage(newMessage.value.trim(), true, messageId);
    send(JSON.stringify(messageData));
    // 清空输入框
    newMessage.value = '';

    lastSendTime.value = now;
    isSendingBlocked.value = true;

    // 2秒后恢复
    setTimeout(() => {
      isSendingBlocked.value = false;
    }, 2000);
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
  router.replace('/home')
};

// 添加撤回消息函数
// const revokeMessage = async (messageId: number) => {
//   try {
//     const response = await fetch('/api/user/chat/revoke', {
//       method: 'POST',
//       headers: {
//         'Authorization': `Bearer ${authStore.token}`,
//         'Content-Type': 'application/json'
//       },
//       body: JSON.stringify({ message_id: messageId })
//     });
    
//     if (response.ok) {
//       // 从本地消息列表中移除
//       messages.value = messages.value.filter(msg => msg.id !== messageId);
//     }
//   } catch (error) {
//     console.error('撤回消息失败:', error);
//   }
// };

// 加载历史消息
const loadHistory = async () => {
  try {
    const res = await apiClient.get('/api/user/chat/messages');
    const data = res.data;
    // messages.value = data.map((msg: any) => ({
    //   text: msg.content,
    //   isSent: msg.is_sent,
    //   time: new Date(msg.sent_at)
    // }));
    if (data && data.length > 0) {
      messages.value = data.map((msg: any) => ({
        id: msg.id,
        text: msg.content,
        isSent: msg.is_sent,
        time: new Date(msg.sent_at)
      }));
    } else {
      messages.value = [{
        id: Date.now(),
        text: '您好，我是陈姐，有什么可以帮您的吗？',
        isSent: false,
        time: new Date()
      }];
    }
    scrollToBottom();
  } catch (e) {
    console.error('加载历史消息失败', e);
  }
};

onMounted(() => {
  open();
  loadHistory();
});

onBeforeUnmount(() => {
  close();
  if (countdownInterval) clearInterval(countdownInterval);
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
  background-color: rgb(216, 127, 194);
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
  &:active {
    opacity: 0.7;
    transition: opacity 0.1s;
  }
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
  background-color: #e298d7;
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