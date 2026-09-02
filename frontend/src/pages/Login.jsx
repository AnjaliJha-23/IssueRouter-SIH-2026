import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { ShieldAlert, User, Building, Factory } from 'lucide-react'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e?.preventDefault()
    setError('')
    try {
      const user = await login(email, password || 'dummyhash')
      // Route based on role
      if (user.role === 'Gov') navigate('/dashboard/gov')
      else if (user.role === 'University' || user.role === 'Industry') navigate('/dashboard/org')
      else navigate('/dashboard/citizen')
    } catch (err) {
      setError('Failed to login. Please check credentials.')
    }
  }

  const seedLogin = (seedEmail) => {
    setEmail(seedEmail)
    setPassword('dummyhash')
    // A small delay to let state update before submitting, though our handleLogin uses state directly.
    // We'll just call login directly here.
    login(seedEmail, 'dummyhash').then((user) => {
      if (user.role === 'Gov') navigate('/dashboard/gov')
      else if (user.role === 'University' || user.role === 'Industry') navigate('/dashboard/org')
      else navigate('/dashboard/citizen')
    }).catch(() => setError('Failed to login'))
  }

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-neutral-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-neutral-900 dark:text-white">
          Societal Innovation Portal
        </h2>
        <p className="mt-2 text-center text-sm text-neutral-600 dark:text-neutral-400">
          SIH 2026 Demo Login
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white dark:bg-neutral-800 py-8 px-4 shadow sm:rounded-lg sm:px-10">
          
          <div className="mb-6">
            <h3 className="text-lg font-medium text-neutral-900 dark:text-white mb-4">Quick Demo Login</h3>
            <div className="grid grid-cols-2 gap-3">
              <button onClick={() => seedLogin('gov@jharkhand.gov.in')} className="flex items-center justify-center p-3 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
                <ShieldAlert className="w-4 h-4 mr-2" /> Gov Admin
              </button>
              <button onClick={() => seedLogin('sharma@rims.ac.in')} className="flex items-center justify-center p-3 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700">
                <Building className="w-4 h-4 mr-2" /> University
              </button>
              <button onClick={() => seedLogin('csr@tatasteel.com')} className="flex items-center justify-center p-3 border border-transparent text-sm font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700">
                <Factory className="w-4 h-4 mr-2" /> Industry CSR
              </button>
              <button onClick={() => seedLogin('rahul@citizen.in')} className="flex items-center justify-center p-3 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700">
                <User className="w-4 h-4 mr-2" /> Citizen
              </button>
            </div>
          </div>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-neutral-300 dark:border-neutral-600" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white dark:bg-neutral-800 text-neutral-500">Or manual login</span>
            </div>
          </div>

          <form className="space-y-6 mt-6" onSubmit={handleLogin}>
            <div>
              <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300">Email address</label>
              <div className="mt-1">
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md shadow-sm placeholder-neutral-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm dark:bg-neutral-700 dark:text-white"
                />
              </div>
            </div>
            {error && <div className="text-red-600 text-sm">{error}</div>}
            <div>
              <button
                type="submit"
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Sign in
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
