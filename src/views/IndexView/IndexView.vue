<template>
    <div class="index-container">
      <!-- 折叠面板 - 移出滚动容器并添加 sticky 样式 -->
      <div class="sticky-collapse">
        <van-collapse v-model="activeNames">
          <van-collapse-item title="搜索条件" name="1">
            <van-form @submit="onSearch">
              <van-field
                v-model="searchForm.gender"
                label="性别"
                placeholder="请选择性别"
                is-link
                readonly
                @click="showGenderPicker = true"
              />
              <van-popup v-model="showGenderPicker" round position="bottom">
                <van-picker
                  :columns="genderOptions"
                  @confirm="onGenderConfirm"
                  @cancel="showGenderPicker = false"
                />
              </van-popup>
    
              <van-field
                v-model="searchForm.age"
                label="年龄"
                placeholder="请输入年龄"
                type="number"
              />
    
              <van-field
                v-model="searchForm.region"
                label="区域"
                placeholder="请选择区域"
                is-link
                readonly
                @click="showRegionPicker = true"
              />
              <van-popup v-model="showRegionPicker" round position="bottom">
                <van-picker
                  :columns="regionOptions"
                  @confirm="onRegionConfirm"
                  @cancel="showRegionPicker = false"
                />
              </van-popup>
    
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
    
              <van-field
                v-model="searchForm.height"
                label="身高"
                placeholder="请输入身高(cm)"
                type="number"
              />
    
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
  import { ref } from 'vue'
  import { Collapse, CollapseItem, Field, Form, Popup, Picker, Button } from 'vant'
  import { RecycleScroller } from 'vue-virtual-scroller';
  import 'vue-virtual-scroller/dist/vue-virtual-scroller.css'
  
  // 搜索条件
  const activeNames = ref(['1'])
  const searchForm = ref({
    gender: '',
    age: '',
    region: '',
    zodiac: '',
    constellation: '',
    height: ''
  })
  
  // 选择器控制
  const showGenderPicker = ref(false)
  const showRegionPicker = ref(false)
  const showZodiacPicker = ref(false)
  const showConstellationPicker = ref(false)
  
  // 选项数据
  const genderOptions = ['男', '女']
  const regionOptions = ['北京', '上海', '广州', '深圳', '杭州', '成都']
  const zodiacOptions = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
  const constellationOptions = [
    '白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座',
    '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座'
  ]
  
  // 选择器确认
  const onGenderConfirm = (value) => {
    searchForm.value.gender = value
    showGenderPicker.value = false
  }
  
  const onRegionConfirm = (value) => {
    searchForm.value.region = value
    showRegionPicker.value = false
  }
  
  const onZodiacConfirm = (value) => {
    searchForm.value.zodiac = value
    showZodiacPicker.value = false
  }
  
  const onConstellationConfirm = (value) => {
    searchForm.value.constellation = value
    showConstellationPicker.value = false
  }
  
  // 搜索
  const onSearch = () => {
    console.log('搜索条件:', searchForm.value)
    // 这里可以添加搜索逻辑
  }
  
  // 模拟数据 - 添加gender字段
  const listData = ref(Array.from({ length: 20 }, (_, i) => ({
    id: i,
    avatar: 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg',
    gender: genderOptions[i % 2], // 添加性别字段
    age: 20 + i,
    region: regionOptions[i % regionOptions.length],
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
    box-shadow: none; /* 移除阴影 */
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
    background-color: #add8e6; /* 淡蓝色 */
}

.female-card::before {
    background-color: #ffb6c1; /* 淡粉色 */
}
    
  .card-left {
    width: 80px;
    height: 80px;
    margin-right: 16px;
    margin-left: 8px; /* 为左侧边框留出空间 */
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
  </style>