import homeIcon from '@/assets/icons/home.svg';
import homeSelectedIcon from '@/assets/icons/home-selected.svg';
import compassIcon from '@/assets/icons/compass.svg';
import compassSelectedIcon from '@/assets/icons/compass-selected.svg';
import likeIcon from '@/assets/icons/like.svg';
import likeSelectedIcon from '@/assets/icons/like-selected.svg';
import smileIcon from '@/assets/icons/smile.svg';
import smileSelectedIcon from '@/assets/icons/smile-selected.svg';

export const tabs = [
  {
    id: 'home',
    label: '首页',
    icon: homeIcon,
    iconSelected: homeSelectedIcon,
    to: '/home'
  },
  {
    id: 'explore',
    label: '寻觅',
    icon: compassIcon,
    iconSelected: compassSelectedIcon,
    to: '/explore'
  },
  {
    id: 'likes',
    label: '喜欢',
    icon: likeIcon,
    iconSelected: likeSelectedIcon,
    to: '/likes'
  },
  {
    id: 'profile',
    label: '个人',
    icon: smileIcon,
    iconSelected: smileSelectedIcon,
    to: '/userCenter'
  }
];