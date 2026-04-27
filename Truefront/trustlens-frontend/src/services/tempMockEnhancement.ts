// Temporary mock enhancement service for testing AI enhancement functionality
import { ScoreResponse, ScoreBreakdown } from '../types/score'

export const createMockEnhancedScore = (candidateId: string, candidateData?: any): ScoreResponse => {
  console.log(`[Mock Enhancement] Creating enhanced score for candidate ${candidateId}`)
  
  // Calculate score based on candidate data
  const calculateScore = (skills: string[] = [], jobRole: string = '') => {
    let skillsScore = 0
    let experienceScore = 60 // Default experience score
    let educationScore = 80 // Default education score
    let projectsScore = 70 // Default projects score
    let softSkillsScore = 75 // Default soft skills score
    
    // Calculate skills score based on provided skills
    if (skills && skills.length > 0) {
      const highValueSkills = [
        'javascript', 'react', 'typescript', 'node.js', 'python', 'java', 
        'aws', 'docker', 'mongodb', 'postgresql', 'git', 'rest api'
      ]
      
      skills.forEach(skill => {
        const skillLower = skill.toLowerCase().trim()
        if (highValueSkills.includes(skillLower)) {
          skillsScore += 85 + Math.random() * 10 // 85-95 for high-value skills
        } else {
          skillsScore += 70 + Math.random() * 15 // 70-85 for other skills
        }
      })
      
      // Average the skills score
      skillsScore = skillsScore / skills.length
    } else {
      // Default skills if none provided
      skillsScore = 75
    }
    
    // Adjust scores based on job role
    if (jobRole) {
      if (jobRole.toLowerCase().includes('senior') || jobRole.toLowerCase().includes('lead')) {
        experienceScore += 15
        projectsScore += 10
      }
      if (jobRole.toLowerCase().includes('junior') || jobRole.toLowerCase().includes('entry')) {
        experienceScore -= 10
      }
    }
    
    // Calculate overall score
    const overall = (skillsScore + experienceScore + educationScore + projectsScore + softSkillsScore) / 5
    
    return {
      skills: skills.map(skill => ({
        skill: skill,
        score: skill.toLowerCase().includes('javascript') || skill.toLowerCase().includes('react') ? 88 + Math.random() * 10 : 75 + Math.random() * 15,
        relevance: 0.8 + Math.random() * 0.2
      })),
      experience: Math.min(experienceScore, 100),
      education: Math.min(educationScore, 100),
      projects: Math.min(projectsScore, 100),
      soft_skills: Math.min(softSkillsScore, 100),
      overall: Math.min(Math.max(overall, 60), 95) // Ensure score is reasonable
    }
  }
  
  // Get candidate data or use defaults
  const skills = candidateData?.skills || ['JavaScript', 'React', 'TypeScript', 'Node.js']
  const jobRole = candidateData?.job_role || 'Software Developer'
  
  const mockBreakdown: ScoreBreakdown = calculateScore(skills, jobRole)

  return {
    candidate_id: candidateId,
    version: 'enhanced',
    breakdown: mockBreakdown,
    explanation: 'AI analysis identified strong technical skills in JavaScript/React ecosystem with good project experience. Education and soft skills are well-developed. Consider focusing on advanced architecture patterns for senior roles.',
    calculated_at: new Date().toISOString(),
  }
}
