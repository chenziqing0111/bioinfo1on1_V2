<template>
  <view class="page">
    <view class="header">
      <text class="title">BioInfo1on1</text>
      <text class="subtitle">生信导师一对一预约平台</text>
    </view>

    <!-- 筛选栏 -->
    <view class="filter-bar">
      <text>共 {{ mentors.length }} 位导师</text>
    </view>

    <!-- 导师列表 -->
    <view class="mentor-list">
      <mentor-card
        v-for="mentor in mentors"
        :key="mentor.id"
        :mentor="mentor"
        @book="handleBook"
      />
    </view>

    <!-- 空状态 -->
    <view v-if="!loading && mentors.length === 0" class="empty">
      <text class="empty-text">暂无导师</text>
    </view>

    <!-- 加载状态 -->
    <view v-if="loading" class="loading">
      <text>加载中...</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { mentorApi } from '@/api/mentor'
import type { MentorListItem } from '@/types/mentor'
import MentorCard from '@/components/MentorCard.vue'

const mentors = ref<MentorListItem[]>([])
const loading = ref(false)

onMounted(() => {
  loadMentors()
})

async function loadMentors() {
  loading.value = true
  try {
    const result = await mentorApi.getList()
    mentors.value = result.items
  } catch (error) {
    console.error('加载导师列表失败', error)
  } finally {
    loading.value = false
  }
}

function handleBook(mentorId: string) {
  uni.navigateTo({
    url: `/pages/appointment/create?mentor_id=${mentorId}`
  })
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: #f5f5f5;
}

.header {
  background: linear-gradient(135deg, #2B579A 0%, #3D6FB8 100%);
  padding: 60rpx 40rpx 40rpx;
  color: white;

  .title {
    display: block;
    font-size: 48rpx;
    font-weight: bold;
    margin-bottom: 12rpx;
  }

  .subtitle {
    font-size: 28rpx;
    opacity: 0.9;
  }
}

.filter-bar {
  padding: 24rpx 40rpx;
  background: white;
  font-size: 26rpx;
  color: #666;
}

.mentor-list {
  padding: 20rpx 40rpx;
}

.empty {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 120rpx 0;

  .empty-text {
    font-size: 28rpx;
    color: #999;
  }
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60rpx 0;
  font-size: 28rpx;
  color: #999;
}
</style>
