import apiClient from '@/plugins/axios';

// 获取活跃聊天会话
export const fetchActiveChats = () => {
  return apiClient.get(`/api/admin/chats`,{});

};

// 获取聊天历史
export const fetchChatHistory = (chatId: number) => {
    return apiClient.get(`/api/admin/chats/${chatId}/messages`,{});
  
};

// 标记消息为已读
export const markMessagesRead = (chatId: number) => {
    return apiClient.post(`/api/admin/chats/${chatId}/mark-read`,{});
  
};