import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { User, Send, LogIn, LayoutDashboard } from 'lucide-react'
import logoImg from '../../assets/IssueRouter.png'

export default function LandingNavbar() {
  const navigate = useNavigate()
  const { user, token } = useAuth()

  const handleReportChallenge = () => {
    if (token) {
      navigate('/dashboard/citizen')
    } else {
      navigate('/login?redirect=/dashboard/citizen&role=Citizen')
    }
  }

  const handleSignIn = () => {
    if (token) {
      if (user?.role === 'Gov') navigate('/dashboard/gov')
      else if (user?.role === 'University' || user?.role === 'Industry') navigate('/dashboard/org')
      else navigate('/dashboard/citizen')
    } else {
      navigate('/login')
    }
  }

  return (
    <header className="sticky top-0 z-50 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border-b border-slate-200 dark:border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Left Brand Identity */}
        <div 
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          className="flex items-center gap-3 cursor-pointer group"
        >
          <img 
            src={logoImg} 
            alt="IssueRouter Logo" 
            className="w-8 h-8 object-contain transition-transform group-hover:scale-105"
            onError={(e) => { e.target.style.display = 'none' }}
          />
          <div className="flex items-center gap-2">
            <span className="text-xl font-extrabold tracking-tight text-blue-700 dark:text-blue-400">
              IssueRouter
            </span>
            <span className="hidden sm:inline-block text-[10px] tracking-wider uppercase font-semibold text-slate-500 dark:text-slate-400 border-l border-slate-300 dark:border-slate-700 pl-2">
              Societal Innovation Portal
            </span>
          </div>
        </div>

        {/* Right Action Controls */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleReportChallenge}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs sm:text-sm font-semibold text-blue-700 dark:text-blue-300 hover:text-blue-800 bg-blue-50/80 hover:bg-blue-100/80 dark:bg-blue-950/40 dark:hover:bg-blue-900/40 border border-blue-200 dark:border-blue-800 rounded transition-all"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Report a Challenge</span>
          </button>

          <button
            onClick={handleSignIn}
            className="inline-flex items-center gap-1.5 px-4 py-1.5 text-xs sm:text-sm font-semibold text-white bg-blue-700 hover:bg-blue-800 dark:bg-blue-600 dark:hover:bg-blue-500 rounded shadow-sm hover:shadow transition-all"
          >
            {token ? (
              <>
                <LayoutDashboard className="w-3.5 h-3.5" />
                <span>Portal</span>
              </>
            ) : (
              <>
                <LogIn className="w-3.5 h-3.5" />
                <span>Sign In</span>
              </>
            )}
          </button>

          {/* User Status / Avatar Pill */}
          <div 
            onClick={handleSignIn}
            className="p-1.5 text-slate-500 hover:text-blue-700 dark:text-slate-400 dark:hover:text-blue-400 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer transition-colors"
            title={user ? `${user.email} (${user.role})` : 'Account'}
          >
            <div className="w-7 h-7 rounded-full bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 flex items-center justify-center text-slate-600 dark:text-slate-300">
              <User className="w-4 h-4" />
            </div>
          </div>
        </div>

      </div>
    </header>
  )
}
