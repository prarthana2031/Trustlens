import { BiasMetric, BiasSeverity } from '../../types/bias'
import { cn } from '../../utils/cn'

interface BiasMetricsCardProps {
  metrics: BiasMetric[]
  overallFairnessScore: number
}

export function BiasMetricsCard({ metrics, overallFairnessScore }: BiasMetricsCardProps) {
  const getSeverityColor = (severity: BiasSeverity) => {
    switch (severity) {
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200'
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Bias Metrics</h3>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">Overall Fairness Score:</span>
          <span className={cn('text-2xl font-bold', getScoreColor(overallFairnessScore))}>
            {overallFairnessScore.toFixed(1)}
          </span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Category</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Indicator</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Value</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Threshold</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Severity</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((metric, index) => (
              <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="py-3 px-4 text-sm text-gray-900">{metric.category}</td>
                <td className="py-3 px-4 text-sm text-gray-600">{metric.indicator}</td>
                <td className="py-3 px-4 text-sm text-gray-900 font-medium">{metric.value.toFixed(2)}</td>
                <td className="py-3 px-4 text-sm text-gray-600">{metric.threshold.toFixed(2)}</td>
                <td className="py-3 px-4">
                  <span
                    className={cn(
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
                      getSeverityColor(metric.severity)
                    )}
                  >
                    {metric.severity}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {metrics.length === 0 && (
        <div className="text-center py-8 text-gray-500">No bias metrics available</div>
      )}
    </div>
  )
}
