export interface MatchRecommendation {
  mentor_id: string
  score: number
  reason: string
  can_solve: string[]
}

export interface MatchResult {
  recommendations: MatchRecommendation[]
}
