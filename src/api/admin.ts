import apiClient from '@/plugins/axios';

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
  points: number;
}

interface UpdateStatusRequest {
  is_active: boolean;
}

// 添加分页和过滤参数
export interface GetUsersParams {
  gender?: 'male' | 'female';
  isTop?: boolean;
  keyword?: string;
  page?: number;
  pageSize?: number;
}

export const getUsersWithLikes = async (params?: GetUsersParams): Promise<AdminUser[]> => {
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

export const toggleUserTopStatus = (userId: number, isTop: boolean): Promise<void> => {
  return apiClient.post(`/api/admin/users/${userId}/toggle-top`, { is_top: isTop });
};