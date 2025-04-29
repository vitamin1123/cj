<template>
  <div class="index-container">
    <!-- 折叠面板 - 移出滚动容器并添加 sticky 样式 -->
    <div class="sticky-collapse">
      <van-collapse v-model="activeNames">
        <van-collapse-item title="搜索条件" name="1">
          <van-form @submit="onSearch">
            <!-- 性别改为radio -->
            <van-field
              label="性别"
            >
              <template #input>
                <van-radio-group v-model="searchForm.gender" direction="horizontal">
                  <van-radio name="男">男</van-radio>
                  <van-radio name="女">女</van-radio>
                </van-radio-group>
              </template>
            </van-field>
            
            <!-- 年龄范围选择器 -->
            <van-field
              v-model="ageRangeText"
              label="年龄范围"
              placeholder="请选择年龄范围"
              is-link
              readonly
              @click="showAgeRangePicker = true"
            />
            <van-popup v-model="showAgeRangePicker" round position="bottom">
              <van-picker
                :columns="ageRangeColumns"
                @confirm="onAgeRangeConfirm"
                @cancel="showAgeRangePicker = false"
              />
            </van-popup>
            
            <!-- 区域选择器 -->
            <van-field
              v-model="regionText"
              label="区域"
              placeholder="请选择区域"
              is-link
              readonly
              @click="showRegionPicker = true"
            />
            <van-popup v-model="showRegionPicker" round position="bottom">
              <van-area
                title="选择地区"
                :area-list="areaList"
                :columns-num="3"
                :columns-placeholder="['请选择', '请选择', '请选择']"
                @confirm="onRegionConfirm"
                @cancel="showRegionPicker = false"
              />
            </van-popup>
            
            <!-- 属相选择器 -->
            <van-field
              v-model="searchForm.zodiac"
              label="属相"
              placeholder="请选择属相"
              is-link
              readonly
              @click="showZodiacPicker = true"
            />
            <van-popup v-model="showZodiacPicker" round position="bottom">
              <van-picker
                :columns="zodiacOptions"
                @confirm="onZodiacConfirm"
                @cancel="showZodiacPicker = false"
              />
            </van-popup>
            
            <!-- 星座选择器 -->
            <van-field
              v-model="searchForm.constellation"
              label="星座"
              placeholder="请选择星座"
              is-link
              readonly
              @click="showConstellationPicker = true"
            />
            <van-popup v-model="showConstellationPicker" round position="bottom">
              <van-picker
                :columns="constellationOptions"
                @confirm="onConstellationConfirm"
                @cancel="showConstellationPicker = false"
              />
            </van-popup>
            
            <!-- 身高范围选择器 -->
            <van-field
              v-model="heightRangeText"
              label="身高范围"
              placeholder="请选择身高范围"
              is-link
              readonly
              @click="showHeightRangePicker = true"
            />
            <van-popup v-model="showHeightRangePicker" round position="bottom">
              <van-picker
                :columns="heightRangeColumns"
                @confirm="onHeightRangeConfirm"
                @cancel="showHeightRangePicker = false"
              />
            </van-popup>
            
            <div style="margin: 16px;">
              <van-button round block color="#ffb6c1" native-type="submit">
                搜索
              </van-button>
            </div>
          </van-form>
        </van-collapse-item>
      </van-collapse>
    </div>
  
    <!-- 卡片列表 -->
    <RecycleScroller
      class="scroller"
      :items="listData"
      :item-size="180"
      key-field="id"
      v-slot="{ item }"
    >
      <div class="card" :class="{'male-card': item.gender === '男', 'female-card': item.gender === '女'}">
          <div class="heart-icon" @click="toggleHeart(item)">
            <van-icon name="like" :class="{'heart-animate': item.heartAnimate}" />
          </div>
          <div class="card-left">
              <img :src="item.avatar" class="avatar" />
          </div>
          <div class="card-right">
              <div class="info-item">年龄: {{ item.age }}</div>
              <div class="info-item">区域: {{ item.region }}</div>
              <div class="info-item">身高: {{ item.height }}cm</div>
              <div class="info-item">属相: {{ item.zodiac }}</div>
              <div class="info-item">简介: {{ item.desc }}</div>
          </div>
      </div>
    </RecycleScroller>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Collapse, CollapseItem, Field, Form, Popup, Picker, Button, RadioGroup, Radio, Area } from 'vant'
import { RecycleScroller } from 'vue-virtual-scroller';
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css'
import { areaList } from '@vant/area-data';

// 搜索条件
const activeNames = ref(['1'])
const searchForm = ref({
  gender: '',
  minAge: 18,
  maxAge: 50,
  region: [],
  zodiac: '',
  constellation: '',
  minHeight: '',
  maxHeight: ''
})

// 选择器控制
const showAgeRangePicker = ref(false)
const showRegionPicker = ref(false)
const showZodiacPicker = ref(false)
const showConstellationPicker = ref(false)
const showHeightRangePicker = ref(false)

// 选项数据
const genderOptions = ['男', '女']
const zodiacOptions = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
const constellationOptions = [
  '白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座',
  '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座'
]

// 年龄选项 (18-100岁)
const ageOptions = Array.from({length: 83}, (_, i) => (18 + i).toString())

// 年龄范围列
const ageRangeColumns = [
  ageOptions.map(value => ({ text: `${value}岁`, value })),
  ageOptions.map(value => ({ text: `${value}岁`, value }))
]

// 年龄范围文本
const ageRangeText = computed(() => {
  if (searchForm.value.minAge && searchForm.value.maxAge) {
    return `${searchForm.value.minAge}岁 - ${searchForm.value.maxAge}岁`
  } else if (searchForm.value.minAge) {
    return `≥${searchForm.value.minAge}岁`
  } else if (searchForm.value.maxAge) {
    return `≤${searchForm.value.maxAge}岁`
  }
  return ''
})

// 区域文本
const regionText = computed(() => {
  if (searchForm.value.region && searchForm.value.region.length > 0) {
    return searchForm.value.region.join(' ')
  }
  return ''
})

// 身高选项 (140-240cm)
const heightOptions = Array.from({length: 101}, (_, i) => (140 + i).toString())

// 身高范围列
const heightRangeColumns = [
  heightOptions.map(value => ({ text: `${value}cm`, value })),
  heightOptions.map(value => ({ text: `${value}cm`, value }))
]

// 身高范围文本
const heightRangeText = computed(() => {
  if (searchForm.value.minHeight && searchForm.value.maxHeight) {
    return `${searchForm.value.minHeight}cm - ${searchForm.value.maxHeight}cm`
  } else if (searchForm.value.minHeight) {
    return `≥${searchForm.value.minHeight}cm`
  } else if (searchForm.value.maxHeight) {
    return `≤${searchForm.value.maxHeight}cm`
  }
  return ''
})

// 年龄范围确认
const onAgeRangeConfirm = (values) => {
  const [min, max] = values
  searchForm.value.minAge = min
  searchForm.value.maxAge = max > min ? max : ''
  showAgeRangePicker.value = false
}

// 区域确认
const onRegionConfirm = (values) => {
  const selected = values.filter(item => item.code !== '')
  searchForm.value.region = selected.map(item => item.name)
  showRegionPicker.value = false
}

// 属相确认
const onZodiacConfirm = (value) => {
  searchForm.value.zodiac = value
  showZodiacPicker.value = false
}

// 星座确认
const onConstellationConfirm = (value) => {
  searchForm.value.constellation = value
  showConstellationPicker.value = false
}

// 身高范围确认
const onHeightRangeConfirm = (values) => {
  const [min, max] = values
  searchForm.value.minHeight = min
  searchForm.value.maxHeight = max > min ? max : ''
  showHeightRangePicker.value = false
}

// 随机触发爱心动画
const randomHeartAnimation = () => {
  const visibleCards = listData.value.filter(item => item.isVisible)
  if (visibleCards.length > 0) {
    const randomIndex = Math.floor(Math.random() * visibleCards.length)
    visibleCards[randomIndex].heartAnimate = true
    
    // 3秒后重置动画状态
    setTimeout(() => {
      visibleCards[randomIndex].heartAnimate = false
    }, 800)
  }
}

// 初始化Intersection Observer
let observer
onMounted(() => {
  observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      const cardId = parseInt(entry.target.getAttribute('data-id'))
      const card = listData.value.find(item => item.id === cardId)
      if (card) {
        card.isVisible = entry.isIntersecting
      }
    })
    
    // 每5秒随机触发一次动画
    setInterval(randomHeartAnimation, 5000)
  }, {
    threshold: 0.5
  })
  
  // 观察所有卡片
  document.querySelectorAll('.card').forEach(card => {
    observer.observe(card)
  })
})

// 处理爱心点击
const toggleHeart = (item) => {
  item.heartAnimate = !item.heartAnimate
}

const onSearch = () => {
  console.log('搜索条件:', searchForm.value)
  
  // 根据搜索条件过滤数据
  const filteredData = listData.value.filter(item => {
    // 性别过滤
    if (searchForm.value.gender && item.gender !== searchForm.value.gender) {
      return false
    }
    
    // 年龄范围过滤
    const age = item.age
    const minAge = searchForm.value.minAge
    const maxAge = searchForm.value.maxAge
    if (minAge && age < parseInt(minAge)) {
      return false
    }
    if (maxAge && age > parseInt(maxAge)) {
      return false
    }
    
    // 区域过滤
    if (searchForm.value.region && searchForm.value.region.length > 0 && 
        !searchForm.value.region.some(region => item.region.includes(region))) {
      return false
    }
    
    // 属相过滤
    if (searchForm.value.zodiac && item.zodiac !== searchForm.value.zodiac) {
      return false
    }
    
    // 星座过滤
    if (searchForm.value.constellation && item.constellation !== searchForm.value.constellation) {
      return false
    }
    
    // 身高范围过滤
    const height = item.height
    const minHeight = searchForm.value.minHeight
    const maxHeight = searchForm.value.maxHeight
    if (minHeight && height < parseInt(minHeight)) {
      return false
    }
    if (maxHeight && height > parseInt(maxHeight)) {
      return false
    }
    
    return true
  })
  
  // 更新显示的数据
  listData.value = filteredData
}

// 模拟数据
const listData = ref(Array.from({ length: 20 }, (_, i) => ({
  id: i,
  avatar: 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg',
  gender: genderOptions[i % 2],
  heartAnimate: false,
  isVisible: false,
  element: null,
  age: 20 + i,
  region: ['北京', '上海', '广州', '深圳', '杭州', '成都'][i % 6],
  height: 160 + i,
  zodiac: zodiacOptions[i % zodiacOptions.length],
  constellation: constellationOptions[i % constellationOptions.length],
  desc: `这是一个关于第${i + 1}位用户的简短描述`
})))
</script>

<style scoped>
.index-container {
  padding: 12px;
  background-color: #f7f8fa;
  min-height: 100vh;
}

.heart-icon {
  position: absolute;
  top: 10px;
  right: 20px;
  z-index: 1;
  font-size: 24px;
  color: #ccc;
  stroke: currentColor;
  stroke-width: 1px;
  fill: none;
}

.heart-animate {
  animation: heartBeat 0.8s ease-in-out;
  color: #ff4757;
  fill: #ff4757;
}

@keyframes heartBeat {
  0% { transform: scale(1); }
  14% { transform: scale(1.3); }
  28% { transform: scale(1); }
  42% { transform: scale(1.3); }
  70% { transform: scale(1); }
}

.sticky-collapse {
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: #f7f8fa;
  padding-bottom: 12px;
}

.scroller {
  height: calc(100vh - 50px);
}
  
.card {
  display: flex;
  width: 96%;
  margin: 0 auto 16px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  min-height: 140px;
  position: relative;
  box-shadow: none;
}

.card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  bottom: 8px;
  width: 4px;
  border-radius: 2px;
}

.male-card::before {
  background-color: #add8e6;
}

.female-card::before {
  background-color: #ffb6c1;
}
  
.card-left {
  width: 80px;
  height: 80px;
  margin-right: 16px;
  margin-left: 8px;
}
  
.avatar {
  width: 100%;
  height: 100%;
  border-radius: 4px;
  object-fit: cover;
}
  
.card-right {
  flex: 1;
}
  
.info-item {
  margin-bottom: 8px;
  font-size: 14px;
  color: #666;
}

/* 调整radio样式 */
:deep(.van-radio) {
  margin-right: 20px;
}
</style>