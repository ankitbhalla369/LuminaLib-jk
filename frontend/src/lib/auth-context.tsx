'use client'

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { api, type User } from './api'

type AuthState = { user: User | null; loading: boolean }

const AuthContext = createContext<AuthState & { login: (email: string, password: string) => Promise<void>; signup: (email: string, password: string, fullName?: string) => Promise<void>; logout: () => void; refresh: () => Promise<void> } | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }
    try {
      const u = await api.auth.me()
      setUser(u)
    } catch {
      localStorage.removeItem('token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const login = useCallback(async (email: string, password: string) => {
    const { access_token } = await api.auth.login(email, password)
    localStorage.setItem('token', access_token)
    await refresh()
  }, [refresh])

  const signup = useCallback(async (email: string, password: string, fullName?: string) => {
    await api.auth.signup(email, password, fullName)
    await login(email, password)
  }, [login])

  const logout = useCallback(() => {
    localStorage.removeItem('token')
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
