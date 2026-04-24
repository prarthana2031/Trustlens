import React from 'react'
import { useAuthStore } from '../../store/authStore'
import { useNavigate } from 'react-router-dom'

export const Header: React.FC = () => {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-bold text-gray-900">TrustLens</h1>
        </div>
        <div className="flex items-center space-x-4">
          {user && (
            <>
              <span className="text-sm text-gray-600">{user.email}</span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
              >
                Logout
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
