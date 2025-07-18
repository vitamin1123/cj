<template>
  <div class="admin-chat-container">
    <van-floating-bubble
      v-model:offset="offset"
      axis="xy"
      magnetic="x"
      icon="revoke"
      :size="54"
      :gap="10"
      @click="goBack"
      style="--van-floating-bubble-background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);"
    />
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
              radius="8"
              width="48px"
              height="48px"
              fit="contain"
              :src="`/avatars/${chat.user_avatar}`"
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
              fit="contain"
              :src="`/avatars/${selectedChat.user_avatar}`"
              class="admin-avatar"
            />
            <div class="user-details">
              <div class="admin-name">{{ selectedChat.user_nickname }}</div>
              
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
            <!-- <van-image
              v-if="!message.isSent"
              round
              width="36px"
              height="36px"
              :src="'/avatars/'+selectedChat.user_avatar || '/avatars/default-avatar.png'"
              class="message-avatar"
            /> -->
            <div class="message-content-container"
            @touchstart="startLongPress(message, $event)"
            @touchend="endLongPress"
            @contextmenu.prevent="handleRightClick(message, $event)">
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
          <van-popup
          v-model:show="showRevokeConfirm"
          position="bottom"
          round
          :style="{ height: '15%', paddingBottom: '20px' }"
        >
          <div class="revoke-popup">
            <van-button color="#d75670" block @click="confirmRevoke" class="revoke-btn-confirm">
              撤回
            </van-button>
            <van-button block @click="cancelRevoke" class="revoke-btn-cancel">
              取消
            </van-button>
          </div>
        </van-popup>
          
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
        />
          

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
    </div>
    
    
    
    <!-- 聊天操作菜单 -->
    <van-action-sheet v-model:show="showActions" title="聊天操作">
      <div class="action-sheet-content">
        <van-cell title="查看用户资料" icon="user-o" />
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue';
import { useWebSocket } from '@vueuse/core';
import { useRouter, useRoute  } from 'vue-router';
import { getPreviousRoute } from '@/utils/routeHistory';
import dayjs from 'dayjs';
import apiClient from '@/plugins/axios';
import { v4 as uuidv4 } from 'uuid';

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
const router = useRouter();
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
const showRevokeConfirm = ref(false);
const selectedMessage = ref<any>(null);
let longPressTimer: number | null = null;
const offset = ref({ x: 0.05 * window.innerWidth, y: 0.83 * window.innerHeight });
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

const isWithinTwoMinutes = (time: Date) => {
  return new Date().getTime() - new Date(time).getTime() < 2 * 60 * 1000;
};

const startLongPress = (message: any, event: TouchEvent) => {
  if (!message.isSent || !isWithinTwoMinutes(message.time)) return;
  event.preventDefault();
  longPressTimer = window.setTimeout(() => {
    selectedMessage.value = message;
    showRevokeConfirm.value = true;
  }, 800);
};

const endLongPress = () => {
  if (longPressTimer) {
    clearTimeout(longPressTimer);
    longPressTimer = null;
  }
};

const handleRightClick = (message: any, event: MouseEvent) => {
  if (!message.isSent || !isWithinTwoMinutes(message.time)) return;
  event.preventDefault();
  selectedMessage.value = message;
  showRevokeConfirm.value = true;
};

const confirmRevoke = async () => {
  if (!selectedMessage.value) return;
  try {
    await revokeMessage(selectedMessage.value.id);
    showRevokeConfirm.value = false;
    selectedMessage.value = null;
  } catch (e) {
    showFailToast('撤回失败');
  }
};

const cancelRevoke = () => {
  showRevokeConfirm.value = false;
  selectedMessage.value = null;
};

// 添加撤回消息函数
const revokeMessage = async (messageId: number) => {
  try {
    
    const response = await apiClient.post('/api/admin/chat/revoke', {
      message_id: selectedMessage.value.id
    });
    
    if (response.status === 200) {
      // 从本地消息列表中移除
      messages.value = messages.value.filter(msg => msg.id !== messageId);
    }
  } catch (error) {
    console.error('撤回消息失败:', error);
  }
};

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
    activeChats.value = response.data.map((chat: any) => {
      let avatar = 'notregisted.png'; // 默认值

      if (chat.user_avatar) {
        avatar = chat.user_avatar;
      } else if (chat.user_gender !== null) {
        avatar = chat.user_gender === 1 ? 'male_def.png' : 'female_def.png';
      }

      return {
        ...chat,
        user_avatar: avatar,
        unread_count: chat.unread_count || 0,
        last_message_time: new Date(chat.last_message_time || new Date())
      };
    });
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
  console.log('chat',chat)
  selectedChat.value = chat;
  selectedChatId.value = chat.chat_id;
  newMessage.value = '';
  console.log('看看chat:',chat)
  // 加载历史消息
  try {
    const response = await fetchChatHistory(chat.chat_id);
    console.log('response',response)
    messages.value = response.data.map((msg: any) => ({
      id: msg.id,
      text: msg.content,
      isSent: msg.sender === 'admin',
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

const goBack = () => {
  const previousRoute = getPreviousRoute();
  if (previousRoute) {
    router.replace({ path: previousRoute.path, query: previousRoute.query, params: previousRoute.params });
  } else {
    router.replace('/home');
  }
};

// 监听WebSocket消息
// watch(data, (newData) => {
//   if (!newData || typeof newData !== 'string') return;
//   // 跳过心跳消息
//   if (newData === 'ping' || newData === 'pong') return;
//   try {
//     const message = JSON.parse(newData);

//     if (message.type === 'revoke_message') {
//       // 处理撤回消息
//       messages.value = messages.value.filter(msg => msg.id !== message.id);
//     } else if (message.chat_id === selectedChatId.value) {
//       addMessage(message.text, false, message.id);
//     } else {
//       Toast.info(`来自${message.user_name || '未知用户'}的新消息`);
//     }

//     updateUnreadCount(message.chat_id, 1);
//   } catch (e) {
//     console.warn('收到非JSON消息，跳过解析:', newData);
//   }
// });
watch(data, (newData) => {
  if (!newData || typeof newData !== 'string') return;
  // 跳过心跳消息
  if (newData === 'ping' || newData === 'pong') return;

  try {
    const message = JSON.parse(newData);

    // ✅ 处理聊天列表实时更新
    if (message.type === 'chat_list_update') {
      const updatedChat = message.chat;

      const index = activeChats.value.findIndex(c => c.chat_id === updatedChat.chat_id);
      if (index !== -1) {
        // 更新已有会话
        activeChats.value[index] = { ...activeChats.value[index], ...updatedChat };
      } else {
        // 新增会话（从未聊过的新用户）
        activeChats.value.unshift(updatedChat);
      }

      // 同步过滤列表
      filteredChats.value = [...activeChats.value];
      return;
    }

    // ✅ 处理消息撤回
    if (message.type === 'revoke_message') {
      messages.value = messages.value.filter(msg => msg.id !== message.id);
      return;
    }

    // ✅ 当前聊天窗口内的消息
    if (message.chat_id === selectedChatId.value) {
      addMessage(message.text, false, message.id);
    } else {
      // ✅ 非当前窗口的新消息提示
      Toast.info(`来自${message.user_name || '未知用户'}的新消息`);
    }

    // ✅ 更新未读数（兼容旧逻辑）
    updateUnreadCount(message.chat_id, 1);
  } catch (e) {
    console.warn('收到非JSON消息，跳过解析:', newData);
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
  
  // 滚动到底部
  scrollToBottom();
};

// 发送消息
const sendMessage = () => {
  console.log('newMessage.value',newMessage.value,selectedChatId.value)
  if (newMessage.value.trim() && selectedChatId.value) {
    const messageId = uuidv4();
    const messageData = {
      id: messageId,
      chat_id: selectedChatId.value,
      text: newMessage.value.trim(),
      receiver_id: selectedChat.value.user_id
    };

    console.log(JSON.stringify(messageData))
    addMessage(newMessage.value.trim(), true, messageId);
    // 发送WebSocket消息
    send(JSON.stringify(messageData));
    
    // 添加到本地消息列表
    
    
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
    loadActiveChats();
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
  width: 100%;
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
    flex: 0 0 30%; 
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
    top: 0;
    right: 0;
    border: 2px solid white;
    z-index: 1;
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
  width: auto; 
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
  max-width: 100%;
  align-self: flex-start;
  
  .message-avatar {
    align-self: flex-end;
    margin-right: 10px;
  }
  
  .message-content-container {
    display: flex;
    flex-direction: column;
    max-width: 80%;
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
  display: flex;
  align-items: flex-end;
  padding: 12px 16px;
  background-color: white;
  border-top: 1px solid #e6e6e6;

  .van-field {
    flex: 1;
    background-color: #f0f2f5;
    border-radius: 20px;
    padding: 8px 16px;
  }

  .send-button {
    margin-left: 14px;
    min-width: 60px;
    height: 40px;
    width: 80px
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
.revoke-popup {
  padding: 16px;
  .revoke-btn-confirm,
  .revoke-btn-cancel {
    margin-bottom: 8px;
  }
}
</style>