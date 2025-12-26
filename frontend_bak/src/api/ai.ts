import { post } from '@/utils/request'
import type { MatchResult } from '@/types/ai'

export const aiApi = {
  match: (requirement: string) => post<MatchResult>('/api/v1/ai/match', { requirement })
}
