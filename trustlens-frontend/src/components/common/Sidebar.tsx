import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useUIStore } from '../../store/uiStore'

export const Sidebar: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { sidebarOpen } = useUIStore()

  const menuItems = [
    { path: '/', label: 'Dashboard' },
    { path: '/upload', label: 'Upload' },
    { path: '/candidates', label: 'Candidates' },
    { path: '/screening', label: 'Screening' },
    { path: '/bias-analysis', label: 'Bias Analysis' },
    { path: '/reports', label: 'Reports' },
  ]

  if (!sidebarOpen) return null

  return (
    <aside className="w-64 bg-gray-50 border-r border-gray-200 min-h-screen">
      <nav className="p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => (
            <li key={item.path}>
              <button
                onClick={() => navigate(item.path)}
                className={`w-full text-left px-4 py-2 rounded-md text-sm ${
                  location.pathname === item.path
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                {item.label}
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  )
}
