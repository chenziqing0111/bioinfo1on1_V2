import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { UserInfo } from '@/types/user'

export const useUserStore = defineStore('user', () => {
  const token = ref(uni.getStorageSync('token') || '')
  const userInfo = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value)
  const isTutor = computed(() => userInfo.value?.role === 'tutor')

  async function wxLogin() {
    // #ifdef MP-WEIXIN
    const { code } = await uni.login({ provider: 'weixin' })
    const result = await authApi.wxLogin(code)

    token.value = result.access_token
    uni.setStorageSync('token', token.value)

    await fetchUserInfo()
    return result.is_new_user
    // #endif

    // #ifdef H5
    // H5 环境暂时返回 false
    console.warn('H5 环境需要实现手机号登录')
    return false
    // #endif
  }

  async function fetchUserInfo() {
    if (!token.value) return
    try {
      userInfo.value = await authApi.getMe()
    } catch (error) {
      console.error('获取用户信息失败', error)
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    uni.removeStorageSync('token')
  }

  function checkLogin(redirect = true): boolean {
    if (!isLoggedIn.value && redirect) {
      uni.showToast({
        title: '请先登录',
        icon: 'none'
      })
      setTimeout(() => {
        uni.navigateTo({ url: '/pages/user/index' })
      }, 1500)
    }
    return isLoggedIn.value
  }

  async function testLogin() {
    const result = await authApi.testLogin()
    token.value = result.access_token
    uni.setStorageSync('token', token.value)
    await fetchUserInfo()
    return result.is_new_user
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    isTutor,
    wxLogin,
    testLogin,
    fetchUserInfo,
    logout,
    checkLogin
  }
})
