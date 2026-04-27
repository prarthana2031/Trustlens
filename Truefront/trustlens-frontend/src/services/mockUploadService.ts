// Mock upload service for development when backend is not available
import { Candidate, UploadCandidateRequest, BatchUploadRequest } from '../types/candidate'

// Generate mock candidate ID
const generateCandidateId = () => {
  const timestamp = Date.now()
  const random = Math.random().toString(36).substr(2, 9)
  return `cand_${timestamp}_${random}`
}

// Mock upload response
const createMockCandidate = (data: UploadCandidateRequest): Candidate => {
  const id = generateCandidateId()
  const now = new Date().toISOString()
  
  return {
    id,
    name: data.name,
    email: data.email,
    skills: data.skills,
    job_role: data.job_role,
    status: 'pending',
    resume_path: `resumes/${id}_${data.resume.name}`,
    created_at: now,
    updated_at: now,
  }
}

// Mock batch upload response
const createMockBatchCandidates = (data: BatchUploadRequest): Candidate[] => {
  return data.candidates.map(candidate => 
    createMockCandidate({
      name: candidate.name,
      email: candidate.email,
      skills: candidate.skills,
      job_role: candidate.job_role,
      resume: candidate.resume,
    })
  )
}

// Simulate upload delay
const simulateUploadDelay = (ms: number = 2000) => {
  return new Promise(resolve => setTimeout(resolve, ms))
}

export const mockUploadService = {
  // Mock single upload
  uploadCandidate: async (data: UploadCandidateRequest): Promise<Candidate> => {
    console.log('[Mock Upload] Starting single upload:', {
      name: data.name,
      email: data.email,
      fileName: data.resume.name,
      fileSize: data.resume.size,
    })

    // Simulate upload processing time
    await simulateUploadDelay(1500 + Math.random() * 2000)

    const mockCandidate = createMockCandidate(data)
    
    console.log('[Mock Upload] Single upload completed:', mockCandidate)
    return mockCandidate
  },

  // Mock batch upload
  batchUploadCandidates: async (data: BatchUploadRequest): Promise<Candidate[]> => {
    console.log('[Mock Upload] Starting batch upload:', {
      count: data.candidates.length,
      files: data.candidates.map(c => ({ name: c.resume.name, size: c.resume.size })),
    })

    // Simulate batch upload processing time (longer for multiple files)
    await simulateUploadDelay(3000 + (data.candidates.length * 1000) + Math.random() * 3000)

    const mockCandidates = createMockBatchCandidates(data)
    
    console.log('[Mock Upload] Batch upload completed:', {
      count: mockCandidates.length,
      candidates: mockCandidates.map(c => ({ id: c.id, name: c.name })),
    })
    
    return mockCandidates
  },
}

// Helper function to check if backend is available
export const isBackendAvailable = async (): Promise<boolean> => {
  try {
    // Try to ping the backend upload endpoint through the Vite proxy
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5000)
    
    const response = await fetch('/api/upload', {
      method: 'HEAD', // Use HEAD to check if endpoint exists without uploading
      signal: controller.signal
    })
    
    clearTimeout(timeoutId)
    return response.ok || response.status === 405 // 405 Method Not Allowed means endpoint exists
  } catch (error) {
    console.debug('[Backend] Upload endpoint not available')
    return false
  }
}
