// src/store/viewState.ts
import { defineStore } from 'pinia'

export const useViewStateStore = defineStore('viewState', {
  state: () => ({
    // 为你的寻觅页面的滚动位置创建一个状态
    exploreScrollPosition: 0,
    // 你还可以为其他需要保存状态的页面添加类似的状态
    // homeScrollPosition: 0,
    // likesScrollPosition: 0,
  }),
  actions: {
    // 创建一个 action 来更新滚动位置
    setExploreScrollPosition(position: number) {
      this.exploreScrollPosition = position
    },
  },
})