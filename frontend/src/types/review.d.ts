export interface Review {
  id: string
  appointment_id: string
  reviewer_id: string
  reviewer_nickname?: string
  reviewer_avatar?: string
  rating: number
  content?: string
  created_at: string
}
