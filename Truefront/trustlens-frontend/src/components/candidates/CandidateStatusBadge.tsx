import { CandidateStatus } from '../../types/candidate'
import { cn } from '../../utils/cn'

interface CandidateStatusBadgeProps {
  status: CandidateStatus
  className?: string
}

export function CandidateStatusBadge({ status, className }: CandidateStatusBadgeProps) {
  const statusConfig = {
    pending: {
      label: 'Pending',
      bgColor: 'bg-gray-100',
      textColor: 'text-gray-800',
      dotColor: 'bg-gray-400',
    },
    processing: {
      label: 'Processing',
      bgColor: 'bg-blue-100',
      textColor: 'text-blue-800',
      dotColor: 'bg-blue-400',
    },
    completed: {
      label: 'Completed',
      bgColor: 'bg-green-100',
      textColor: 'text-green-800',
      dotColor: 'bg-green-400',
    },
    error: {
      label: 'Error',
      bgColor: 'bg-red-100',
      textColor: 'text-red-800',
      dotColor: 'bg-red-400',
    },
    recommended: {
      label: 'Recommended',
      bgColor: 'bg-purple-100',
      textColor: 'text-purple-800',
      dotColor: 'bg-purple-400',
    },
    under_review: {
      label: 'Under Review',
      bgColor: 'bg-yellow-100',
      textColor: 'text-yellow-800',
      dotColor: 'bg-yellow-400',
    },
  }

  const config = statusConfig[status]

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium',
        config.bgColor,
        config.textColor,
        className
      )}
    >
      <span className={cn('h-2 w-2 rounded-full', config.dotColor)} />
      {config.label}
    </span>
  )
}
