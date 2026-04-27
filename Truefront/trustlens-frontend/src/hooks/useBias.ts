import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { biasService } from '../services/biasService'
import { queryKeys } from '../store/queryKeys'
import { ScoreVersion } from '../types/score'
import toast from 'react-hot-toast'

export function useBiasMetrics(candidateId: string, version: ScoreVersion = 'original') {
  return useQuery({
    queryKey: queryKeys.bias.metrics(candidateId, version),
    queryFn: () => biasService.getBiasMetrics(candidateId, version),
    enabled: !!candidateId,
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  })
}

export function useBiasAnalysis() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: biasService.analyzeBias,
    onSuccess: (data) => {
      console.log('[useBiasAnalysis] Success:', data)
      queryClient.invalidateQueries({ queryKey: queryKeys.bias.all })
      toast.success('Bias analysis completed')
    },
    onError: (error: any) => {
      console.error('[useBiasAnalysis] Error:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to analyze bias'
      toast.error(`Bias analysis failed: ${errorMessage}`)
    },
  })
}
