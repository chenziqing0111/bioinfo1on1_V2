import { get, post } from '@/utils/request'
import type { MentorInfo, MentorListItem } from '@/types/mentor'

interface ListResponse<T> {
  items: T[]
  total: number
}

export const mentorApi = {
  getList: (params?: any) => get<ListResponse<MentorListItem>>('/api/v1/mentors', params),
  getDetail: (id: string) => get<MentorInfo>(`/api/v1/mentors/${id}`),
  apply: (data: any) => post<MentorInfo>('/api/v1/mentors/apply', data),
  getTags: () => get<Record<string, any>>('/api/v1/mentors/tags')
}
