<template>
  <view class="page">
    <view class="container">
      <!-- 导师信息 -->
      <view v-if="mentor" class="mentor-info">
        <text class="mentor-title">{{ mentor.title || '导师' }}</text>
        <text class="mentor-institution">{{ mentor.institution || '' }}</text>
        <view class="mentor-rate">
          <text class="rate-label">时薪：</text>
          <text class="rate-value">¥{{ mentor.hourly_rate }}/小时</text>
        </view>
      </view>

      <!-- 预约时间 -->
      <view class="form-section">
        <text class="section-title">预约时间</text>
        <picker
          mode="date"
          :value="dateValue"
          @change="onDateChange"
          :start="minDate"
        >
          <view class="picker-item">
            <text>{{ dateValue || '请选择日期' }}</text>
            <text class="arrow">›</text>
          </view>
        </picker>
        <picker
          mode="time"
          :value="timeValue"
          @change="onTimeChange"
        >
          <view class="picker-item">
            <text>{{ timeValue || '请选择时间' }}</text>
            <text class="arrow">›</text>
          </view>
        </picker>
      </view>

      <!-- 课程时长 -->
      <view class="form-section">
        <text class="section-title">课程时长</text>
        <radio-group @change="onDurationChange">
          <label class="duration-option">
            <radio :value="60" :checked="duration === 60" />
            <text>60 分钟</text>
          </label>
          <label class="duration-option">
            <radio :value="90" :checked="duration === 90" />
            <text>90 分钟</text>
          </label>
          <label class="duration-option">
            <radio :value="120" :checked="duration === 120" />
            <text>120 分钟</text>
          </label>
        </radio-group>
      </view>

      <!-- 需求描述 -->
      <view class="form-section">
        <text class="section-title">需求描述（至少20字）</text>
        <textarea
          v-model="requirements"
          placeholder="请详细描述您的问题和需求..."
          :maxlength="2000"
          class="textarea"
          auto-height
        />
        <text class="char-count">{{ requirements.length }}/2000</text>
      </view>

      <!-- NDA 协议 -->
      <view class="nda-section">
        <text class="nda-title">保密协议</text>
        <view class="nda-content">
          <text>
            1. 导师承诺对课程中涉及的学员代码、数据、研究内容严格保密。
            2. 未经学员许可，不得向第三方透露任何课程相关信息。
            3. 课程结束后，导师将删除所有学员提供的敏感文件。
          </text>
        </view>
        <view class="nda-checkbox">
          <checkbox :checked="acceptNda" @tap="acceptNda = !acceptNda" />
          <text class="nda-text" @tap="acceptNda = !acceptNda">我已阅读并同意上述保密协议</text>
        </view>
      </view>

      <!-- 价格信息 -->
      <view class="price-info">
        <text class="price-label">总计：</text>
        <text class="price-value">¥{{ totalPrice }}</text>
      </view>

      <!-- 提交按钮 -->
      <button
        class="submit-btn"
        :disabled="!canSubmit"
        :class="{ disabled: !canSubmit }"
        @click="handleSubmit"
      >
        确认预约
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { mentorApi } from '@/api/mentor'
import { appointmentApi } from '@/api/appointment'
import { useUserStore } from '@/stores/user'
import type { MentorInfo } from '@/types/mentor'

const userStore = useUserStore()
const mentor = ref<MentorInfo | null>(null)
const dateValue = ref('')
const timeValue = ref('')
const duration = ref(60)
const requirements = ref('')
const acceptNda = ref(false)

// 最小日期（明天）
const minDate = computed(() => {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  return tomorrow.toISOString().split('T')[0]
})

// 总价
const totalPrice = computed(() => {
  if (!mentor.value) return 0
  return ((mentor.value.hourly_rate / 60) * duration.value).toFixed(2)
})

// 是否可提交
const canSubmit = computed(() => {
  const result = {
    mentor: !!mentor.value,
    dateValue: dateValue.value,
    timeValue: timeValue.value,
    requirementsLength: requirements.value.length,
    acceptNda: acceptNda.value
  }
  console.log('canSubmit 检查:', result)
  return (
    mentor.value &&
    dateValue.value &&
    timeValue.value &&
    requirements.value.length >= 20 &&
    acceptNda.value
  )
})

onMounted(async () => {
  if (!userStore.checkLogin()) return

  // 获取页面参数
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1] as any
  const options = currentPage.options || {}

  const mentorId = options.mentor_id
  const requirementFromParam = options.requirement
    ? decodeURIComponent(options.requirement)
    : ''

  if (!mentorId) {
    uni.showToast({
      title: '缺少导师信息',
      icon: 'none'
    })
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
    return
  }

  // 加载导师信息
  try {
    mentor.value = await mentorApi.getDetail(mentorId)
    requirements.value = requirementFromParam
  } catch (error) {
    console.error('加载导师信息失败', error)
  }
})

function onDateChange(e: any) {
  dateValue.value = e.detail.value
}

function onTimeChange(e: any) {
  timeValue.value = e.detail.value
}

function onDurationChange(e: any) {
  duration.value = Number(e.detail.value)
}

async function handleSubmit() {
  if (!canSubmit.value) return

  if (!acceptNda.value) {
    uni.showToast({
      title: '请先同意保密协议',
      icon: 'none'
    })
    return
  }

  try {
    const scheduledTime = new Date(`${dateValue.value}T${timeValue.value}:00`)

    const result = await appointmentApi.create({
      mentor_id: mentor.value!.id,
      scheduled_time: scheduledTime.toISOString(),
      duration_minutes: duration.value,
      requirements: requirements.value,
      accept_nda: true
    })

    uni.showToast({
      title: '预约成功',
      icon: 'success'
    })

    setTimeout(() => {
      uni.redirectTo({
        url: `/pages/appointment/detail?id=${result.id}`
      })
    }, 1500)
  } catch (error: any) {
    console.error('创建订单失败', error)
  }
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

.mentor-info {
  background: white;
  border-radius: 16rpx;
  padding: 32rpx;
  margin-bottom: 32rpx;

  .mentor-title {
    display: block;
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 12rpx;
  }

  .mentor-institution {
    display: block;
    font-size: 26rpx;
    color: #999;
    margin-bottom: 20rpx;
  }

  .mentor-rate {
    .rate-label {
      font-size: 26rpx;
      color: #666;
    }

    .rate-value {
      font-size: 28rpx;
      font-weight: 600;
      color: #2B579A;
    }
  }
}

.form-section {
  background: white;
  border-radius: 16rpx;
  padding: 32rpx;
  margin-bottom: 32rpx;

  .section-title {
    display: block;
    font-size: 28rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 24rpx;
  }

  .picker-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24rpx;
    border: 2rpx solid #e0e0e0;
    border-radius: 12rpx;
    margin-bottom: 20rpx;

    .arrow {
      font-size: 40rpx;
      color: #999;
    }
  }

  .duration-option {
    display: flex;
    align-items: center;
    gap: 16rpx;
    padding: 20rpx 0;

    text {
      font-size: 28rpx;
    }
  }

  .textarea {
    width: 100%;
    min-height: 200rpx;
    padding: 20rpx;
    border: 2rpx solid #e0e0e0;
    border-radius: 12rpx;
    font-size: 28rpx;
    line-height: 1.6;
  }

  .char-count {
    display: block;
    margin-top: 12rpx;
    text-align: right;
    font-size: 24rpx;
    color: #999;
  }
}

.nda-section {
  background: white;
  border-radius: 16rpx;
  padding: 32rpx;
  margin-bottom: 32rpx;

  .nda-title {
    display: block;
    font-size: 28rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 20rpx;
  }

  .nda-content {
    background: #f9f9f9;
    padding: 24rpx;
    border-radius: 12rpx;
    margin-bottom: 24rpx;

    text {
      font-size: 26rpx;
      line-height: 1.8;
      color: #666;
    }
  }

  .nda-checkbox {
    display: flex;
    align-items: center;
    gap: 16rpx;

    text {
      font-size: 26rpx;
      color: #333;
    }
  }
}

.price-info {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 32rpx;

  .price-label {
    font-size: 28rpx;
    color: #666;
  }

  .price-value {
    font-size: 40rpx;
    font-weight: bold;
    color: #FF6B6B;
  }
}

.submit-btn {
  width: 100%;
  background: linear-gradient(135deg, #2B579A 0%, #3D6FB8 100%);
  color: white;
  border: none;
  border-radius: 12rpx;
  font-size: 32rpx;
  font-weight: 600;
  padding: 28rpx 0;

  &.disabled {
    opacity: 0.5;
  }
}
</style>
