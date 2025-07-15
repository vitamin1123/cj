<template>
  <div class="admin-chat-container">
    <!-- 侧边栏 - 用户列表 -->
    <div class="sidebar" :class="{ 'collapsed': selectedChat }">
      <div class="sidebar-header">
        <!-- <van-icon name="manager" size="20" /> -->
        
        <van-search 
          v-model="searchQuery"
          placeholder="搜索用户"
          shape="round"
          class="search-box"
        />
      </div>
      
      <van-list v-model:loading="loading" :finished="finished">
        <div 
          v-for="chat in filteredChats" 
          :key="chat.id"
          :class="['user-item', { 'active': selectedChatId === chat.id }]"
          @click="selectChat(chat)"
        >
          <div class="avatar-container">
            <van-image
              round
              width="48px"
              height="48px"
              :src="chat.user_avatar || '/default-avatar.png'"
              class="user-avatar"
            />
            <van-badge :content="chat.unread_count" v-if="chat.unread_count > 0" />
          </div>
          <div class="user-info">
            <div class="user-name">{{ chat.user_nickname }}</div>
            <div class="last-message">
              <van-icon 
                name="comment" 
                size="12" 
                v-if="chat.last_message_sender === 'user'" 
                class="msg-icon"
              />
              {{ truncateText(chat.last_message, 20) }}
            </div>
          </div>
          <div class="time-info">
            {{ formatShortTime(chat.last_message_time) }}
          </div>
        </div>
      </van-list>
    </div>

    <!-- 主聊天区域 -->
    <div class="main-chat" v-if="selectedChat">
      <!-- 顶部导航栏 -->
      <van-sticky>
        <div class="chat-header">
          <van-icon name="arrow-left" class="back-icon" @click="closeChat" />
          <div class="header-info">
            <van-image
              round
              width="40px"
              height="40px"
              :src="selectedChat.user_avatar || '/default-avatar.png'"
              class="admin-avatar"
            />
            <div class="user-details">
              <div class="admin-name">{{ selectedChat.user_nickname }}</div>
              <div class="status">
                <van-icon name="certificate" color="#07c160" size="12" />
                <span>在线</span>
              </div>
            </div>
          </div>
          <van-icon name="ellipsis" class="menu-icon" @click="showChatActions" />
        </div>
      </van-sticky>
      
      <!-- 聊天消息区域 -->
      <div ref="messagesContainer" class="messages-container">
        <!-- 日期分隔符 -->
        <div class="date-divider" v-if="showDateDivider">
          <span>{{ formatDate(today) }}</span>
        </div>
        
        <div v-for="(message, index) in messages" :key="index">
          <!-- 时间分隔符 -->
          <div class="time-divider" v-if="shouldShowTimeDivider(index)">
            {{ formatTime(message.time) }}
          </div>
          
          <div :class="['message', message.isSent ? 'sent' : 'received']">
            <van-image
              v-if="!message.isSent"
              round
              width="36px"
              height="36px"
              :src="selectedChat.user_avatar || '/default-avatar.png'"
              class="message-avatar"
            />
            <div class="message-content-container">
              <div class="message-content">
                {{ message.text }}
              </div>
              <div class="message-status">
                <span v-if="message.isSent">
                  <van-icon name="passed" color="#07c160" v-if="message.read" />
                  <van-icon name="clock" color="#ccc" v-else />
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 输入区域 -->
      <div class="input-container">
        <van-field
          v-model="newMessage"
          type="textarea"
          rows="1"
          autosize
          placeholder="输入回复..."
          @keyup.enter="sendMessage"
          class="message-input"
        >
          <template #button>
            <div class="input-actions">
              <!-- <van-icon name="smile" class="action-icon" />
              <van-icon name="photo" class="action-icon" /> -->
              <van-button 
                round 
                type="primary" 
                size="small" 
                @click="sendMessage"
                :disabled="!newMessage.trim()"
                class="send-button"
              >
                发送
              </van-button>
            </div>
          </template>
        </van-field>
      </div>
    </div>
    
    
    
    <!-- 聊天操作菜单 -->
    <van-action-sheet v-model:show="showActions" title="聊天操作">
      <div class="action-sheet-content">
        <van-cell title="查看用户资料" icon="user-o" />
        <van-cell title="清空聊天记录" icon="delete" />
        <van-cell title="标记为未读" icon="envelop-o" />
        <van-cell title="投诉用户" icon="warning-o" />
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue';
import { useWebSocket } from '@vueuse/core';
import dayjs from 'dayjs';
import { 
  Image as VanImage, 
  Icon, 
  Button, 
  Field, 
  ActionSheet, 
  Cell, 
  List, 
  Search, 
  Sticky,
  Badge,
  Toast,
  showFailToast
} from 'vant';
import { fetchActiveChats, fetchChatHistory, markMessagesRead } from '@/api/chatApi';
import { useAuthStore } from '@/store/authStore';

const authStore = useAuthStore();

// 聊天数据
const activeChats = ref<any[]>([]);
const filteredChats = ref<any[]>([]);
const selectedChat = ref<any>(null);
const selectedChatId = ref<number | null>(null);
const messages = ref<any[]>([]);
const newMessage = ref('');
const searchQuery = ref('');
const loading = ref(false);
const finished = ref(false);
const showActions = ref(false);

// 日期处理
const today = ref(new Date());

// WebSocket连接 - 管理员端
const token = authStore.token;
const WS_URL = `${import.meta.env.VITE_WS_BASE_URL}/ws/admin?token=${token}`;
const { data, send, open, close } = useWebSocket(WS_URL, {
  autoReconnect: {
    retries: 3,
    delay: 3000,
    onFailed() {
      console.error('WebSocket连接失败');
      showFailToast('连接服务器失败');
    }
  },
  heartbeat: true,
  immediate: true,
});

// 过滤用户列表
watch([activeChats, searchQuery], () => {
  if (!searchQuery.value) {
    filteredChats.value = [...activeChats.value];
    return;
  }
  
  const query = searchQuery.value.toLowerCase();
  filteredChats.value = activeChats.value.filter(chat => 
    chat.user_nickname.toLowerCase().includes(query) || 
    chat.last_message.toLowerCase().includes(query)
  );
});

// 加载活跃聊天会话
const loadActiveChats = async () => {
  try {
    loading.value = true;
    const response = await fetchActiveChats();
    activeChats.value = response.data.map((chat: any) => ({
      ...chat,
      unread_count: chat.unread_count || 0,
      last_message_time: new Date(chat.last_message_time || new Date())
    }));
    filteredChats.value = [...activeChats.value];
    finished.value = true;
  } catch (error) {
    console.error('加载聊天列表失败', error);
    showFailToast('加载聊天列表失败');
  } finally {
    loading.value = false;
  }
};

// 选择聊天会话
const selectChat = async (chat: any) => {
  selectedChat.value = chat;
  selectedChatId.value = chat.id;
  newMessage.value = '';
  console.log('看看chat:',chat)
  // 加载历史消息
  try {
    const response = await fetchChatHistory(chat.chat_id);
    messages.value = response.data.map((msg: any) => ({
      id: msg.id,
      text: msg.content,
      isSent: msg.sender_type === 'admin',
      time: new Date(msg.sent_at),
      read: msg.read
    }));
    
    // 标记消息为已读
    await markMessagesAsRead(chat.chat_id);
    
    // 滚动到底部
    scrollToBottom();
  } catch (error) {
    console.error('加载历史消息失败', error);
    showFailToast('加载历史消息失败');
  }
};

// 关闭当前聊天
const closeChat = () => {
  selectedChat.value = null;
  selectedChatId.value = null;
  messages.value = [];
};

// 监听WebSocket消息
watch(data, (newData) => {
  if (newData) {
    try {
      const message = JSON.parse(newData);
      
      // 检查是否是当前选中的聊天
      if (message.chat_id === selectedChatId.value) {
        addMessage(message.text, false);
      } else {
        // 通知新消息
        Toast.info(`来自${message.user_name}的新消息`);
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
    time: new Date(),
    read: isSent ? false : true
  });
  
  // 滚动到底部
  scrollToBottom();
};

// 发送消息
const sendMessage = () => {
  if (newMessage.value.trim() && selectedChatId.value) {
    const messageData = {
      chat_id: selectedChatId.value,
      text: newMessage.value.trim(),
      receiver_id: selectedChat.value.user_id
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

// 格式化短时间
const formatShortTime = (time: Date) => {
  const now = new Date();
  const msgTime = new Date(time);
  
  if (dayjs(now).isSame(msgTime, 'day')) {
    return dayjs(msgTime).format('HH:mm');
  } else if (dayjs(now).subtract(1, 'day').isSame(msgTime, 'day')) {
    return '昨天';
  } else {
    return dayjs(msgTime).format('MM/DD');
  }
};

// 格式化日期
const formatDate = (date: Date) => {
  return dayjs(date).format('YYYY年MM月DD日');
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

// 文本截断
const truncateText = (text: string, maxLength: number) => {
  if (!text) return '';
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
};

// 显示聊天操作
const showChatActions = () => {
  showActions.value = true;
};

// 检查是否显示时间分隔符
const shouldShowTimeDivider = (index: number) => {
  if (index === 0) return true;
  
  const currentTime = messages.value[index].time;
  const prevTime = messages.value[index - 1].time;
  
  // 如果当前消息和前一条消息间隔超过5分钟，显示时间
  return dayjs(currentTime).diff(prevTime, 'minute') > 5;
};

// 计算是否显示日期分隔符
const showDateDivider = computed(() => {
  return messages.value.some(msg => 
    dayjs(msg.time).isSame(today.value, 'day')
  );
});

onMounted(() => {
  open();
  loadActiveChats();
});

onBeforeUnmount(() => {
  close();
});
</script>

<style scoped lang="scss">
.admin-chat-container {
  display: flex;
  height: 100vh;
  background-color: #f0f2f5;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.sidebar {
  width: 100%;
  background-color: #ffffff;
  border-right: 1px solid #e6e6e6;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  box-shadow: 1px 0 5px rgba(0, 0, 0, 0.05);
  
  /* 新增：桌面端/大屏样式 */
  @media (min-width: 768px) {
    width: 30%;
    min-width: 300px;
    max-width: 400px;
    
    &.collapsed {
      display: flex; /* 大屏上始终显示侧边栏 */
    }
  }
  
  /* 移动端保持原有行为 */
  @media (max-width: 767px) {
    &.collapsed {
      display: none;
    }
  }
}

.sidebar-header {
  display: flex;
  align-items: center;
  padding: 16px 12px 8px;
  background-color: #f9f9f9;
  
  .van-icon {
    margin-right: 8px;
    color: #07c160;
  }
  
  span {
    font-size: 18px;
    font-weight: 500;
    flex: 1;
  }
}

.search-box {
  padding: 8px 12px;
  background: transparent;
}

.user-item {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s;
  position: relative;
  
  &:hover {
    background-color: #f8f8f8;
  }
  
  &.active {
    background-color: #f0f7ff;
  }
}

.avatar-container {
  position: relative;
  margin-right: 12px;
  
  .van-badge {
    position: absolute;
    top: -4px;
    right: -4px;
    border: 2px solid white;
  }
}

.user-info {
  flex: 1;
  min-width: 0;
  
  .user-name {
    font-size: 16px;
    font-weight: 500;
    margin-bottom: 4px;
    color: #333;
  }
  
  .last-message {
    font-size: 13px;
    color: #999;
    display: flex;
    align-items: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    
    .msg-icon {
      margin-right: 4px;
      color: #07c160;
    }
  }
}

.time-info {
  font-size: 12px;
  color: #999;
  align-self: flex-start;
}

.main-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #f0f2f5;
  position: relative;
  
  /* 新增：桌面端/大屏样式 */
  @media (min-width: 768px) {
    width: 70%;
    
    /* 调整消息区域高度 */
    .messages-container {
      height: calc(100vh - 120px);
    }
  }
}


.chat-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background-color: #ffffff;
  border-bottom: 1px solid #e6e6e6;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  
  .back-icon {
    font-size: 20px;
    margin-right: 12px;
    cursor: pointer;
    color: #07c160;
  }
  
  .header-info {
    display: flex;
    align-items: center;
    flex: 1;
    
    .admin-avatar {
      margin-right: 12px;
    }
    
    .user-details {
      .admin-name {
        font-size: 16px;
        font-weight: 500;
        margin-bottom: 2px;
      }
      
      .status {
        display: flex;
        align-items: center;
        font-size: 12px;
        color: #666;
        
        span {
          margin-left: 4px;
        }
      }
    }
  }
  
  .menu-icon {
    font-size: 20px;
    color: #07c160;
    cursor: pointer;
  }
}

.messages-container {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  background-color: #e6e1dc;
  background-image: url('https://www.transparenttextures.com/patterns/concrete-wall.png');
}

.date-divider {
  text-align: center;
  margin: 16px 0;
  font-size: 12px;
  color: #999;
  
  span {
    background-color: #d9d9d9;
    padding: 4px 12px;
    border-radius: 12px;
  }
}

.time-divider {
  text-align: center;
  margin: 8px 0;
  font-size: 11px;
  color: #999;
}

.message {
  display: flex;
  margin-bottom: 16px;
  max-width: 80%;
  align-self: flex-start;
  
  .message-avatar {
    align-self: flex-end;
    margin-right: 10px;
  }
  
  .message-content-container {
    display: flex;
    flex-direction: column;
    max-width: calc(100% - 46px);
  }
  
  .message-content {
    padding: 12px 16px;
    border-radius: 18px;
    font-size: 15px;
    line-height: 1.4;
    position: relative;
    word-wrap: break-word;
    background-color: white;
    border: 1px solid #e6e6e6;
    box-shadow: 0 1px 1px rgba(0,0,0,0.05);
    border-top-left-radius: 4px;
  }
  
  .message-status {
    font-size: 10px;
    color: #999;
    margin-top: 4px;
    text-align: right;
    padding-right: 4px;
  }
  
  &.sent {
    align-self: flex-end;
    flex-direction: row-reverse;
    
    .message-avatar {
      margin-right: 0;
      margin-left: 10px;
    }
    
    .message-content {
      background-color: #95ec69;
      color: #000;
      border-top-right-radius: 4px;
      border-top-left-radius: 18px;
    }
    
    .message-status {
      text-align: left;
      padding-left: 4px;
    }
  }
}

.input-container {
  padding: 12px 16px;
  background-color: white;
  border-top: 1px solid #e6e6e6;
  
  .van-field {
    background-color: #f0f2f5;
    border-radius: 20px;
    padding: 8px 16px;
  }
}

.input-actions {
  display: flex;
  align-items: center;
  margin-left: 10px;
  
  .action-icon {
    font-size: 20px;
    color: #07c160;
    margin-right: 12px;
    cursor: pointer;
  }
  
  .send-button {
    background-color: #07c160;
    border: none;
    font-weight: 500;
    min-width: 70px;
    
    &:disabled {
      background-color: #cccccc;
    }
  }
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f8f8;
  
  .empty-content {
    text-align: center;
    max-width: 300px;
    
    .empty-icon {
      font-size: 80px;
      color: #e0e0e0;
      margin-bottom: 20px;
    }
    
    h3 {
      font-size: 22px;
      font-weight: 500;
      color: #333;
      margin-bottom: 12px;
    }
    
    p {
      font-size: 15px;
      color: #999;
      line-height: 1.5;
    }
  }
}

.action-sheet-content {
  padding: 16px;
  
  .van-cell {
    padding: 16px 0;
    font-size: 16px;
    
    &:not(:last-child) {
      border-bottom: 1px solid #f0f0f0;
    }
    
    .van-icon {
      margin-right: 10px;
      font-size: 18px;
    }
  }
}
</style>