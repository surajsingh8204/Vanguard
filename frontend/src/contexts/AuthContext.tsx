import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react'
import { getMe, login as loginRequest, register as registerRequest, type User } from '@/api/auth'

type AuthContextValue = {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (payload: {
    username: string
    email: string
    password: string
  }) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setLoading(false)
      return
    }

    getMe()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem('access_token')
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const result = await loginRequest(email, password)
    localStorage.setItem('access_token', result.access_token)
    setUser(result.user)
  }, [])

  const register = useCallback(
    async (payload: { username: string; email: string; password: string }) => {
      await registerRequest(payload)
      await login(payload.email, payload.password)
    },
    [login],
  )

  const logout = useCallback(() => {
    localStorage.removeItem('access_token')
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, loading, login, register, logout }),
    [user, loading, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
