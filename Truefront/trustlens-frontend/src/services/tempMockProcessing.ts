// Temporary mock processing service for testing candidate processing functionality
import { ProcessCandidateResponse } from '../types/candidate'
import { ScoreResponse, ScoreBreakdown } from '../types/score'

export const createMockProcessedCandidate = (candidateId: string): ProcessCandidateResponse => {
  console.log(`[Mock Processing] Creating processed response for candidate ${candidateId}`)
  
  // Mock extracted skills and job role analysis
  const mockBreakdown: ScoreBreakdown = {
    skills: [
      { skill: 'JavaScript', score: 75, relevance: 0.8 },
      { skill: 'React', score: 78, relevance: 0.85 },
      { skill: 'TypeScript', score: 72, relevance: 0.75 },
      { skill: 'Node.js', score: 70, relevance: 0.7 },
    ],
    experience: 65,
    education: 80,
    projects: 75,
    soft_skills: 78,
    overall: 73.2,
  }

  return {
    message: 'Candidate processed successfully with AI analysis',
    candidate_id: candidateId,
  }
}
