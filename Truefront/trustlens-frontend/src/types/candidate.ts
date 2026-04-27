export type CandidateStatus = 'pending' | 'processing' | 'completed' | 'error' | 'recommended' | 'under_review'

export interface Candidate {
  id?: string
  candidate_id?: string
  name: string
  email: string
  skills: string[]
  job_role: string
  status: CandidateStatus
  created_at?: string
  updated_at?: string
  resume_path?: string
  application_id?: string
  file_id?: string
  filename?: string
  size_bytes?: number
  storage_url?: string
  uploaded_at?: string
}

export interface CandidateListResponse {
  candidates: Candidate[]
  total: number
  skip: number
  limit: number
}

export interface CandidateDetail extends Candidate {
  experience_years?: number
  education_level?: string
  projects_count?: number
  soft_skills?: string[]
}

export interface UploadCandidateRequest {
  name: string
  email: string
  skills: string[]
  job_role: string
  resume: File
}

export interface BatchUploadRequest {
  candidates: {
    name: string
    email: string
    skills: string[]
    job_role: string
    resume: File
  }[]
}

export interface ProcessCandidateResponse {
  message: string
  candidate_id: string
}

export interface DeleteCandidateResponse {
  message: string
}
