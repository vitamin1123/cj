import apiClient from '@/plugins/axios';

export const likeUser = (likedId: number, action: 'like' | 'unlike') => {
  return apiClient.post('/api/like', {
    liked_id: likedId,
    action: action
  }, {
    timeout: 3000,
    // 由于 retry 不是 AxiosRequestConfig 的标准配置项，需要移除
    // retryDelay: 500
  });
};

export const checkLikeStatus = (likedId: number) => {
  return apiClient.get(`/api/like/status?liked_id=${likedId}`);
};