<template>
  <view class="page">
    <!-- 加载状态 -->
    <view v-if="loading" class="loading">
      <text>加载中...</text>
    </view>

    <!-- 订单信息 -->
    <template v-else-if="appointment">
      <view class="container">
        <!-- 状态卡片 -->
        <view class="status-card" :class="`status-${appointment.status}`">
          <view class="status-icon">
            <text>{{ getStatusIcon(appointment.status) }}</text>
          </view>
          <text class="status-text">{{ getStatusText(appointment.status) }}</text>
          <text class="status-desc">{{ getStatusDesc(appointment.status) }}</text>
        </view>

        <!-- 导师信息 -->
        <view class="section">
          <text class="section-title">导师信息</text>
          <view class="mentor-info" @click="goMentorDetail">
            <view class="mentor-avatar-wrap">
              <image
                v-if="appointment.mentor_avatar"
                class="mentor-avatar"
                :src="appointment.mentor_avatar"
                mode="aspectFill"
              />
              <view v-else class="mentor-avatar avatar-placeholder">
                <text>{{ (appointment.mentor_nickname || '导师')[0] }}</text>
              </view>
            </view>
            <view class="mentor-detail">
              <text class="mentor-name">{{ appointment.mentor_nickname || '导师' }}</text>
              <text class="mentor-title">{{ appointment.mentor_title || '生信导师' }}</text>
            </view>
            <text class="arrow">›</text>
          </view>
        </view>

        <!-- 订单信息 -->
        <view class="section">
          <text class="section-title">订单信息</text>
          <view class="info-list">
            <view class="info-item">
              <text class="info-label">订单编号</text>
              <text class="info-value">{{ appointment.order_no }}</text>
            </view>
            <view class="info-item">
              <text class="info-label">预约时间</text>
              <text class="info-value">{{ formatDateTime(appointment.scheduled_time) }}</text>
            </view>
            <view class="info-item">
              <text class="info-label">课程时长</text>
              <text class="info-value">{{ appointment.duration_minutes }} 分钟</text>
            </view>
            <view class="info-item">
              <text class="info-label">课程费用</text>
              <text class="info-value price">¥{{ appointment.price }}</text>
            </view>
            <view class="info-item">
              <text class="info-label">创建时间</text>
              <text class="info-value">{{ formatDateTime(appointment.created_at) }}</text>
            </view>
          </view>
        </view>

        <!-- 需求描述 -->
        <view v-if="appointment.requirements" class="section">
          <text class="section-title">需求描述</text>
          <text class="requirements">{{ appointment.requirements }}</text>
        </view>

        <!-- 会议链接 (accepted/to_attend 状态) -->
        <view
          v-if="['accepted', 'to_attend', 'in_progress'].includes(appointment.status) && appointment.meeting_link"
          class="section"
        >
          <text class="section-title">会议信息</text>
          <view class="meeting-info">
            <text class="meeting-link">{{ appointment.meeting_link }}</text>
            <button class="btn-copy" @click="copyMeetingLink">复制链接</button>
          </view>
        </view>

        <!-- 取消原因 (cancelled 状态) -->
        <view v-if="appointment.status === 'cancelled' && appointment.cancel_reason" class="section">
          <text class="section-title">取消原因</text>
          <text class="cancel-reason">{{ appointment.cancel_reason }}</text>
        </view>

        <!-- 评价内容 (completed 状态) -->
        <view v-if="appointment.status === 'completed' && appointment.review" class="section">
          <text class="section-title">我的评价</text>
          <view class="review-content">
            <view class="rating-stars">
              <text v-for="i in 5" :key="i" class="star" :class="{ active: i <= appointment.review.rating }">
                ★
              </text>
            </view>
            <text v-if="appointment.review.content" class="review-text">
              {{ appointment.review.content }}
            </text>
            <text class="review-time">{{ formatDateTime(appointment.review.created_at) }}</text>
          </view>
        </view>

        <!-- 底部占位 -->
        <view class="bottom-placeholder"></view>
      </view>

      <!-- 底部操作栏 -->
      <view class="bottom-bar">
        <!-- 待接单 -->
        <view v-if="appointment.status === 'pending_accept'" class="btn-group">
          <button class="btn-waiting" disabled>等待导师接单</button>
        </view>

        <!-- 已接单 / 待上课 -->
        <view v-else-if="['accepted', 'to_attend'].includes(appointment.status)" class="btn-group">
          <button class="btn-secondary" @click="goLessonPlan">查看教案</button>
          <button v-if="appointment.meeting_link" class="btn-primary" @click="joinMeeting">
            进入会议
          </button>
        </view>

        <!-- 待评价 -->
        <view v-else-if="appointment.status === 'evaluating'" class="btn-group">
          <button class="btn-secondary" @click="goLessonPlan">查看教案</button>
          <button class="btn-primary" @click="goReview">去评价</button>
        </view>

        <!-- 已完成 -->
        <view v-else-if="appointment.status === 'completed'" class="btn-group">
          <button class="btn-secondary" @click="goLessonPlan">查看教案</button>
          <button class="btn-primary" @click="bookAgain">再次预约</button>
        </view>

        <!-- 已取消 -->
        <view v-else-if="appointment.status === 'cancelled'" class="btn-group">
          <button class="btn-primary" @click="bookAgain">重新预约</button>
        </view>
      </view>
    </template>

    <!-- 错误状态 -->
    <view v-else class="error">
      <text class="error-text">订单信息加载失败</text>
      <button class="btn-retry" @click="loadData">重试</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { appointmentApi } from '@/api/appointment'
import type { Appointment, AppointmentStatus } from '@/types/appointment'

const appointment = ref<Appointment | null>(null)
const loading = ref(true)
const appointmentId = ref('')

onMounted(() => {
  // 获取页面参数
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1] as any
  const options = currentPage.options || {}

  appointmentId.value = options.id

  if (!appointmentId.value) {
    uni.showToast({
      title: '缺少订单ID',
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
    appointment.value = await appointmentApi.getDetail(appointmentId.value)
  } catch (error) {
    console.error('加载订单信息失败', error)
    appointment.value = null
  } finally {
    loading.value = false
  }
}

function getStatusIcon(status: AppointmentStatus): string {
  const iconMap: Record<AppointmentStatus, string> = {
    pending_accept: '⏳',
    accepted: '✓',
    to_attend: '📅',
    in_progress: '🎓',
    evaluating: '⭐',
    completed: '✅',
    cancelled: '✗',
    refunding: '💰',
    refunded: '💸'
  }
  return iconMap[status] || '📋'
}

function getStatusText(status: AppointmentStatus): string {
  const statusMap: Record<AppointmentStatus, string> = {
    pending_accept: '待接单',
    accepted: '已接单',
    to_attend: '待上课',
    in_progress: '上课中',
    evaluating: '待评价',
    completed: '已完成',
    cancelled: '已取消',
    refunding: '退款中',
    refunded: '已退款'
  }
  return statusMap[status] || status
}

function getStatusDesc(status: AppointmentStatus): string {
  const descMap: Record<AppointmentStatus, string> = {
    pending_accept: '导师正在审核您的预约，请耐心等待',
    accepted: '导师已接单，请留意会议链接',
    to_attend: '即将开始上课，请准时参加',
    in_progress: '课程进行中，祝您学习愉快',
    evaluating: '课程已结束，请对导师进行评价',
    completed: '感谢您的信任，期待再次为您服务',
    cancelled: '订单已取消',
    refunding: '退款申请处理中，请耐心等待',
    refunded: '退款已完成'
  }
  return descMap[status] || ''
}

function formatDateTime(dateStr?: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

function goMentorDetail() {
  if (appointment.value) {
    uni.navigateTo({
      url: `/pages/mentor/detail?id=${appointment.value.mentor_id}`
    })
  }
}

function goLessonPlan() {
  uni.navigateTo({
    url: `/pages/appointment/lesson-plan?id=${appointmentId.value}`
  })
}

function goReview() {
  uni.navigateTo({
    url: `/pages/review/create?appointment_id=${appointmentId.value}`
  })
}

function bookAgain() {
  if (appointment.value) {
    uni.navigateTo({
      url: `/pages/appointment/create?mentor_id=${appointment.value.mentor_id}`
    })
  }
}

function copyMeetingLink() {
  if (appointment.value?.meeting_link) {
    uni.setClipboardData({
      data: appointment.value.meeting_link,
      success: () => {
        uni.showToast({
          title: '链接已复制',
          icon: 'success'
        })
      }
    })
  }
}

function joinMeeting() {
  if (appointment.value?.meeting_link) {
    // 尝试打开外部链接
    // #ifdef H5
    window.open(appointment.value.meeting_link, '_blank')
    // #endif

    // #ifndef H5
    uni.setClipboardData({
      data: appointment.value.meeting_link,
      success: () => {
        uni.showModal({
          title: '会议链接已复制',
          content: '请在浏览器中粘贴链接加入会议',
          showCancel: false
        })
      }
    })
    // #endif
  }
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

.container {
  padding: 0 40rpx;
}

.status-card {
  background: linear-gradient(135deg, #2B579A 0%, #3D6FB8 100%);
  margin: 40rpx 0;
  border-radius: 16rpx;
  padding: 48rpx 32rpx;
  text-align: center;

  &.status-completed {
    background: linear-gradient(135deg, #28a745 0%, #34ce57 100%);
  }

  &.status-cancelled,
  &.status-refunded {
    background: linear-gradient(135deg, #6c757d 0%, #868e96 100%);
  }

  &.status-evaluating {
    background: linear-gradient(135deg, #fd7e14 0%, #f9a825 100%);
  }

  .status-icon {
    font-size: 64rpx;
    margin-bottom: 16rpx;
  }

  .status-text {
    display: block;
    font-size: 36rpx;
    font-weight: 600;
    color: white;
    margin-bottom: 12rpx;
  }

  .status-desc {
    font-size: 26rpx;
    color: rgba(255, 255, 255, 0.8);
  }
}

.section {
  background: white;
  border-radius: 16rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;

  .section-title {
    display: block;
    font-size: 30rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 24rpx;
  }
}

.mentor-info {
  display: flex;
  align-items: center;
  gap: 20rpx;

  .mentor-avatar-wrap {
    flex-shrink: 0;

    .mentor-avatar {
      width: 80rpx;
      height: 80rpx;
      border-radius: 50%;
    }

    .avatar-placeholder {
      display: flex;
      justify-content: center;
      align-items: center;
      background: #e0e0e0;

      text {
        font-size: 32rpx;
        color: #666;
      }
    }
  }

  .mentor-detail {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8rpx;

    .mentor-name {
      font-size: 30rpx;
      font-weight: 600;
      color: #333;
    }

    .mentor-title {
      font-size: 26rpx;
      color: #999;
    }
  }

  .arrow {
    font-size: 40rpx;
    color: #999;
  }
}

.info-list {
  .info-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20rpx 0;
    border-bottom: 2rpx solid #f5f5f5;

    &:last-child {
      border-bottom: none;
      padding-bottom: 0;
    }

    .info-label {
      font-size: 28rpx;
      color: #666;
    }

    .info-value {
      font-size: 28rpx;
      color: #333;

      &.price {
        font-weight: 600;
        color: #FF6B6B;
      }
    }
  }
}

.requirements {
  font-size: 28rpx;
  line-height: 1.8;
  color: #666;
}

.meeting-info {
  display: flex;
  align-items: center;
  gap: 20rpx;

  .meeting-link {
    flex: 1;
    font-size: 26rpx;
    color: #2B579A;
    word-break: break-all;
  }

  .btn-copy {
    flex-shrink: 0;
    background: #f0f5ff;
    color: #2B579A;
    border: none;
    border-radius: 8rpx;
    font-size: 24rpx;
    padding: 12rpx 24rpx;
  }
}

.cancel-reason {
  font-size: 28rpx;
  line-height: 1.6;
  color: #dc3545;
}

.review-content {
  .rating-stars {
    margin-bottom: 16rpx;

    .star {
      font-size: 36rpx;
      color: #e0e0e0;

      &.active {
        color: #FFD700;
      }
    }
  }

  .review-text {
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

  .btn-group {
    display: flex;
    gap: 24rpx;

    button {
      flex: 1;
      border: none;
      border-radius: 12rpx;
      font-size: 30rpx;
      font-weight: 600;
      padding: 24rpx 0;
    }

    .btn-primary {
      background: linear-gradient(135deg, #2B579A 0%, #3D6FB8 100%);
      color: white;
    }

    .btn-secondary {
      background: #f5f5f5;
      color: #333;
    }

    .btn-waiting {
      background: #e0e0e0;
      color: #999;
    }
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
