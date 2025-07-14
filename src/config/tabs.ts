import homeIcon from '@/assets/tabbar/home.png';
import homeSelectedIcon from '@/assets/tabbar/home_selected.png';
import compassIcon from '@/assets/tabbar/compass.png';
import compassSelectedIcon from '@/assets/tabbar/compass_selected.png';
import likeIcon from '@/assets/tabbar/like.png';
import likeSelectedIcon from '@/assets/tabbar/like_selected.png';
import smileIcon from '@/assets/tabbar/smile.png';
import smileSelectedIcon from '@/assets/tabbar/smile_selected.png';

// 所有可能的标签配置
export const ALL_TABS = [
  { 
    id: 'home', 
    label: '首页', 
    icon: homeIcon,
    iconSelected: homeSelectedIcon,
    to: '/home',
    requiredPermission: null // 不需要权限
  },
  { 
    id: 'explore', 
    label: '寻觅', 
    icon: compassIcon,
    iconSelected: compassSelectedIcon,
    to: '/explore',
    requiredPermission: 'explore:access'
  },
  { 
    id: 'likes', 
    label: '喜欢', 
    icon: likeIcon,
    iconSelected: likeSelectedIcon,
    to: '/likes',
    requiredPermission: 'likes:access'
  },
  { 
    id: 'profile', 
    label: '个人', 
    icon: smileIcon,
    iconSelected: smileSelectedIcon,
    to: '/userCenter',
    requiredPermission: 'profile:access'
  }
] as const;

// 类型导出
export type TabItem = typeof ALL_TABS[number];