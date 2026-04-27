import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { getAuthToken } from './firebaseConfig'

// Use environment variable or default to deployed backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://resume-backend-948277799081.us-central1.run.app'

console.log('[API] === CONFIG v3.0 ===')
console.log('[API] Environment:', import.meta.env.MODE)
console.log('[API] Base URL:', `${API_BASE_URL}/api/v1`)
console.log('[API] Timestamp:', new Date().toISOString())

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 second timeout
  withCredentials: false, // Don't send credentials for CORS
})

// Add request interceptor to handle preflight requests
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // For file uploads, don't set Content-Type - let browser set it with boundary
    if (config.data instanceof FormData && config.headers) {
      delete config.headers['Content-Type']
    }

    const token = await getAuthToken()
    if (token) {
      config.headers = config.headers ?? {}
      config.headers.Authorization = `Bearer ${token}`
    }
    console.debug(`[API] ${config.method?.toUpperCase()} ${config.url}`, { baseURL: API_BASE_URL })
    return config
  },
  (error: AxiosError) => {
    console.error('[API] Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.debug(`[API] Response: ${response.status}`, response.config.url)
    return response
  },
  async (error: AxiosError) => {
    const responseData = error.response?.data as any
    const errorMessage = responseData?.detail || error.message || 'Unknown error'
    const isError = error.response?.status && error.response.status >= 500
    const logMessage = '[API] Response error:'
    const logData = {
      status: error.response?.status,
      url: error.config?.url,
      message: errorMessage,
    }
    if (isError) {
      console.error(logMessage, logData)
    } else {
      console.debug(logMessage, logData)
    }

    if (error.response?.status === 401) {
      // Token expired, try to refresh
      const refreshToken = localStorage.getItem('firebase_refresh_token')
      if (refreshToken) {
        try {
          // In a real app, you'd call Firebase to refresh the token
          // For now, we'll just clear the tokens and redirect to login
          localStorage.removeItem('firebase_token')
          localStorage.removeItem('firebase_refresh_token')
          window.location.href = '/login'
        } catch (refreshError) {
          localStorage.removeItem('firebase_token')
          localStorage.removeItem('firebase_refresh_token')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient
