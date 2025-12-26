import { get, post } from '@/utils/request'
import type { Review } from '@/types/review'

interface ListResponse<T> {
  items: T[]
  total: number
}

export const reviewApi = {
  getMentorReviews: (mentorId: string) => get<ListResponse<Review>>(`/api/v1/reviews/mentor/${mentorId}`),
  create: (data: { appointment_id: string; rating: number; content?: string }) =>
    post<Review>('/api/v1/reviews', data)
}
