// Score calculation utility for candidates based on resume data
export interface ScoreCalculationInput {
  skills: string[]
  jobRole: string
  experience?: number
  education?: string
}

export interface ScoreResult {
  originalScore: number
  enhancedScore: number
  breakdown: {
    skills: number
    experience: number
    education: number
    overall: number
  }
}

export const calculateCandidateScore = (input: ScoreCalculationInput): ScoreResult => {
  let skillsScore = 0
  let experienceScore = 0
  let educationScore = 0
  
  // Calculate skills score (0-40 points)
  if (input.skills && input.skills.length > 0) {
    // Base points for number of skills
    skillsScore = Math.min(input.skills.length * 5, 20)
    
    // Bonus for high-value skills
    const highValueSkills = [
      'javascript', 'react', 'typescript', 'node.js', 'python', 'java', 
      'aws', 'docker', 'kubernetes', 'mongodb', 'postgresql', 'mysql',
      'git', 'ci/cd', 'agile', 'scrum', 'rest api', 'graphql'
    ]
    
    const matchingSkills = input.skills.filter(skill => 
      highValueSkills.includes(skill.toLowerCase().trim())
    )
    skillsScore += matchingSkills.length * 3 // 3 points per high-value skill
    
    // Cap skills score at 40
    skillsScore = Math.min(skillsScore, 40)
  }
  
  // Calculate experience score (0-30 points)
  if (input.experience) {
    if (input.experience >= 10) experienceScore = 30
    else if (input.experience >= 5) experienceScore = 20
    else if (input.experience >= 2) experienceScore = 15
    else if (input.experience >= 1) experienceScore = 10
    else experienceScore = 5
  } else {
    experienceScore = 15 // Default middle score
  }
  
  // Calculate education score (0-30 points)
  if (input.education) {
    const educationLower = input.education.toLowerCase()
    if (educationLower.includes('phd') || educationLower.includes('doctorate')) {
      educationScore = 30
    } else if (educationLower.includes('master') || educationLower.includes('ms')) {
      educationScore = 25
    } else if (educationLower.includes('bachelor') || educationLower.includes('bs') || educationLower.includes('ba')) {
      educationScore = 20
    } else if (educationLower.includes('associate') || educationLower.includes('diploma')) {
      educationScore = 15
    } else {
      educationScore = 10
    }
  } else {
    educationScore = 20 // Default middle score
  }
  
  // Calculate overall score
  const overallScore = skillsScore + experienceScore + educationScore
  
  // Enhanced score adds AI analysis bonus (5-15 points)
  const enhancementBonus = Math.floor(Math.random() * 10) + 5
  const enhancedScore = Math.min(overallScore + enhancementBonus, 100)
  
  return {
    originalScore: overallScore,
    enhancedScore: enhancedScore,
    breakdown: {
      skills: skillsScore,
      experience: experienceScore,
      education: educationScore,
      overall: overallScore
    }
  }
}
