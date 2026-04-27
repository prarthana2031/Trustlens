import apiClient from './api'
import { ScoreResponse, ScoreVersion } from '../types/score'

export const scoringService = {
  // Get candidate score
  getScore: async (candidateId: string, version: ScoreVersion = 'original'): Promise<ScoreResponse> => {
    const response = await apiClient.get<ScoreResponse>(`/scores/candidate/${candidateId}`, {
      params: { version },
    })
    return response.data
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
