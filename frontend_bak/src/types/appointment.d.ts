export type AppointmentStatus =
  | 'pending_accept'
  | 'accepted'
  | 'to_attend'
  | 'in_progress'
  | 'evaluating'
  | 'completed'
  | 'cancelled'
  | 'refunding'
  | 'refunded'

export interface Appointment {
  id: string
  order_no: string
  learner_id: string
  mentor_id: string
  status: AppointmentStatus
  price: number
  duration_minutes: number
  scheduled_time?: string
  meeting_link?: string
  accept_nda: boolean
  created_at: string
}

export interface LessonPlan {
  content_md: string
  model_name?: string
  is_fallback: boolean
  created_at: string
}
