<template>
  <div class="admin-chat-container">
    <!-- 侧边栏 - 用户列表 -->
    <div class="sidebar">
      <div class="header">用户列表</div>
      <div 
        v-for="chat in activeChats" 
        :key="chat.id"
        :class="['user-item', { active: selectedChatId === chat.id }]"
        @click="selectChat(chat)"
      >
        <img :src="chat.user_avatar || '/default-avatar.png'" class="user-avatar" />
        <div class="user-info">
          <div class="user-name">{{ chat.user_nickname }}</div>
          <div class="last-message">{{ chat.last_message }}</div>
        </div>
        <div v-if="chat.unread_count > 0" class="unread-badge">{{ chat.unread_count }}</div>
      </div>
    </div>

    <!-- 主聊天区域 -->
    <div class="main-chat">
      <div v-if="selectedChat" class="chat-header">
        <div class="header-info">
          <img :src="selectedChat.user_avatar || '/default-avatar.png'" class="admin-avatar" />
          <div>
            <div class="admin-name">{{ selectedChat.user_nickname }}</div>
            <div class="status">在线</div>
          </div>
        </div>
      </div>
      
      <!-- 聊天消息区域 -->
      <div v-if="selectedChat" ref="messagesContainer" class="messages-container">
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
      <div v-if="selectedChat" class="input-container">
        <input 
          v-model="newMessage" 
          type="text" 
          placeholder="输入回复..."
          @keyup.enter="sendMessage"
          class="message-input"
        />
        <van-button
          @click="sendMessage"
          class="send-button"
          :icon="sendIcon"
        ></van-button>
      </div>
      
      <div v-else class="empty-state">
        <p>请从左侧选择一个用户开始聊天</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue';
import { useWebSocket } from '@vueuse/core';
import dayjs from 'dayjs';
import sendIcon from '@/assets/icons/send.svg';
import { useAuthStore } from '@/store/authStore';
import { fetchActiveChats, fetchChatHistory } from '@/api/chatApi';

const authStore = useAuthStore();

// 聊天数据
const activeChats = ref<any[]>([]);
const selectedChat = ref<any>(null);
const selectedChatId = ref<number | null>(null);
const messages = ref<any[]>([]);
const newMessage = ref('');

// WebSocket连接 - 管理员端
const token = authStore.token;
const WS_URL = `${import.meta.env.VITE_WS_BASE_URL}/ws/admin?token=${token}`;
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

// 加载活跃聊天会话
const loadActiveChats = async () => {
  try {
    const response = await fetchActiveChats();
    activeChats.value = response.data.map((chat: any) => ({
      ...chat,
      unread_count: chat.unread_count || 0
    }));
  } catch (error) {
    console.error('加载聊天列表失败', error);
  }
};

// 选择聊天会话
const selectChat = async (chat: any) => {
  selectedChat.value = chat;
  selectedChatId.value = chat.id;
  newMessage.value = '';
  
  // 加载历史消息
  try {
    const response = await fetchChatHistory(chat.id);
    messages.value = response.data.map((msg: any) => ({
      id: msg.id,
      text: msg.content,
      isSent: msg.sender_openid === 'admin', // 管理员发送的消息
      time: new Date(msg.sent_at)
    }));
    
    // 标记消息为已读
    markMessagesAsRead(chat.id);
    
    // 滚动到底部
    scrollToBottom();
  } catch (error) {
    console.error('加载历史消息失败', error);
  }
};

// 监听WebSocket消息
watch(data, (newData) => {
  if (newData) {
    try {
      const message = JSON.parse(newData);
      
      // 检查是否是当前选中的聊天
      if (message.chat_id === selectedChatId.value) {
        addMessage(message.text, false);
      }
      
      // 更新未读消息计数
      updateUnreadCount(message.chat_id, 1);
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
  if (newMessage.value.trim() && selectedChatId.value) {
    const messageData = {
      chat_id: selectedChatId.value,
      text: newMessage.value.trim()
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
    const container = document.querySelector('.messages-container');
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  });
};

// 格式化时间
const formatTime = (time: Date) => {
  return dayjs(time).format('HH:mm');
};

// 标记消息为已读
const markMessagesAsRead = async (chatId: number) => {
  try {
    await markMessagesRead(chatId);
    
    // 更新未读计数
    const chat = activeChats.value.find(c => c.id === chatId);
    if (chat) {
      chat.unread_count = 0;
    }
  } catch (error) {
    console.error('标记消息为已读失败', error);
  }
};

// 更新未读消息计数
const updateUnreadCount = (chatId: number, count: number) => {
  const chat = activeChats.value.find(c => c.id === chatId);
  if (chat) {
    chat.unread_count = (chat.unread_count || 0) + count;
  }
};

onMounted(() => {
  open();
  loadActiveChats();
});

onBeforeUnmount(() => {
  close();
});
</script>

<style scoped>
.admin-chat-container {
  display: flex;
  height: 100vh;
  background-color: #f8f8f8;
  font-family: "Microsoft YaHei", sans-serif;
}

.sidebar {
  width: 300px;
  border-right: 1px solid #e6e6e6;
  background-color: white;
  overflow-y: auto;
}

.header {
  padding: 16px;
  font-size: 18px;
  font-weight: 500;
  border-bottom: 1px solid #e6e6e6;
}

.user-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  position: relative;
}

.user-item:hover {
  background-color: #f9f9f9;
}

.user-item.active {
  background-color: #f0f7ff;
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  margin-right: 12px;
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 4px;
}

.last-message {
  font-size: 14px;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.unread-badge {
  background-color: #ff4d4f;
  color: white;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.main-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 16px;
}

/* 其他样式与Chat.vue相同 */
</style>