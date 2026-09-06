import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext()

export function useAuth() {
  return useContext(AuthContext)
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('user')
      return stored ? JSON.parse(stored) : null
    } catch (e) {
      return null
    }
  })
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (token) {
      // Sync user profile in background
      fetch('/api/auth/me?email=admin', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      .then(res => res.json())
      .then(data => {
        if (data && data.name) {
          setUser(prev => ({
            ...prev,
            ...data
          }))
        }
      })
      .catch(() => {
        // Keep existing localStorage user if offline
      })
    }
  }, [token])

  const login = async (email, password) => {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      if (!response.ok) throw new Error('Login failed')

      const data = await response.json()
      
      const fallbackName = email.includes('csr') ? 'CSR Head' : (email.includes('gov') ? 'Admin' : (email.includes('sharma') ? 'Dr. Sharma' : 'Rahul Kumar'))
      const fallbackOrg = data.role === 'Industry' ? { name: 'Tata Steel CSR' } : (data.role === 'University' ? { name: 'RIMS Ranchi' } : { name: 'Jharkhand Health Dept' })

      const userData = {
        id: data.user_id,
        name: data.name || fallbackName,
        email: email,
        role: data.role,
        org_id: data.org_id,
        organization: data.organization || fallbackOrg
      }

      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(userData))
      setToken(data.access_token)
      setUser(userData)
      return userData
    } catch (error) {
      console.error(error)
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setToken(null)
    setUser(null)
  }

  const value = {
    user,
    token,
    login,
    logout,
    loading
  }

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  )
}
