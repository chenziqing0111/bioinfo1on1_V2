import { post, get } from '@/utils/request'
import type { WxLoginResponse, UserInfo } from '@/types/user'

export const authApi = {
  wxLogin: (code: string) => post<WxLoginResponse>('/api/v1/auth/wx-login', { code }),
  getMe: () => get<UserInfo>('/api/v1/auth/me')
}
