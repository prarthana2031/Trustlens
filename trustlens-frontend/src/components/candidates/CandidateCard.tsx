import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Candidate } from '../../types/candidate'
import { CandidateStatusBadge } from '../common/CandidateStatusBadge'
import { getInitials } from '../../utils/formatting'

interface CandidateCardProps {
  candidate: Candidate
}

export const CandidateCard: React.FC<CandidateCardProps> = ({ candidate }) => {
  const navigate = useNavigate()

  return (
    <div
      className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
      onClick={() => navigate(`/candidate/${candidate.id}`)}
    >
      <div className="flex items-start space-x-4">
        <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-semibold">
          {getInitials(candidate.name)}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-medium text-gray-900 truncate">{candidate.name}</h3>
          <p className="text-xs text-gray-500 truncate">{candidate.email}</p>
          <p className="text-xs text-gray-400 mt-1">{candidate.job_role}</p>
        </div>
        <CandidateStatusBadge status={candidate.status} />
      </div>
      <div className="mt-3 flex items-center justify-between">
        <div className="text-xs text-gray-500">
          {candidate.skills.length} skill{candidate.skills.length !== 1 ? 's' : ''}
        </div>
        <div className="text-xs text-gray-400">
          {new Date(candidate.created_at).toLocaleDateString()}
        </div>
      </div>
    </div>
  )
}
