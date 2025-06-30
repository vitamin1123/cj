import apiClient from '@/plugins/axios';

// 使用唯一导出声明
export interface AdminUser {
  id: number;
  nickname: string;
  gender: 'male' | 'female';
  avatar: string;
  like_count: number;
  is_active: boolean;
  is_top: boolean;
  state: number;
  expire_at: string;
}

// 内部使用的请求类型不需要导出
interface UpdateStatusRequest {
  is_active: boolean;
}

export const getUsersWithLikes = async (gender?: 'male' | 'female'): Promise<AdminUser[]> => {
  const params: Record<string, any> = {};
  if (gender) params.gender = gender;
  const response = await apiClient.get('/api/admin/users', { params });
  return response.data || [];
};

export const updateUserActiveStatus = (
  userId: number, 
  isActive: boolean
): Promise<void> => {
  return apiClient.post(`/api/admin/users/${userId}/status`, {
    is_active: isActive
  });
};