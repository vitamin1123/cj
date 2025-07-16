<template>
  <div class="mana-container">
    <van-floating-bubble
      v-model:offset="offset"
      axis="xy"
      magnetic="x"
      icon="revoke"
      :size="54"
      :gap="10"
      @click="goBack"
      style="--van-floating-bubble-background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);"
    />

    <!-- 固定在顶部的搜索栏 -->
    <div class="sticky-header">
      <div class="search-container">
        <van-search
          v-model="searchKeyword"
          placeholder="搜索昵称 / ID"
          shape="round"
          background="#F2EEE8"
          @search="onSearch"
        />
      </div>
    </div>

    <!-- 用户列表 -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
      >
        <div
          v-for="user in list"
          :key="user.id"
          class="user-card"
          @click="goToDetail(user.id)"
        >
          <div class="card-header">
            <div class="avatar-container">
              <van-image
                width="48"
                height="48"
                :src="getAvatarUrl(user.avatar)"
                round
                fit="cover"
                lazy-load
              >
                <template v-slot:loading>
                  <div class="avatar-placeholder">
                    <van-icon name="user-circle-o" size="24" />
                  </div>
                </template>
                <template v-slot:error>
                  <div class="avatar-placeholder">
                    <van-icon name="user-circle-o" size="24" />
                  </div>
                </template>
              </van-image>
            </div>
            <div class="user-info">
              <div class="name">
                {{ user.nickname || '未填写昵称' }}
              </div>
              <div class="meta">
                <span class="gender" :class="user.gender">{{
                  user.gender === 'male' ? '♂' : '♀'
                }}</span>
                <span class="region">{{ displayRegion(user.region_code) }}</span>
              </div>
            </div>
          </div>
          <div class="card-footer">
            <van-tag 
              :type="user.updated_at !== user.created_at ? 'danger' : 'primary'" 
              
              class="status-tag"
            >
              {{ user.updated_at !== user.created_at ? '修改信息' : '注册信息' }}
            </van-tag>
            <div class="expire">注册于 {{ formatDate(user.created_at) }}</div>
          </div>
        </div>
      </van-list>
    </van-pull-refresh>

    <!-- 空状态 -->
    <div v-if="!loading && list.length === 0 && finished" class="no-data">
      <van-icon name="user-o" size="48" color="#EBE3D7" />
      <p>暂无待审核用户</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/plugins/axios'
import { areaList } from '@vant/area-data'
import {
  Image as VanImage,
  List as VanList,
  PullRefresh as VanPullRefresh,
  Search as VanSearch,
  showToast
} from 'vant'

interface AuditUser {
  id: number
  openid: string
  nickname?: string
  gender: string
  avatar?: string
  region_code?: string
  created_at: string
  updated_at: string
}

const isLoading = ref(false)
const router = useRouter()
const list = ref<AuditUser[]>([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const searchKeyword = ref('')
const offset = ref({ x: 0.05 * window.innerWidth, y: 0.03 * window.innerHeight })
const currentPage = ref(1)
const pageSize = ref(20)

const goBack = () => router.replace('/manacenter')

const getAvatarUrl = (avatar?: string) => avatar ? `/avatars/${avatar}` : ''

const displayRegion = (code?: string) => {
  if (!code) return ''
  try {
    const p = areaList.province_list[code.substring(0, 2) + '0000']
    const c = areaList.city_list[code.substring(0, 4) + '00']
    return p && c ? `${p} ${c}` : p || '未知'
  } catch {
    return '未知'
  }
}

const formatDate = (str: string) =>
  new Date(str).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })

const onSearch = () => onRefresh()

const onRefresh = () => {
  list.value = []
  currentPage.value = 1
  finished.value = false
  loading.value = true
  onLoad()
}

const onLoad = async () => {
  if (refreshing.value) refreshing.value = false
  try {
    const { data } = await apiClient.get('/api/admin/audit-list', {
      params: {
        keyword: searchKeyword.value || undefined,
        page: currentPage.value,
        pageSize: pageSize.value
      }
    })
    const users = data.list || []
    list.value.push(...users)
    loading.value = false
    if (users.length < pageSize.value) finished.value = true
    else currentPage.value++
  } catch (e) {
    loading.value = false
    finished.value = true
    showToast('加载失败')
  }
}

const goToDetail = (id: number) => {
    console.log('id: ',id)
  router.replace(`/moderation-detail/${id}`)
}

// onMounted(onLoad)
</script>

<style scoped>
.mana-container {
  background-color: #F2EEE8;
  min-height: 100vh;
  padding: 16px;
  font-family: "Microsoft YaHei", sans-serif;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sticky-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: #F2EEE8;
  padding-bottom: 12px;
}

.search-container {
  margin-bottom: 12px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.user-card {
  background-color: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.avatar-container {
  margin-right: 12px;
}

.avatar-placeholder {
  width: 48px;
  height: 48px;
  background-color: #f0f0f0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}

.user-info {
  flex: 1;
}

.name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

.meta {
  display: flex;
  gap: 12px;
  font-size: 14px;
  color: #888;
}

.gender.male {
  color: #6495ed;
}

.gender.female {
  color: #ff69b4;
}

.status-tag {
  margin-right: 8px;
}

.card-footer {
  display: flex;
  /* justify-content: space-between; */
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f5f5f5;
}

.expire {
  font-size: 12px;
  color: #888;
}

.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #888;
}
</style>