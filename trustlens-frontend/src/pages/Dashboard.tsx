import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCandidates, useDeleteCandidate } from '../hooks/useCandidates'
import { CandidateStatusBadge } from '../components/common/CandidateStatusBadge'
import { Skeleton } from '../components/common/Skeleton'
import { Header } from '../components/common/Header'
import { EmptyState } from '../components/common/EmptyState'
import { useDebounce } from '../utils/debounce'
import { FilterParams } from '../types/api'
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts'

const STATUS_COLORS: Record<string, string> = {
  completed: '#10b981',
  processing: '#3b82f6',
  pending: '#6b7280',
  error: '#ef4444',
}

export default function Dashboard() {
  const navigate = useNavigate()
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [searchInput, setSearchInput] = useState('')
  const debouncedSearch = useDebounce(searchInput, 300)
  const deleteCandidate = useDeleteCandidate()

  const params: FilterParams = {
    status: statusFilter || undefined,
    search: debouncedSearch || undefined,
    skip: 0,
    limit: 50,
  }

  const { data, isLoading, error } = useCandidates(params)

  const filteredCandidates = data?.candidates || []

  // Status distribution for pie chart
  const statusCounts = filteredCandidates.reduce((acc, c) => {
    acc[c.status] = (acc[c.status] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const statusPieData = Object.entries(statusCounts).map(([status, count]) => ({
    name: status.charAt(0).toUpperCase() + status.slice(1),
    value: count,
  }))

  // Job role distribution for bar chart
  const roleCounts = filteredCandidates.reduce((acc, c) => {
    acc[c.job_role] = (acc[c.job_role] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const roleBarData = Object.entries(roleCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)
    .map(([role, count]) => ({
      name: role.length > 15 ? role.slice(0, 15) + '...' : role,
      count,
    }))

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this candidate?')) {
      await deleteCandidate.mutateAsync(id)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-4 py-3">
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium">
              Dashboard
            </button>
            <button
              onClick={() => navigate('/upload')}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg text-sm font-medium transition-colors"
            >
              Upload
            </button>
            <button
              onClick={() => navigate('/screening')}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg text-sm font-medium transition-colors"
            >
              Screening
            </button>
            <button
              onClick={() => navigate('/bias-analysis')}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg text-sm font-medium transition-colors"
            >
              Bias Analysis
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search candidates..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div className="sm:w-48">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Status</option>
                <option value="pending">Pending</option>
                <option value="processing">Processing</option>
                <option value="completed">Completed</option>
                <option value="error">Error</option>
              </select>
            </div>
            <button
              onClick={() => navigate('/upload')}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Upload Candidate
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <p className="text-sm text-gray-600">Total Candidates</p>
            <p className="text-2xl font-bold text-gray-900">{data?.total || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <p className="text-sm text-gray-600">Completed</p>
            <p className="text-2xl font-bold text-green-600">
              {filteredCandidates.filter(c => c.status === 'completed').length}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <p className="text-sm text-gray-600">Processing</p>
            <p className="text-2xl font-bold text-blue-600">
              {filteredCandidates.filter(c => c.status === 'processing').length}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <p className="text-sm text-gray-600">Pending</p>
            <p className="text-2xl font-bold text-gray-600">
              {filteredCandidates.filter(c => c.status === 'pending').length}
            </p>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Status Distribution */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Status Distribution</h3>
            {statusPieData.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={statusPieData}
                    cx="50%"
                    cy="50%"
                    outerRadius={70}
                    dataKey="value"
                    label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                    labelLine={{ stroke: '#9ca3af' }}
                  >
                    {statusPieData.map((entry, index) => (
                      <Cell
                        key={index}
                        fill={STATUS_COLORS[entry.name.toLowerCase()] || '#6b7280'}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-500 text-center py-8">No data available</p>
            )}
          </div>

          {/* Job Role Distribution */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Candidates by Role</h3>
            {roleBarData.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={roleBarData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={24} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-500 text-center py-8">No data available</p>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
          <button
            onClick={() => navigate('/upload')}
            className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-4 text-left hover:from-blue-600 hover:to-blue-700 transition-all"
          >
            <p className="text-white font-semibold">Upload Resumes</p>
            <p className="text-blue-100 text-sm">Add new candidates to the pipeline</p>
          </button>
          <button
            onClick={() => navigate('/screening')}
            className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-4 text-left hover:from-purple-600 hover:to-purple-700 transition-all"
          >
            <p className="text-white font-semibold">Start Screening</p>
            <p className="text-purple-100 text-sm">Screen candidates with fairness checks</p>
          </button>
          <button
            onClick={() => navigate('/bias-analysis')}
            className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-4 text-left hover:from-green-600 hover:to-green-700 transition-all"
          >
            <p className="text-white font-semibold">Analyze Bias</p>
            <p className="text-green-100 text-sm">Review demographic disparities</p>
          </button>
        </div>

        {/* Candidates Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {isLoading ? (
            <div className="p-8 space-y-4">
              {[...Array(5)].map((_, i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          ) : error ? (
            <EmptyState
              title="Failed to Load Candidates"
              description="We encountered an error while loading candidates. Please try again."
              action={{
                label: 'Retry',
                onClick: () => window.location.reload(),
              }}
            />
          ) : filteredCandidates.length === 0 ? (
            <EmptyState
              title="No Candidates Yet"
              description="Upload your first resume to get started with the fair hiring process."
              action={{
                label: 'Upload Candidate',
                onClick: () => navigate('/upload'),
              }}
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Name</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Email</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Job Role</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Skills</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Status</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredCandidates.map((candidate) => (
                    <tr key={candidate.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4 text-sm font-medium text-gray-900">
                        {candidate.name}
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">{candidate.email}</td>
                      <td className="py-3 px-4 text-sm text-gray-600">{candidate.job_role}</td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        <div className="flex flex-wrap gap-1">
                          {candidate.skills.slice(0, 3).map((skill, i) => (
                            <span
                              key={i}
                              className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded text-xs"
                            >
                              {skill}
                            </span>
                          ))}
                          {candidate.skills.length > 3 && (
                            <span className="text-xs text-gray-500">
                              +{candidate.skills.length - 3}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <CandidateStatusBadge status={candidate.status} />
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex gap-2">
                          <button
                            onClick={() => navigate(`/candidate/${candidate.id}`)}
                            className="px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded transition-colors"
                          >
                            View
                          </button>
                          <button
                            onClick={() => handleDelete(candidate.id)}
                            className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded transition-colors"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
