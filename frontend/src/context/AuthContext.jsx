import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext()

export function useAuth() {
  return useContext(AuthContext)
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      // Fetch user profile
      fetch('http://localhost:8000/api/auth/me?email=admin', { // For MVP, normally token decodes or backend infers
        headers: { 'Authorization': `Bearer ${token}` }
      })
      .then(res => {
          // As a shortcut for MVP, since we mocked the auth, we'll store user data directly in localStorage
          const storedUser = localStorage.getItem('user')
          if (storedUser) setUser(JSON.parse(storedUser))
      })
      .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [token])

  const login = async (email, password) => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      if (!response.ok) throw new Error('Login failed')

      const data = await response.json()
      
      const userData = {
        id: data.user_id,
        email: email,
        role: data.role,
        org_id: data.org_id
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
