<template>
  <view class="mentor-card" @click="goDetail">
    <view class="mentor-header">
      <text class="mentor-title">{{ mentor.title || '导师' }}</text>
      <text class="mentor-institution">{{ mentor.institution || '暂无机构' }}</text>
    </view>

    <view class="mentor-stats">
      <view class="stat-item">
        <text class="stat-label">评分</text>
        <text class="stat-value">{{ mentor.rating }}</text>
      </view>
      <view class="stat-item">
        <text class="stat-label">课程</text>
        <text class="stat-value">{{ mentor.total_sessions }}</text>
      </view>
      <view class="stat-item">
        <text class="stat-label">时薪</text>
        <text class="stat-value">¥{{ mentor.hourly_rate }}</text>
      </view>
    </view>

    <view class="mentor-tags" v-if="mentor.tags && mentor.tags.length > 0">
      <text class="tag" v-for="tag in mentor.tags" :key="tag">{{ tag }}</text>
    </view>

    <view class="mentor-actions">
      <button class="btn-primary" @click.stop="handleBook">立即预约</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import type { MentorListItem } from '@/types/mentor'

const props = defineProps<{
  mentor: MentorListItem
}>()

const emit = defineEmits<{
  book: [mentorId: string]
}>()

function goDetail() {
  uni.navigateTo({
    url: `/pages/mentor/detail?id=${props.mentor.id}`
  })
}

function handleBook() {
  emit('book', props.mentor.id)
}
</script>

<style lang="scss" scoped>
.mentor-card {
  background: white;
  border-radius: 12rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.mentor-header {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  margin-bottom: 20rpx;

  .mentor-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
  }

  .mentor-institution {
    font-size: 26rpx;
    color: #999;
  }
}

.mentor-stats {
  display: flex;
  gap: 40rpx;
  margin-bottom: 20rpx;

  .stat-item {
    display: flex;
    flex-direction: column;
    gap: 8rpx;

    .stat-label {
      font-size: 24rpx;
      color: #999;
    }

    .stat-value {
      font-size: 28rpx;
      font-weight: 600;
      color: #2B579A;
    }
  }
}

.mentor-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-bottom: 20rpx;

  .tag {
    padding: 6rpx 16rpx;
    background: #f0f0f0;
    border-radius: 24rpx;
    font-size: 24rpx;
    color: #666;
  }
}

.mentor-actions {
  .btn-primary {
    background: #2B579A;
    color: white;
    border: none;
    border-radius: 8rpx;
    font-size: 28rpx;
    padding: 16rpx 0;
  }
}
</style>
