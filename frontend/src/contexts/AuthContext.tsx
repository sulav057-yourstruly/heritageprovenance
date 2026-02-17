import { createContext, useContext, useEffect, useState } from 'react'
import { LoginResponse, apiClient } from '../lib/api'

type AuthUser = LoginResponse['user'] | null

interface AuthContextValue {
  user: AuthUser
  token: string | null
  login: (email: string, password: string) => Promise<NonNullable<AuthUser>>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

const STORAGE_KEY = 'kathmandu_archive_auth'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser>(null)
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY)
    if (stored) {
      try {
        const parsed = JSON.parse(stored) as { token: string; user: AuthUser }
        setToken(parsed.token)
        setUser(parsed.user)
        apiClient.setToken(parsed.token)
      } catch {
        window.localStorage.removeItem(STORAGE_KEY)
      }
    }
  }, [])

  const login = async (email: string, password: string) => {
    const res = await apiClient.login(email, password)
    setUser(res.user)
    setToken(res.access_token)
    apiClient.setToken(res.access_token)
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ token: res.access_token, user: res.user }),
    )
    return res.user
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    apiClient.setToken(null)
    window.localStorage.removeItem(STORAGE_KEY)
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

