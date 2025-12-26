import { get, post } from '@/utils/request'
import type { Appointment, LessonPlan } from '@/types/appointment'

export const appointmentApi = {
  create: (data: any) => post<Appointment>('/api/v1/appointments', data),
  getList: (params?: any) => get<Appointment[]>('/api/v1/appointments', params),
  getDetail: (id: string) => get<Appointment>(`/api/v1/appointments/${id}`),
  accept: (id: string, meetingLink?: string) =>
    post(`/api/v1/appointments/${id}/accept`, { meeting_link: meetingLink }),
  cancel: (id: string, reason: string) =>
    post(`/api/v1/appointments/${id}/cancel`, { reason }),
  getLessonPlan: (id: string) => get<LessonPlan>(`/api/v1/appointments/${id}/lesson-plan`)
}
