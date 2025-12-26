<template>
  <view class="page">
    <view class="container">
      <!-- 订单列表 -->
      <view v-if="appointments.length > 0" class="appointment-list">
        <view
          v-for="item in appointments"
          :key="item.id"
          class="appointment-card"
          @click="goDetail(item.id)"
        >
          <view class="card-header">
            <text class="order-no">订单号: {{ item.order_no }}</text>
            <view class="status-badge" :class="`status-${item.status}`">
              {{ getStatusText(item.status) }}
            </view>
          </view>

          <view class="card-body">
            <view class="info-row">
              <text class="label">预约时间：</text>
              <text class="value">{{ formatDate(item.scheduled_time) }}</text>
            </view>
            <view class="info-row">
              <text class="label">课程时长：</text>
              <text class="value">{{ item.duration_minutes }} 分钟</text>
            </view>
            <view class="info-row">
              <text class="label">课程费用：</text>
              <text class="value price">¥{{ item.price }}</text>
            </view>
          </view>

          <view class="card-footer">
            <text class="create-time">创建于 {{ formatDate(item.created_at) }}</text>
            <text class="arrow">›</text>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view v-else-if="!loading" class="empty">
        <text class="empty-text">暂无订单</text>
        <button class="btn-go-home" @click="goHome">
          去首页看看
        </button>
      </view>

      <!-- 加载状态 -->
      <view v-if="loading" class="loading">
        <text>加载中...</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { appointmentApi } from '@/api/appointment'
import { useUserStore } from '@/stores/user'
import type { Appointment, AppointmentStatus } from '@/types/appointment'

const userStore = useUserStore()
const appointments = ref<Appointment[]>([])
const loading = ref(false)

onMounted(() => {
  if (userStore.checkLogin(false)) {
    loadAppointments()
  }
})

async function loadAppointments() {
  loading.value = true
  try {
    appointments.value = await appointmentApi.getList()
  } catch (error) {
    console.error('加载订单列表失败', error)
  } finally {
    loading.value = false
  }
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

function formatDate(dateStr?: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

function goDetail(id: string) {
  uni.navigateTo({
    url: `/pages/appointment/detail?id=${id}`
  })
}

function goHome() {
  uni.switchTab({
    url: '/pages/index/index'
  })
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: #f5f5f5;
}

.container {
  padding: 40rpx;
}

.appointment-list {
  .appointment-card {
    background: white;
    border-radius: 16rpx;
    padding: 32rpx;
    margin-bottom: 32rpx;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24rpx;

      .order-no {
        font-size: 26rpx;
        color: #999;
      }

      .status-badge {
        padding: 6rpx 16rpx;
        border-radius: 24rpx;
        font-size: 24rpx;
        font-weight: 600;

        &.status-pending_accept {
          background: #FFF3CD;
          color: #856404;
        }

        &.status-accepted,
        &.status-to_attend {
          background: #D1ECF1;
          color: #0C5460;
        }

        &.status-in_progress {
          background: #D4EDDA;
          color: #155724;
        }

        &.status-evaluating {
          background: #E2E3E5;
          color: #383D41;
        }

        &.status-completed {
          background: #D4EDDA;
          color: #155724;
        }

        &.status-cancelled,
        &.status-refunded {
          background: #F8D7DA;
          color: #721C24;
        }

        &.status-refunding {
          background: #FFF3CD;
          color: #856404;
        }
      }
    }

    .card-body {
      .info-row {
        display: flex;
        margin-bottom: 16rpx;

        .label {
          font-size: 26rpx;
          color: #666;
          flex-shrink: 0;
        }

        .value {
          font-size: 26rpx;
          color: #333;

          &.price {
            font-weight: 600;
            color: #FF6B6B;
          }
        }
      }
    }

    .card-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 24rpx;
      padding-top: 24rpx;
      border-top: 2rpx solid #f0f0f0;

      .create-time {
        font-size: 24rpx;
        color: #999;
      }

      .arrow {
        font-size: 40rpx;
        color: #999;
      }
    }
  }
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 0;

  .empty-text {
    font-size: 28rpx;
    color: #999;
    margin-bottom: 40rpx;
  }

  .btn-go-home {
    background: #2B579A;
    color: white;
    border: none;
    border-radius: 48rpx;
    font-size: 28rpx;
    padding: 20rpx 60rpx;
  }
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 120rpx 0;
  font-size: 28rpx;
  color: #999;
}
</style>
