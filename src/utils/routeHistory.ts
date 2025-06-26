// src/utils/routeHistory.ts
import type { RouteLocationNormalized } from 'vue-router';

// 获取上一个路由
export const getPreviousRoute = (): RouteLocationNormalized | null => {
  const saved = sessionStorage.getItem('previous_route');
  return saved ? JSON.parse(saved) : null;
};

// 设置上一个路由
export const setPreviousRoute = (route: RouteLocationNormalized) => {
  // 只保存必要信息
  const { path, query, params } = route;
  sessionStorage.setItem('previous_route', JSON.stringify({ path, query, params }));
};

// 清除历史记录
export const clearRouteHistory = () => {
  sessionStorage.removeItem('previous_route');
};