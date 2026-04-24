import apiClient from './api'
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
    const response = await apiClient.get<CandidateListResponse>('/candidates', { params })
    return response.data
  },

  // Get single candidate details
  getCandidate: async (id: string): Promise<CandidateDetail> => {
    const response = await apiClient.get<CandidateDetail>(`/candidates/${id}`)
    return response.data
  },

  // Get candidate status with score
  getCandidateStatus: async (id: string): Promise<CandidateStatusWithScore> => {
    const response = await apiClient.get<CandidateStatusWithScore>(`/candidates/${id}/status`)
    return response.data
  },

  // Upload single candidate
  uploadCandidate: async (data: UploadCandidateRequest): Promise<Candidate> => {
    const formData = new FormData()
    formData.append('name', data.name)
    formData.append('email', data.email)
    formData.append('skills', JSON.stringify(data.skills))
    formData.append('job_role', data.job_role)
    formData.append('resume', data.resume)

    const response = await apiClient.post<Candidate>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Batch upload candidates
  batchUploadCandidates: async (data: BatchUploadRequest): Promise<Candidate[]> => {
    const formData = new FormData()
    formData.append('candidates', JSON.stringify(
      data.candidates.map(c => ({
        name: c.name,
        email: c.email,
        skills: c.skills,
        job_role: c.job_role,
      }))
    ))
    data.candidates.forEach((c, index) => {
      formData.append(`resume_${index}`, c.resume)
    })

    const response = await apiClient.post<Candidate[]>('/upload/batch', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Process candidate (trigger ML)
  processCandidate: async (id: string): Promise<ProcessCandidateResponse> => {
    const response = await apiClient.post<ProcessCandidateResponse>(`/candidates/${id}/process`)
    return response.data
  },

  // Delete candidate
  deleteCandidate: async (id: string): Promise<DeleteCandidateResponse> => {
    const response = await apiClient.delete<DeleteCandidateResponse>(`/candidates/${id}`)
    return response.data
  },

  // Enhance candidate with AI bias correction
  enhanceCandidate: async (id: string): Promise<any> => {
    const response = await apiClient.post(`/candidates/${id}/enhance`)
    return response.data
  },
}
