import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { authApi } from '../services/resources'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setLoading(false)
      return
    }
    try {
      const res = await authApi.me()
      setUser(res.data)
    } catch {
      localStorage.removeItem('access_token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadUser()
  }, [loadUser])

  const login = async (email, password) => {
    const res = await authApi.login(email, password)
    localStorage.setItem('access_token', res.data.access_token)
    const me = await authApi.me()
    setUser(me.data)
    return me.data
  }

  const register = async (data) => {
    const res = await authApi.register(data)
    localStorage.setItem('access_token', res.data.access_token)
    const me = await authApi.me()
    setUser(me.data)
    return me.data
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    setUser(null)
    window.location.href = '/login'
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
