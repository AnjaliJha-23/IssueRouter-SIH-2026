import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { ShieldAlert, ArrowLeft, Home } from 'lucide-react'

export default function Unauthorized() {
  const { user } = useAuth()
  const navigate = useNavigate()

  const getDashboardPath = () => {
    if (user?.role === 'Gov') return '/dashboard/gov'
    if (user?.role === 'University') return '/dashboard/org'
    if (user?.role === 'Industry') return '/dashboard/industry'
    return '/dashboard/citizen'
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col items-center justify-center p-6 text-center">
      <div className="w-16 h-16 rounded-2xl bg-amber-500/10 text-amber-600 dark:text-amber-400 flex items-center justify-center mb-6 shadow-xs border border-amber-500/20">
        <ShieldAlert size={36} />
      </div>

      <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white tracking-tight mb-2">
        Restricted Access Area
      </h1>

      <p className="text-sm text-slate-600 dark:text-slate-400 max-w-md mb-8 leading-relaxed">
        Your authenticated account role <strong className="font-semibold text-slate-800 dark:text-slate-200">({user?.role || 'Guest'})</strong> does not have permission to view this section or administrative portal.
      </p>

      <div className="flex flex-col sm:flex-row gap-3">
        <button
          onClick={() => navigate(getDashboardPath())}
          className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold shadow-sm hover:shadow transition-all cursor-pointer"
        >
          <Home size={16} /> Return to My Portal
        </button>
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 text-sm font-medium transition-colors cursor-pointer"
        >
          <ArrowLeft size={16} /> Go Back
        </button>
      </div>
    </div>
  )
}
