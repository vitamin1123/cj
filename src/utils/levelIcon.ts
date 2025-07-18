import level0 from '@/assets/icons/level_0.svg';
import level1 from '@/assets/icons/level_1.svg';
import level2 from '@/assets/icons/level_2.svg';
import level3 from '@/assets/icons/level_3.svg';
import level4 from '@/assets/icons/level_4.svg';
import level5 from '@/assets/icons/level_5.svg';
import level6 from '@/assets/icons/level_6.svg';

const levelMap = [level0, level1, level2, level3, level4, level5, level6];

export const getLevelIcon = (points: number | null): string => {
  if (points === null || points === 0) return level1;

  let level = 1;
  if (points >= 3000) level = 6;
  else if (points >= 1000) level = 5;
  else if (points >= 300) level = 4;
  else if (points >= 100) level = 3;
  else if (points >= 30) level = 2;

  return levelMap[level] || level1;
};