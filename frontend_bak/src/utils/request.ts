import { useUserStore } from '@/stores/user'

const BASE_URL = import.meta.env.VITE_API_BASE_URL

interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  error?: { code: number; message: string }
}

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  showLoading?: boolean
}

export async function request<T = any>(options: RequestOptions): Promise<T> {
  const userStore = useUserStore()
  const { url, method = 'GET', data, showLoading = true } = options

  if (showLoading) {
    uni.showLoading({ title: '加载中...' })
  }

  try {
    const response = await uni.request({
      url: `${BASE_URL}${url}`,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        ...(userStore.token ? { Authorization: `Bearer ${userStore.token}` } : {})
      }
    })

    const result = response.data as ApiResponse<T>
    if (showLoading) uni.hideLoading()

    if (!result.success) {
      // Token 过期
      if (result.error?.code === 1001 || result.error?.code === 1002) {
        userStore.logout()
        uni.navigateTo({ url: '/pages/user/index' })
      }
      throw new Error(result.error?.message || '请求失败')
    }

    return result.data
  } catch (error: any) {
    if (showLoading) uni.hideLoading()
    uni.showToast({
      title: error.message || '网络错误',
      icon: 'none',
      duration: 2000
    })
    throw error
  }
}

export const get = <T>(url: string, data?: any) => request<T>({ url, method: 'GET', data })
export const post = <T>(url: string, data?: any) => request<T>({ url, method: 'POST', data })
export const put = <T>(url: string, data?: any) => request<T>({ url, method: 'PUT', data })
export const del = <T>(url: string, data?: any) => request<T>({ url, method: 'DELETE', data })
