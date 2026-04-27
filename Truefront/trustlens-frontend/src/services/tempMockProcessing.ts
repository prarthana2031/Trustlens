// Temporary mock processing service for testing candidate processing functionality
import { ProcessCandidateResponse } from '../types/candidate'

export const createMockProcessedCandidate = (candidateId: string): ProcessCandidateResponse => {
  console.log(`[Mock Processing] Creating processed response for candidate ${candidateId}`)
  
  // Mock processing response
  return {
    message: 'Candidate processed successfully with AI analysis',
    candidate_id: candidateId,
  }
}
