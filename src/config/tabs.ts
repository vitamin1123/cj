import homeIcon from '@/assets/icons/home.svg';
import homeSelectedIcon from '@/assets/icons/home-selected.svg';
import compassIcon from '@/assets/icons/compass.svg';
import compassSelectedIcon from '@/assets/icons/compass-selected.svg';
import likeIcon from '@/assets/icons/like.svg';
import likeSelectedIcon from '@/assets/icons/like-selected.svg';
import smileIcon from '@/assets/icons/smile.svg';
import smileSelectedIcon from '@/assets/icons/smile-selected.svg';
import manaIcon from '@/assets/icons/mana.svg';
import manaSelectedIcon from '@/assets/icons/mana-selected.svg';

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

export const ICON_MAP = {
  mana: {
    default: manaIcon,
    selected: manaSelectedIcon
  },
  // 添加其他图标类型...
} as const;

export type StaticTabId = typeof ALL_TABS[number]['id']; // "home" | "explore" | "likes" | "profile"

export interface DynamicTabItem {
  id: string; // 允许任意字符串
  label: string;
  iconType: IconType;
  to: string;
  requiredPermission?: string;
}


// 类型导出
export type TabItem = 
  | typeof ALL_TABS[number] // 静态菜单项
  | { // 动态菜单项
      id: string;
      label: string;
      icon: string;
      iconSelected: string;
      to: string;
      requiredPermission?: string;
    };

export type IconType = keyof typeof ICON_MAP