export interface MentorInfo {
  id: string
  user_id: string
  nickname?: string
  avatar_url?: string
  bio?: string
  title?: string
  institution?: string
  honors?: string
  hourly_rate: number
  rating: number
  total_sessions: number
  tags: string[]
  audit_status: 'pending' | 'approved' | 'rejected'
  created_at: string
}

export interface MentorListItem {
  id: string
  title?: string
  institution?: string
  hourly_rate: number
  rating: number
  total_sessions: number
  tags: string[]
}
