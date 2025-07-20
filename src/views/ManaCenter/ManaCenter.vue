<template>
  <div class="mana-container">
    <!-- 顶部统计卡片 -->
    <div class="stats-container">
      <!-- 左侧大卡片 - 最近7天登录人数 -->
      <div class="stat-card large">
        <div class="stat-header">
          <van-icon name="user-o" size="16" color="#6A6A6A" />
          <span class="stat-title">最近7天登录人数</span>
        </div>
        <div class="chart-container">
          <div ref="loginChart" style="width: 100%; height: 120px;"></div>
        </div>
      </div>

      <!-- 右侧小卡片容器 -->
      <div class="small-cards">
        <!-- 最近注册人数 -->
        <div class="stat-card small">
          <div class="stat-header">
            <van-icon name="records-o" size="14" color="#6A6A6A" />
            <span class="stat-title">最近注册人数</span>
          </div>
          <div class="stat-value">{{ formatNumber(newRegistrations.count) }}</div>
          <div class="stat-trend">
            <van-icon 
              :name="newRegistrations.growth_rate >= 0 ? 'arrow-up' : 'arrow-down'" 
              size="12" 
              :color="newRegistrations.growth_rate >= 0 ? '#07C160' : '#EE0A24'" 
            />
            <span 
              class="trend-text" 
              :class="newRegistrations.growth_rate >= 0 ? 'positive' : 'negative'"
            >
              {{ formatGrowthRate(newRegistrations.growth_rate) }}
            </span>
          </div>
        </div>

        <!-- 累计打赏数量 -->
        <div class="stat-card small">
          <div class="stat-header">
            <van-icon name="cash-back-record" size="14" color="#6A6A6A" />
            <span class="stat-title">累计打赏数量</span>
          </div>
          <div class="stat-value">{{ formatNumber(tipStats.total) }}</div>
          <div class="stat-trend">
            <van-icon 
              :name="tipStats.growth_rate >= 0 ? 'arrow-up' : 'arrow-down'" 
              size="12" 
              :color="tipStats.growth_rate >= 0 ? '#07C160' : '#EE0A24'" 
            />
            <span 
              class="trend-text" 
              :class="tipStats.growth_rate >= 0 ? 'positive' : 'negative'"
            >
              {{ formatGrowthRate(tipStats.growth_rate) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 管理菜单 -->
    <div class="menu-section">
      <h2 class="section-title">管理</h2>
      <div class="menu-cards">
        <!-- 用户管理 -->
        <div class="menu-card" @click="navigateTo('mana')">
          <div class="menu-icon">
            <van-icon name="friends-o" size="24" color="#6A6A6A" />
          </div>
          <div class="menu-title">用户管理</div>
        </div>
        
        <!-- 数据统计 -->
        <!-- <div class="menu-card" @click="navigateTo('analytics')">
          <div class="menu-icon">
            <van-icon name="chart-trending-o" size="24" color="#6A6A6A" />
          </div>
          <div class="menu-title">数据统计</div>
        </div> -->
        
        <!-- 系统设置 -->
        <div class="menu-card" @click="navigateTo('settings')">
          <div class="menu-icon">
            <van-icon name="setting-o" size="24" color="#6A6A6A" />
          </div>
          <div class="menu-title">系统设置</div>
        </div>
        
        <!-- 内容审核 -->
        <div class="menu-card" @click="navigateTo('moderation')">
          <div class="menu-icon-container">
          <div class="menu-icon">
            
              <van-icon name="todo-list-o" size="24" color="#6A6A6A" />
            
          </div>
          <van-badge :content="manaStore.pendingAudit || ''" class="audit-badge"></van-badge>
          </div>
          <div class="menu-title">信息审核</div>
        </div>

        <div class="menu-card" @click="navigateTo('adminchat')">
          <div class="menu-icon-container">
          <div class="menu-icon">
            
              <van-icon name="chat-o" size="24" color="#6A6A6A" />
            
          </div>
          <van-badge :content="manaStore.pendingAudit || ''" class="audit-badge"></van-badge>
          </div>
          <div class="menu-title">用户沟通</div>
        </div>


      </div>
    </div>
    <TabBar 
      :active-tab="activeTab" 
      @update:active-tab="activeTab = $event"
      :tabs="tabs"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import * as echarts from 'echarts/core';
import type { EChartsCoreOption } from 'echarts/core';
import { LineChart } from 'echarts/charts'; // 改为LineChart
import { useAuthStore } from '@/store/authStore';
import { useManaStore } from '@/store/manaStore'
import apiClient from '@/plugins/axios';
import { ALL_TABS, ICON_MAP, type TabItem, type IconType, type DynamicTabItem } from '@/config/tabs'
import { 
  GridComponent, 
  TooltipComponent, 
  TitleComponent,
  LegendComponent
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
const manaStore = useManaStore()
// 注册ECharts组件
echarts.use([
  LineChart, // 使用折线图
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
  CanvasRenderer
]);

const router = useRouter();

const activeTab = ref('manacenter');
const authStore = useAuthStore();
const tabs = computed(() => [...ALL_TABS, ...authStore.menuItems]);
// 登录图表引用
const loginChart = ref<HTMLDivElement | null>(null);

const loginStats = ref<any[]>([]);
const tipStats = ref({ total: 0, growth_rate: 0 });
const newRegistrations = ref({ count: 0, growth_rate: 0 });

// 获取统计数据
const fetchStats = async () => {
  try {
    const [loginRes, tipRes, regRes] = await Promise.all([
      apiClient.get('/api/admin/login-stats?days=7'),
      apiClient.get('/api/admin/tip-stats'),
      apiClient.get('/api/admin/new-registrations')
    ]);

    loginStats.value = loginRes.data || [];
    tipStats.value = tipRes.data || { total: 0, growth_rate: 0 };
    newRegistrations.value = regRes.data || { count: 0, growth_rate: 0 };
  } catch (error) {
    console.error('获取统计数据失败:', error);
  }
};

// 初始化图表
const initLoginChart = () => {
  if (!loginChart.value) return;
  const chart = echarts.init(loginChart.value);

  const option: EChartsCoreOption = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(107, 107, 107, 0.9)',
      padding: 8,
      textStyle: { fontSize: 12, color: '#fff' }
    },
    grid: {
      left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true
    },
    xAxis: {
      type: 'category',
      data: loginStats.value.map(item => item.date),
      axisLine: { lineStyle: { color: '#D9D9D9' } },
      axisLabel: { color: '#6A6A6A', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      min: 0,
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: 'rgba(217, 217, 217, 0.2)' } },
      axisLabel: { color: '#6A6A6A', fontSize: 10 }
    },
    series: [{
      name: '登录人数',
      type: 'line',
      data: loginStats.value.map(item => item.count),
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { width: 3, color: '#5470C6' },
      itemStyle: { color: '#5470C6' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(84, 112, 198, 0.3)' },
            { offset: 1, color: 'rgba(84, 112, 198, 0.05)' }
          ]
        }
      }
    }]
  };

  chart.setOption(option);

  const resizeHandler = () => chart.resize();
  window.addEventListener('resize', resizeHandler);
  onUnmounted(() => {
    window.removeEventListener('resize', resizeHandler);
    chart.dispose();
  });
};

// 格式化数字
const formatNumber = (num: number) => num.toLocaleString();

// 格式化增长率
const formatGrowthRate = (rate: number) => {
  const sign = rate >= 0 ? '+' : '';
  return `${sign}${rate.toFixed(1)}%`;
};


// 导航到指定页面
const navigateTo = (route: string) => {
  router.replace(`/${route}`);
};

// 组件挂载后初始化图表
onMounted(async() => {
  await fetchStats();
  initLoginChart();
  manaStore.fetchPendingAudit();
});
</script>

<style scoped>

.menu-icon-container {
  position: relative;
  display: inline-block; /* 改为行内块元素 */
  margin-bottom: 0px;
}

.audit-badge {
  position: absolute;
  top: -5px; /* 向上移动减少距离 */
  right: -5px; /* 向右移动减少距离 */
  z-index: 10;
  transform: scale(1.1); /* 稍微缩小徽章尺寸 */
}

/* 调整van-badge位置 */
:deep(.van-badge) {
  position: absolute;
  top: -5px;
  right: -5px;
}

/* 当数量为0时隐藏徽标 */
:deep(.van-badge--content.van-badge__content.van-badge__content--fixed) {
  display: block;
}
:deep(.van-badge__content.van-badge__content--fixed[data-v-xxxx]:empty) {
  display: none;
}
.mana-container {
  background-color: #F2EEE8;
  min-height: 100vh;
  padding: 16px;
  font-family: "Microsoft YaHei", sans-serif;
  display: flex;
  flex-direction: column;
  position: relative;
}

/* 顶部统计容器 */
.stats-container {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

/* 统计卡片通用样式 */
.stat-card {
  background-color: #FFFFFF;
  border-radius: 8px;
  border: 1px solid #D9D9D9;
  padding: 12px; /* 缩小内边距 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

/* 大卡片样式 */
.stat-card.large {
  flex: 3;
}

/* 小卡片容器 */
.small-cards {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 小卡片样式 */
.stat-card.small {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

/* 统计头部 */
.stat-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px; /* 减少底部间距 */
}

.stat-title {
  font-size: 13px; /* 缩小字体大小 */
  color: #6A6A6A;
  margin-left: 6px; /* 减少左边距 */
  white-space: nowrap; /* 防止换行 */
}

/* 统计值 */
.stat-value {
  font-size: 20px; /* 缩小字体大小 */
  font-weight: bold;
  color: #333;
  margin-bottom: 4px; /* 减少底部间距 */
}

/* 趋势统计 */
.stat-trend {
  display: flex;
  align-items: center;
  font-size: 12px; /* 缩小字体大小 */
}

.trend-text {
  font-size: 12px;
  margin-left: 4px;
}

.trend-text.positive {
  color: #07C160;
}

.trend-text.negative {
  color: #EE0A24;
}

/* 图表容器 */
.chart-container {
  height: 162px; /* 缩小图表高度 */
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 菜单部分 */
.menu-section {
  margin-bottom: 24px;
}

.section-title {
  color: #6A6A6A;
  font-size: 16px;
  margin-bottom: 16px;
  font-weight: normal;
}

/* 菜单卡片容器 */
.menu-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

/* 单个菜单卡片 */
.menu-card {
  background-color: #FFFFFF;
  border-radius: 8px;
  border: 1px solid #D9D9D9;
  padding: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100px;
}

.menu-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* 菜单图标 */
.menu-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%; /* 确保是圆形 */
  background-color: #F2EEE8;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
  /* 添加以下属性确保完美圆形 */
  overflow: hidden; 
  flex-shrink: 0; /* 防止在flex容器中变形 */
  position: relative;
}

/* 菜单标题 */
.menu-title {
  font-size: 14px;
  color: #6A6A6A;
  font-weight: 500;
}
</style>