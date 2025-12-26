export type UserRole = 'student' | 'tutor' | 'admin'

export interface UserInfo {
  id: string
  openid: string
  role: UserRole
  nickname?: string
  avatar_url?: string
  bio?: string
  created_at: string
}

export interface WxLoginResponse {
  access_token: string
  token_type: string
  is_new_user: boolean
}
