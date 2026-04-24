import React from 'react'
import { CandidateList } from '../components/candidates/CandidateList'
import { useCandidates } from '../hooks/useCandidates'
import { LoadingSpinner } from '../components/common/LoadingSpinner'

const CandidatesPage: React.FC = () => {
  const { data, isLoading, refetch } = useCandidates()

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Candidates</h1>
      {isLoading ? (
        <LoadingSpinner size="lg" />
      ) : (
        <CandidateList
          candidates={data?.candidates || []}
          isLoading={isLoading}
          onRefresh={() => refetch()}
        />
      )}
    </div>
  )
}

export default CandidatesPage
