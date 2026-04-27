import apiClient from './api'
import { BiasMetricsResponse } from '../types/bias'
import { ScoreVersion } from '../types/score'

export const biasService = {
  // Get bias metrics for a candidate
  getBiasMetrics: async (
    candidateId: string,
    version: ScoreVersion = 'original'
  ): Promise<BiasMetricsResponse> => {
    const response = await apiClient.get<BiasMetricsResponse>('/bias/metrics', {
      params: {
        candidate_id: candidateId,
        version,
      },
    })
    return response.data
  },

  // Analyze bias for multiple candidates
  analyzeBias: async (data: {
    candidates: Array<{ candidate_id: string; score: number; attributes: Record<string, any> }>
  }): Promise<any> => {
    console.log('[BiasService] Analyzing bias for candidates:', data.candidates.length)
    console.log('[BiasService] Request data:', JSON.stringify(data, null, 2))
    
    try {
      const response = await apiClient.post('/bias/analyze', data)
      console.log('[BiasService] Response:', response.data)
      return response.data
    } catch (error) {
      console.error('[BiasService] Error:', error)
      throw error
    }
  },
}

