<template>
  <view class="page">
    <!-- 加载状态 -->
    <view v-if="loading" class="loading">
      <text>加载中...</text>
    </view>

    <!-- 导师信息 -->
    <template v-else-if="mentor">
      <!-- 头部信息 -->
      <view class="header">
        <view class="avatar-section">
          <image
            v-if="mentor.avatar_url"
            class="avatar"
            :src="mentor.avatar_url"
            mode="aspectFill"
          />
          <view v-else class="avatar avatar-placeholder">
            <text>{{ (mentor.nickname || '导师')[0] }}</text>
          </view>
        </view>
        <view class="info-section">
          <text class="nickname">{{ mentor.nickname || '导师' }}</text>
          <text class="title">{{ mentor.title || '生信导师' }}</text>
          <text class="institution">{{ mentor.institution || '暂无机构信息' }}</text>
        </view>
      </view>

      <!-- 统计数据 -->
      <view class="stats-card">
        <view class="stat-item">
          <text class="stat-value">{{ mentor.rating.toFixed(1) }}</text>
          <text class="stat-label">评分</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-value">{{ mentor.total_sessions }}</text>
          <text class="stat-label">咨询次数</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-value price">¥{{ mentor.hourly_rate }}</text>
          <text class="stat-label">时薪</text>
        </view>
      </view>

      <!-- 技能标签 -->
      <view v-if="mentor.tags && mentor.tags.length > 0" class="section">
        <text class="section-title">擅长领域</text>
        <view class="tags-list">
          <text v-for="tag in mentor.tags" :key="tag" class="tag">
            {{ tag }}
          </text>
        </view>
      </view>

      <!-- 个人简介 -->
      <view class="section">
        <text class="section-title">个人简介</text>
        <text class="bio">{{ mentor.bio || '这位导师还没有填写简介' }}</text>
      </view>

      <!-- 荣誉成就 -->
      <view v-if="mentor.honors" class="section">
        <text class="section-title">荣誉成就</text>
        <text class="honors">{{ mentor.honors }}</text>
      </view>

      <!-- 评价列表 -->
      <view class="section">
        <text class="section-title">学员评价 ({{ reviews.length }})</text>
        <view v-if="reviews.length > 0" class="reviews-list">
          <view v-for="review in reviews" :key="review.id" class="review-item">
            <view class="review-header">
              <view class="reviewer-info">
                <image
                  v-if="review.reviewer_avatar"
                  class="reviewer-avatar"
                  :src="review.reviewer_avatar"
                  mode="aspectFill"
                />
                <view v-else class="reviewer-avatar avatar-placeholder">
                  <text>{{ (review.reviewer_nickname || '学员')[0] }}</text>
                </view>
                <text class="reviewer-name">{{ review.reviewer_nickname || '匿名学员' }}</text>
              </view>
              <view class="rating-stars">
                <text v-for="i in 5" :key="i" class="star" :class="{ active: i <= review.rating }">
                  ★
                </text>
              </view>
            </view>
            <text v-if="review.content" class="review-content">{{ review.content }}</text>
            <text class="review-time">{{ formatDate(review.created_at) }}</text>
          </view>
        </view>
        <view v-else class="empty-reviews">
          <text>暂无评价</text>
        </view>
      </view>

      <!-- 底部占位 -->
      <view class="bottom-placeholder"></view>
    </template>

    <!-- 错误状态 -->
    <view v-else class="error">
      <text class="error-text">导师信息加载失败</text>
      <button class="btn-retry" @click="loadData">重试</button>
    </view>

    <!-- 底部固定按钮 -->
    <view v-if="mentor" class="bottom-bar">
      <button class="btn-book" @click="handleBook">立即预约</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { mentorApi } from '@/api/mentor'
import { reviewApi } from '@/api/review'
import type { MentorInfo } from '@/types/mentor'
import type { Review } from '@/types/review'

const mentor = ref<MentorInfo | null>(null)
const reviews = ref<Review[]>([])
const loading = ref(true)
const mentorId = ref('')

onMounted(() => {
  // 获取页面参数
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1] as any
  const options = currentPage.options || {}

  mentorId.value = options.id

  if (!mentorId.value) {
    uni.showToast({
      title: '缺少导师ID',
      icon: 'none'
    })
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
    return
  }

  loadData()
})

async function loadData() {
  loading.value = true
  try {
    // 并行加载导师信息和评价
    const [mentorData, reviewsResult] = await Promise.all([
      mentorApi.getDetail(mentorId.value),
      reviewApi.getMentorReviews(mentorId.value).catch(() => ({ items: [], total: 0 }))
    ])
    mentor.value = mentorData
    reviews.value = reviewsResult.items
  } catch (error) {
    console.error('加载导师信息失败', error)
    mentor.value = null
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function handleBook() {
  uni.navigateTo({
    url: `/pages/appointment/create?mentor_id=${mentorId.value}`
  })
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: env(safe-area-inset-bottom);
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 120rpx 0;
  font-size: 28rpx;
  color: #999;
}

.header {
  background: linear-gradient(135deg, #2B579A 0%, #3D6FB8 100%);
  padding: 60rpx 40rpx 40rpx;
  display: flex;
  gap: 32rpx;

  .avatar-section {
    flex-shrink: 0;

    .avatar {
      width: 140rpx;
      height: 140rpx;
      border-radius: 50%;
      border: 4rpx solid rgba(255, 255, 255, 0.3);
    }

    .avatar-placeholder {
      display: flex;
      justify-content: center;
      align-items: center;
      background: rgba(255, 255, 255, 0.2);

      text {
        font-size: 48rpx;
        color: white;
        font-weight: 600;
      }
    }
  }

  .info-section {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 12rpx;

    .nickname {
      font-size: 36rpx;
      font-weight: 600;
      color: white;
    }

    .title {
      font-size: 28rpx;
      color: rgba(255, 255, 255, 0.9);
    }

    .institution {
      font-size: 26rpx;
      color: rgba(255, 255, 255, 0.7);
    }
  }
}

.stats-card {
  background: white;
  margin: -30rpx 40rpx 0;
  border-radius: 16rpx;
  padding: 32rpx;
  display: flex;
  justify-content: space-around;
  align-items: center;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);

  .stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8rpx;

    .stat-value {
      font-size: 36rpx;
      font-weight: 600;
      color: #333;

      &.price {
        color: #FF6B6B;
      }
    }

    .stat-label {
      font-size: 24rpx;
      color: #999;
    }
  }

  .stat-divider {
    width: 2rpx;
    height: 60rpx;
    background: #f0f0f0;
  }
}

.section {
  background: white;
  margin: 24rpx 40rpx;
  border-radius: 16rpx;
  padding: 32rpx;

  .section-title {
    display: block;
    font-size: 30rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 24rpx;
  }
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;

  .tag {
    padding: 10rpx 24rpx;
    background: #f0f5ff;
    border-radius: 32rpx;
    font-size: 26rpx;
    color: #2B579A;
  }
}

.bio,
.honors {
  font-size: 28rpx;
  line-height: 1.8;
  color: #666;
}

.reviews-list {
  .review-item {
    padding: 24rpx 0;
    border-bottom: 2rpx solid #f5f5f5;

    &:last-child {
      border-bottom: none;
      padding-bottom: 0;
    }

    .review-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16rpx;

      .reviewer-info {
        display: flex;
        align-items: center;
        gap: 16rpx;

        .reviewer-avatar {
          width: 56rpx;
          height: 56rpx;
          border-radius: 50%;
        }

        .avatar-placeholder {
          display: flex;
          justify-content: center;
          align-items: center;
          background: #e0e0e0;

          text {
            font-size: 24rpx;
            color: #666;
          }
        }

        .reviewer-name {
          font-size: 26rpx;
          color: #333;
        }
      }

      .rating-stars {
        .star {
          font-size: 28rpx;
          color: #e0e0e0;

          &.active {
            color: #FFD700;
          }
        }
      }
    }

    .review-content {
      display: block;
      font-size: 28rpx;
      line-height: 1.6;
      color: #666;
      margin-bottom: 12rpx;
    }

    .review-time {
      font-size: 24rpx;
      color: #999;
    }
  }
}

.empty-reviews {
  padding: 40rpx 0;
  text-align: center;
  font-size: 28rpx;
  color: #999;
}

.bottom-placeholder {
  height: 140rpx;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  padding: 20rpx 40rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);

  .btn-book {
    width: 100%;
    background: linear-gradient(135deg, #2B579A 0%, #3D6FB8 100%);
    color: white;
    border: none;
    border-radius: 12rpx;
    font-size: 32rpx;
    font-weight: 600;
    padding: 28rpx 0;
  }
}

.error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 0;

  .error-text {
    font-size: 28rpx;
    color: #999;
    margin-bottom: 32rpx;
  }

  .btn-retry {
    background: #2B579A;
    color: white;
    border: none;
    border-radius: 48rpx;
    font-size: 28rpx;
    padding: 20rpx 60rpx;
  }
}
</style>
