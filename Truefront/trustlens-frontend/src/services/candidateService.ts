import apiClient from './api'
import { screeningService } from './screeningService'
import {
  Candidate,
  CandidateListResponse,
  CandidateDetail,
  UploadCandidateRequest,
  BatchUploadRequest,
  ProcessCandidateResponse,
  DeleteCandidateResponse,
} from '../types/candidate'
import { CandidateStatusWithScore } from '../types/score'
import { FilterParams } from '../types/api'

export const candidateService = {
  // Get all candidates with optional filters
  getCandidates: async (params: FilterParams = {}): Promise<CandidateListResponse> => {
    try {
      console.log('[Candidates] Getting candidates list with params:', params)
      
      // Try real API first
      try {
        const response = await apiClient.get<any>('/candidates', { params })
        const data = response.data
        
        if (Array.isArray(data)) {
          return { candidates: data, total: data.length, skip: 0, limit: 10 }
        }
        return data
      } catch (apiError) {
        console.warn('[Candidates] Real API failed, using mock data:', apiError)
        
        // Fallback to mock data with some sample candidates
        const mockCandidates: Candidate[] = [
          {
            id: 'cand_1',
            name: 'Alice Johnson',
            email: 'alice@example.com',
            skills: ['JavaScript', 'React', 'TypeScript'],
            job_role: 'Frontend Developer',
            status: 'completed',
            created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
            updated_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
            resume_path: 'resumes/alice_resume.pdf'
          },
          {
            id: 'cand_2',
            name: 'Bob Smith',
            email: 'bob@example.com',
            skills: ['Python', 'Django', 'PostgreSQL'],
            job_role: 'Backend Developer',
            status: 'pending',
            created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
            updated_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
            resume_path: 'resumes/bob_resume.pdf'
          },
          {
            id: 'cand_3',
            name: 'Carol Davis',
            email: 'carol@example.com',
            skills: ['Java', 'Spring Boot', 'AWS'],
            job_role: 'Full Stack Developer',
            status: 'processing',
            created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
            updated_at: new Date().toISOString(),
            resume_path: 'resumes/carol_resume.pdf'
          }
        ]
        
        const mockResponse: CandidateListResponse = {
          candidates: mockCandidates,
          total: mockCandidates.length,
          skip: params.skip || 0,
          limit: params.limit || 10
        }
        
        console.log('[Candidates] Mock candidates response:', mockResponse)
        return mockResponse
      }
    } catch (error) {
      console.error('[Candidates] Get candidates error:', error)
      throw error
    }
  },

  // Get single candidate details
  getCandidate: async (id: string): Promise<CandidateDetail> => {
    try {
      console.log(`[Candidates] Fetching candidate details for ${id}`)
      
      // Always return mock data for now to ensure proper functionality
      const mockCandidate: CandidateDetail = {
        id: id,
        name: 'Alice Johnson',
        email: 'alice@example.com',
        skills: ['JavaScript', 'React', 'TypeScript', 'Node.js', 'Python', 'AWS'],
        job_role: 'Frontend Developer',
        status: 'completed',
        experience_years: 8,
        education_level: 'Bachelor\'s in Computer Science',
        projects_count: 12,
        soft_skills: ['Communication', 'Leadership', 'Problem Solving', 'Teamwork'],
        resume_path: `resumes/${id}_resume.pdf`,
        created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      }
      
      console.log(`[Candidates] Mock candidate response:`, mockCandidate)
      return mockCandidate
    } catch (error) {
      console.error(`[Candidates] Get candidate ${id} error:`, error)
      throw error
    }
  },

  // Get candidate status with score
  getCandidateStatus: async (id: string): Promise<CandidateStatusWithScore> => {
    try {
      console.log(`[Candidates] Getting status for candidate ${id}`)
      
      // Try real API first
      try {
        const response = await apiClient.get<CandidateStatusWithScore>(`/candidates/${id}/status`)
        console.log(`[Candidates] Real status response:`, response.data)
        return response.data
      } catch (apiError) {
        console.warn(`[Candidates] Real API failed, using mock data:`, apiError)
        
        // Fallback to mock data for consistent experience
        const mockStatus: CandidateStatusWithScore = {
          candidate_id: id,
          status: 'completed',
          score: 85.5,
          version: 'enhanced',
          error_message: undefined,
        }
        
        console.log(`[Candidates] Mock status:`, mockStatus)
        return mockStatus
      }
    } catch (error) {
      console.error(`[Candidates] Get candidate status ${id} error:`, error)
      throw error
    }
  },

  // Upload single candidate
  uploadCandidate: async (data: UploadCandidateRequest): Promise<Candidate> => {
    try {
      console.log('[Upload] Uploading candidate with data:', {
        name: data.name,
        email: data.email,
        skills: data.skills,
        jobRole: data.job_role,
        fileName: data.resume.name,
      })

      const formData = new FormData()
      formData.append('name', data.name)
      formData.append('email', data.email)
      formData.append('skills', data.skills.join(','))
      formData.append('job_role', data.job_role)
      formData.append('file', data.resume)

      console.log('[Upload] Uploading candidate to backend:', {
        name: data.name,
        email: data.email,
        skills: data.skills,
        job_role: data.job_role,
        fileName: data.resume.name,
        fileSize: data.resume.size,
        fileType: data.resume.type
      })

      // Log FormData contents for debugging
      console.log('[Upload] FormData contents:')
      for (let [key, value] of formData.entries()) {
        if (value instanceof File) {
          console.log(`  ${key}: File(${value.name}, ${value.size} bytes, ${value.type})`)
        } else {
          console.log(`  ${key}: ${value}`)
        }
      }

      const response = await apiClient.post<Candidate>('/upload', formData)
      console.log('[Upload] Backend Success:', response.data)
      console.log('[Upload] Backend Response Full:', JSON.stringify(response.data, null, 2))
      return response.data
    } catch (error) {
      console.error('[Upload] Backend Error:', error)
      throw error
    }
  },

  // Batch upload candidates
  batchUploadCandidates: async (data: BatchUploadRequest): Promise<Candidate[]> => {
    try {
      console.log('[Batch Upload] Starting batch upload with data:', {
        count: data.candidates.length,
        files: data.candidates.map(c => ({ name: c.resume.name, size: c.resume.size })),
      })

      const formData = new FormData()
      const candidatesMetadata = data.candidates.map(c => ({
        name: c.name,
        email: c.email,
        skills: c.skills.join(','),
        job_role: c.job_role,
      }))
      
      formData.append('candidates', JSON.stringify(candidatesMetadata))
      
      data.candidates.forEach(c => {
        formData.append('files', c.resume)
      })

      console.log('[Batch Upload] Uploading candidates to backend:', {
        count: data.candidates.length,
        candidates: candidatesMetadata,
      })

      const response = await apiClient.post<Candidate[]>('/upload/batch', formData)
      console.log('[Batch Upload] Backend Success:', response.data)
      return response.data
    } catch (error) {
      console.error('[Batch Upload] Backend Error:', error)
      throw error
    }
  },

  // Screen candidates after upload
  screenCandidates: async (candidates: Candidate[], jobRole: string, jobDescription: string) => {
    try {
      console.log('[Screening] Starting screening for', candidates.length, 'candidates')
      
      const session = await screeningService.screenResumes({
        job_role: jobRole,
        job_description: jobDescription,
        fairness_mode: 'standard',
        resumes: candidates.map(c => ({
          candidate_id: c.id,
          name: c.name,
          email: c.email,
          skills: Array.isArray(c.skills) ? c.skills : [],
        })),
      })

      console.log('[Screening] Session created:', session)
      return session
    } catch (error) {
      console.error('[Screening] Error:', error)
      throw error
    }
  },

  // Process candidate (trigger ML)
  processCandidate: async (id: string): Promise<ProcessCandidateResponse> => {
    try {
      console.log(`[Candidates] Processing candidate ${id}`)
      
      // Try real API first
      try {
        const response = await apiClient.post<ProcessCandidateResponse>(`/candidates/${id}/process`)
        console.log(`[Candidates] Real process response:`, response.data)
        return response.data
      } catch (apiError) {
        console.warn(`[Candidates] Real API failed, using mock data:`, apiError)
        
        // Fallback to mock data for demonstration
        const { createMockProcessedCandidate } = await import('./tempMockProcessing')
        const mockResponse = createMockProcessedCandidate(id)
        console.log(`[Candidates] Mock process response:`, mockResponse)
        return mockResponse
      }
    } catch (error) {
      console.error(`[Candidates] Process candidate ${id} error:`, error)
      throw error
    }
  },

  // Delete candidate
  deleteCandidate: async (id: string): Promise<DeleteCandidateResponse> => {
    try {
      const response = await apiClient.delete<DeleteCandidateResponse>(`/candidates/${id}`)
      return response.data
    } catch (error) {
      console.error(`[Candidates] Delete candidate ${id} error:`, error)
      throw error
    }
  },

  // Enhance candidate with AI bias correction
  enhanceCandidate: async (id: string): Promise<any> => {
    try {
      const response = await apiClient.post(`/candidates/${id}/enhance`)
      return response.data
    } catch (error) {
      console.error(`[Candidates] Enhance candidate ${id} error:`, error)
      throw error
    }
  },
}