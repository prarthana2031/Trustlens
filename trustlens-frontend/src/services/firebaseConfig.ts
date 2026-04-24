import { initializeApp, getApps, FirebaseApp } from 'firebase/app'
import { 
  getAuth, 
  signInWithEmailAndPassword, 
  signInWithPopup, 
  GoogleAuthProvider,
  createUserWithEmailAndPassword,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  User,
  Auth
} from 'firebase/auth'

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
}

// Initialize Firebase
let app: FirebaseApp
if (!getApps().length) {
  app = initializeApp(firebaseConfig)
} else {
  app = getApps()[0]
}

export const auth: Auth = getAuth(app)
export const googleProvider = new GoogleAuthProvider()

// Auth functions
export const signInWithEmail = async (email: string, password: string) => {
  const result = await signInWithEmailAndPassword(auth, email, password)
  const token = await result.user.getIdToken()
  const refreshToken = result.user.refreshToken
  localStorage.setItem('firebase_token', token)
  localStorage.setItem('firebase_refresh_token', refreshToken)
  return result.user
}

export const signUpWithEmail = async (email: string, password: string) => {
  const result = await createUserWithEmailAndPassword(auth, email, password)
  const token = await result.user.getIdToken()
  const refreshToken = result.user.refreshToken
  localStorage.setItem('firebase_token', token)
  localStorage.setItem('firebase_refresh_token', refreshToken)
  return result.user
}

export const signInWithGoogle = async () => {
  const result = await signInWithPopup(auth, googleProvider)
  const token = await result.user.getIdToken()
  const refreshToken = result.user.refreshToken
  localStorage.setItem('firebase_token', token)
  localStorage.setItem('firebase_refresh_token', refreshToken)
  return result.user
}

export const signOut = async () => {
  await firebaseSignOut(auth)
  localStorage.removeItem('firebase_token')
  localStorage.removeItem('firebase_refresh_token')
}

export const onAuthChange = (callback: (user: User | null) => void) => {
  return onAuthStateChanged(auth, callback)
}

export default app
