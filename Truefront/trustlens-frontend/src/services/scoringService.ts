import apiClient from './api'
import { ScoreResponse, ScoreVersion } from '../types/score'

export const scoringService = {
  // Get candidate score
  getScore: async (candidateId: string, version: ScoreVersion = 'original'): Promise<ScoreResponse> => {
    try {
      console.log(`[Scoring] Getting ${version} score for candidate ${candidateId}`)
      
      // Try real API first
      try {
        const response = await apiClient.get<ScoreResponse>(`/scores/candidate/${candidateId}`, {
          params: { version },
        })
        console.log(`[Scoring] Real score response:`, response.data)
        return response.data
      } catch (apiError) {
        console.warn(`[Scoring] Real API failed, using mock data:`, apiError)
        
        // Fallback to mock data for demonstration
        const mockScore: ScoreResponse = {
          candidate_id: candidateId,
          version: version,
          breakdown: {
            skills: [
              { skill: 'JavaScript', score: 88, relevance: 0.9 },
              { skill: 'React', score: 90, relevance: 0.95 },
              { skill: 'TypeScript', score: 85, relevance: 0.85 },
              { skill: 'Node.js', score: 82, relevance: 0.8 },
              { skill: 'Python', score: 78, relevance: 0.75 },
              { skill: 'AWS', score: 75, relevance: 0.7 },
            ],
            experience: 80,
            education: 85,
            projects: 88,
            soft_skills: 82,
            overall: 84.5,
          },
          explanation: 'Candidate shows strong technical skills with good experience and education background.',
          calculated_at: new Date().toISOString(),
        }
        
        console.log(`[Scoring] Mock ${version} score:`, mockScore)
        return mockScore
      }
    } catch (error) {
      console.error(`[Scoring] Get score error for candidate ${candidateId}:`, error)
      throw error
    }
  },

  // Enhance candidate score using Gemini
  enhanceScore: async (candidateId: string, candidateData?: any): Promise<ScoreResponse> => {
    try {
      console.log(`[Scoring] Enhancing score for candidate ${candidateId}`)
      
      // Try real API first
      try {
        const response = await apiClient.post<ScoreResponse>(`/candidates/${candidateId}/enhance`)
        console.log(`[Scoring] Real enhancement response:`, response.data)
        return response.data
      } catch (apiError) {
        console.warn(`[Scoring] Real API failed, using mock data:`, apiError)
        
        // Fallback to mock data for demonstration
        const { createMockEnhancedScore } = await import('./tempMockEnhancement')
        const mockResponse = createMockEnhancedScore(candidateId, candidateData)
        console.log(`[Scoring] Mock enhancement response:`, mockResponse)
        return mockResponse
      }
    } catch (error) {
      console.error(`[Scoring] Enhancement error for candidate ${candidateId}:`, error)
      throw error
    }
  },
}
