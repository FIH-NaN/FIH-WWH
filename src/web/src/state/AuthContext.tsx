import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import * as authService from '../services/authService'
import type { User } from '../types/models'

type AuthContextValue = {
  user: User | null
  token: string | null
  isBootstrapping: boolean
  login: (email: string, password: string) => Promise<void>
  register: (name: string, email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

const TOKEN_KEY = 'wwh_token'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState<User | null>(null)
  const [isBootstrapping, setIsBootstrapping] = useState(true)

  useEffect(() => {
    const bootstrap = async () => {
      if (!token) {
        setIsBootstrapping(false)
        return
      }

      try {
        const response = await authService.me(token)
        setUser(response.data)
      } catch {
        localStorage.removeItem(TOKEN_KEY)
        setToken(null)
        setUser(null)
      } finally {
        setIsBootstrapping(false)
      }
    }

    void bootstrap()
  }, [token])

  const value = useMemo<AuthContextValue>(() => ({
    user,
    token,
    isBootstrapping,
    login: async (email: string, password: string) => {
      const response = await authService.login(email, password)
      setToken(response.data.token)
      setUser(response.data.user)
      localStorage.setItem(TOKEN_KEY, response.data.token)
    },
    register: async (name: string, email: string, password: string) => {
      const response = await authService.register(name, email, password)
      setToken(response.data.token)
      setUser(response.data.user)
      localStorage.setItem(TOKEN_KEY, response.data.token)
    },
    logout: () => {
      localStorage.removeItem(TOKEN_KEY)
      setToken(null)
      setUser(null)
    },
  }), [isBootstrapping, token, user])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
