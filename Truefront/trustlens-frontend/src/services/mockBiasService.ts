import { DemographicBreakdown, DisparityIndicator } from '../types/bias'

/**
 * Generate mock bias analysis data for demonstration
 * This is used when the real backend bias endpoint is not available
 */
export function generateMockBiasAnalysis(candidates: Array<{ candidate_id: string; attributes: any }>) {
  console.log('[MockBiasService] Generating mock analysis for', candidates.length, 'candidates')

  // Group candidates by job role for demographic breakdown
  const jobRoleGroups: Record<string, any[]> = {}
  candidates.forEach(c => {
    const role = c.attributes?.job_role || 'Unknown'
    if (!jobRoleGroups[role]) jobRoleGroups[role] = []
    jobRoleGroups[role].push(c)
  })

  // Create demographic breakdown
  const demographicBreakdown: DemographicBreakdown[] = [
    {
      category: 'Job Role',
      groups: Object.entries(jobRoleGroups).reduce((acc, [role, group]) => {
        acc[role] = {
          count: group.length,
          avg_score: 65 + Math.random() * 25, // Random score between 65-90
          selection_rate: 0.4 + Math.random() * 0.4, // Random rate between 40-80%
        }
        return acc
      }, {} as Record<string, { count: number; avg_score: number; selection_rate: number }>),
    },
    {
      category: 'Skills Level',
      groups: {
        'Beginner': { count: Math.floor(candidates.length * 0.3), avg_score: 55, selection_rate: 0.25 },
        'Intermediate': { count: Math.floor(candidates.length * 0.5), avg_score: 72, selection_rate: 0.55 },
        'Advanced': { count: Math.floor(candidates.length * 0.2), avg_score: 85, selection_rate: 0.75 },
      },
    },
    {
      category: 'Experience',
      groups: {
        '0-2 years': { count: Math.floor(candidates.length * 0.25), avg_score: 60, selection_rate: 0.30 },
        '3-5 years': { count: Math.floor(candidates.length * 0.40), avg_score: 75, selection_rate: 0.60 },
        '6+ years': { count: Math.floor(candidates.length * 0.35), avg_score: 80, selection_rate: 0.70 },
      },
    },
  ]

  // Generate disparity indicators
  const disparityIndicators: DisparityIndicator[] = [
    {
      group: 'Female Candidates',
      score: 82.5,
      benchmark: 85.0,
      disparity: 0.97,
      severity: 'low',
    },
    {
      group: 'Junior (0-2 years)',
      score: 65.0,
      benchmark: 78.0,
      disparity: 0.83,
      severity: 'medium',
    },
    {
      group: 'Beginner Skills',
      score: 58.0,
      benchmark: 75.0,
      disparity: 0.77,
      severity: 'medium',
    },
    {
      group: 'Frontend Developers',
      score: 80.0,
      benchmark: 82.0,
      disparity: 0.98,
      severity: 'low',
    },
  ]

  // Calculate overall fairness score (weighted average)
  const overallFairnessScore = 78.5

  const result = {
    demographic_breakdown: demographicBreakdown,
    disparity_indicators: disparityIndicators,
    overall_fairness_score: overallFairnessScore,
    analysis_timestamp: new Date().toISOString(),
    candidates_analyzed: candidates.length,
  }

  console.log('[MockBiasService] Generated mock result:', result)
  return result
}
