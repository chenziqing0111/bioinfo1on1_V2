<template>
  <view class="page">
    <view class="container">
      <!-- 用户信息区 -->
      <view v-if="userStore.isLoggedIn && userStore.userInfo" class="user-info">
        <view class="avatar">
          <image
            v-if="userStore.userInfo.avatar_url"
            :src="userStore.userInfo.avatar_url"
            class="avatar-img"
          />
          <text v-else class="avatar-text">
            {{ userStore.userInfo.nickname?.charAt(0) || '用' }}
          </text>
        </view>
        <view class="user-details">
          <text class="nickname">{{ userStore.userInfo.nickname || '未设置昵称' }}</text>
          <text class="role">{{ getRoleText(userStore.userInfo.role) }}</text>
        </view>
      </view>

      <!-- 未登录状态 -->
      <view v-else class="login-section">
        <text class="login-title">欢迎来到 BioInfo1on1</text>
        <text class="login-subtitle">生信导师一对一预约平台</text>
        <!-- #ifdef MP-WEIXIN -->
        <button class="btn-login" @click="handleLogin">微信登录</button>
        <!-- #endif -->
        <!-- #ifdef H5 -->
        <button v-if="isDev" class="btn-test-login" @click="handleTestLogin">
          测试登录
        </button>
        <text v-else class="login-tip">H5 环境暂不支持微信登录</text>
        <!-- #endif -->
      </view>

      <!-- 功能菜单 -->
      <view v-if="userStore.isLoggedIn" class="menu-list">
        <view class="menu-item" @click="goAppointments">
          <text class="menu-icon">📋</text>
          <text class="menu-text">我的订单</text>
          <text class="menu-arrow">›</text>
        </view>

        <view v-if="userStore.isTutor" class="menu-item" @click="goTutorOrders">
          <text class="menu-icon">👨‍🏫</text>
          <text class="menu-text">接单管理</text>
          <text class="menu-arrow">›</text>
        </view>

        <view class="menu-item" @click="handleLogout">
          <text class="menu-icon">🚪</text>
          <text class="menu-text">退出登录</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>

      <!-- 关于 -->
      <view class="about">
        <text class="about-title">BioInfo1on1</text>
        <text class="about-version">v1.0.0</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import type { UserRole } from '@/types/user'

const userStore = useUserStore()

// 判断是否为开发环境
const isDev = computed(() => {
  return import.meta.env.DEV || import.meta.env.MODE === 'development'
})

onMounted(() => {
  if (userStore.isLoggedIn) {
    userStore.fetchUserInfo()
  }
})

function getRoleText(role: UserRole): string {
  const roleMap: Record<UserRole, string> = {
    student: '学员',
    tutor: '导师',
    admin: '管理员'
  }
  return roleMap[role] || role
}

async function handleLogin() {
  try {
    const isNewUser = await userStore.wxLogin()

    if (isNewUser) {
      uni.showToast({
        title: '登录成功，欢迎新用户',
        icon: 'success'
      })
    } else {
      uni.showToast({
        title: '登录成功',
        icon: 'success'
      })
    }
  } catch (error: any) {
    console.error('登录失败', error)
    uni.showToast({
      title: error.message || '登录失败',
      icon: 'none'
    })
  }
}

async function handleTestLogin() {
  try {
    await userStore.testLogin()
    uni.showToast({
      title: '测试登录成功',
      icon: 'success'
    })
  } catch (error: any) {
    console.error('测试登录失败', error)
    uni.showToast({
      title: error.message || '登录失败',
      icon: 'none'
    })
  }
}

function handleLogout() {
  uni.showModal({
    title: '确认退出',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        userStore.logout()
        uni.showToast({
          title: '已退出登录',
          icon: 'success'
        })
      }
    }
  })
}

function goAppointments() {
  uni.switchTab({
    url: '/pages/appointment/list'
  })
}

function goTutorOrders() {
  uni.showToast({
    title: '导师端功能开发中',
    icon: 'none'
  })
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(180deg, #2B579A 0%, #f5f5f5 40%);
}

.container {
  padding: 40rpx;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 32rpx;
  padding: 40rpx;
  background: white;
  border-radius: 16rpx;
  margin-bottom: 40rpx;

  .avatar {
    width: 120rpx;
    height: 120rpx;
    border-radius: 50%;
    overflow: hidden;
    background: #e0e0e0;
    display: flex;
    align-items: center;
    justify-content: center;

    .avatar-img {
      width: 100%;
      height: 100%;
    }

    .avatar-text {
      font-size: 48rpx;
      font-weight: 600;
      color: white;
    }
  }

  .user-details {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 12rpx;

    .nickname {
      font-size: 36rpx;
      font-weight: 600;
      color: #333;
    }

    .role {
      font-size: 26rpx;
      color: #999;
    }
  }
}

.login-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24rpx;
  padding: 80rpx 40rpx;
  background: white;
  border-radius: 16rpx;
  margin-bottom: 40rpx;

  .login-title {
    font-size: 40rpx;
    font-weight: bold;
    color: #333;
  }

  .login-subtitle {
    font-size: 28rpx;
    color: #666;
    margin-bottom: 20rpx;
  }

  .btn-login {
    background: linear-gradient(135deg, #2B579A 0%, #3D6FB8 100%);
    color: white;
    border: none;
    border-radius: 48rpx;
    font-size: 32rpx;
    font-weight: 600;
    padding: 24rpx 80rpx;
  }

  .btn-test-login {
    background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
    color: white;
    border: none;
    border-radius: 48rpx;
    font-size: 32rpx;
    font-weight: 600;
    padding: 24rpx 80rpx;
  }

  .login-tip {
    font-size: 26rpx;
    color: #999;
  }
}

.menu-list {
  background: white;
  border-radius: 16rpx;
  overflow: hidden;
  margin-bottom: 40rpx;

  .menu-item {
    display: flex;
    align-items: center;
    gap: 24rpx;
    padding: 32rpx;
    border-bottom: 2rpx solid #f0f0f0;

    &:last-child {
      border-bottom: none;
    }

    .menu-icon {
      font-size: 40rpx;
    }

    .menu-text {
      flex: 1;
      font-size: 28rpx;
      color: #333;
    }

    .menu-arrow {
      font-size: 40rpx;
      color: #999;
    }

    &:active {
      background: #f9f9f9;
    }
  }
}

.about {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  padding: 40rpx 0;

  .about-title {
    font-size: 32rpx;
    font-weight: 600;
    color: white;
  }

  .about-version {
    font-size: 24rpx;
    color: rgba(255, 255, 255, 0.8);
  }
}
</style>
