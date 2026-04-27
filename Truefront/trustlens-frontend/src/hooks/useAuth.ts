import { useState, useEffect } from 'react'
import { User } from 'firebase/auth'
import { onAuthChange, signOut } from '../services/firebaseConfig'

// Mock user for development
const mockUser = {
  uid: 'mock-user-id',
  email: 'demo@trustlens.com',
  displayName: 'Demo User',
  photoURL: null,
  emailVerified: true,
  isAnonymous: false,
  providerData: [],
  phoneNumber: null,
  providerId: null
} as unknown as User

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // For development, use mock user if Firebase is not configured
    if (!import.meta.env.VITE_FIREBASE_API_KEY) {
      console.log('[Auth] Using mock user for development')
      setUser(mockUser)
      setLoading(false)
      return
    }

    const unsubscribe = onAuthChange((user) => {
      setUser(user)
      setLoading(false)
    })

    return () => unsubscribe()
  }, [])

  const logout = async () => {
    if (!import.meta.env.VITE_FIREBASE_API_KEY) {
      setUser(null)
      return
    }
    await signOut()
    setUser(null)
  }

  return { user, loading, logout }
}
