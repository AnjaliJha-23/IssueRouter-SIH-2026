import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { User, Menu, X } from 'lucide-react'
import logoSvg from '../../assets/issuerouter-logo.svg'

export default function LandingNavbar() {
  const navigate = useNavigate()
  const { user, token } = useAuth()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const handleLoginClick = () => {
    navigate('/login')
  }

  const handleProfileClick = () => {
    if (token) {
      if (user?.role === 'Gov') navigate('/dashboard/gov')
      else if (user?.role === 'Industry') navigate('/dashboard/industry')
      else if (user?.role === 'University') navigate('/dashboard/org')
      else navigate('/dashboard/citizen')
    } else {
      navigate('/login')
    }
  }

  const scrollTo = (id) => {
    setMobileMenuOpen(false)
    if (id === 'top') {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } else {
      const el = document.getElementById(id)
      if (el) el.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <header className="sticky top-0 z-50 bg-white/95 dark:bg-[#0b1c30]/95 backdrop-blur-md border-b border-slate-200/80 dark:border-slate-800 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-18 sm:h-20 flex items-center justify-between">
        
        {/* Left: IssueRouter Logo */}
        <div 
          onClick={() => scrollTo('top')}
          className="flex items-center cursor-pointer group"
          title="IssueRouter Home"
        >
          <img 
            src={logoSvg} 
            alt="IssueRouter Logo" 
            className="h-8 sm:h-10 w-auto object-contain transition-transform group-hover:scale-[1.02]"
          />
        </div>

        {/* Right Desktop Nav: Home, How it Works, About, Login button, User profile */}
        <nav className="hidden md:flex items-center gap-8">
          <button 
            type="button"
            onClick={() => scrollTo('top')}
            className="text-sm font-medium text-slate-700 hover:text-blue-600 dark:text-slate-300 dark:hover:text-blue-400 transition-colors cursor-pointer"
          >
            Home
          </button>
          <button 
            type="button"
            onClick={() => scrollTo('problem-to-impact')}
            className="text-sm font-medium text-slate-700 hover:text-blue-600 dark:text-slate-300 dark:hover:text-blue-400 transition-colors cursor-pointer"
          >
            How it Works
          </button>
          <button 
            type="button"
            onClick={() => scrollTo('about')}
            className="text-sm font-medium text-slate-700 hover:text-blue-600 dark:text-slate-300 dark:hover:text-blue-400 transition-colors cursor-pointer"
          >
            About
          </button>

          {/* Login Button (Strictly "Login" per design reference) */}
          <button
            type="button"
            id="nav-login-btn"
            onClick={handleLoginClick}
            className="px-5 py-2 text-sm font-semibold text-white bg-[#0F172A] hover:bg-[#1E293B] dark:bg-blue-600 dark:hover:bg-blue-700 rounded-lg shadow-sm transition-all hover:shadow cursor-pointer"
          >
            Login
          </button>

          {/* User/Profile Icon */}
          <button 
            type="button"
            id="nav-profile-btn"
            onClick={handleProfileClick}
            className="w-9 h-9 rounded-full border border-slate-300 dark:border-slate-700 flex items-center justify-center text-slate-700 dark:text-slate-300 hover:border-slate-500 hover:text-blue-600 dark:hover:text-blue-400 transition-all cursor-pointer bg-slate-50/50 dark:bg-slate-800/50"
            title={user ? `${user.email} (${user.role})` : 'User Profile'}
            aria-label="User Profile"
          >
            <User className="w-5 h-5" />
          </button>
        </nav>

        {/* Mobile Hamburger Controls */}
        <div className="flex md:hidden items-center gap-3">
          <button
            type="button"
            onClick={handleLoginClick}
            className="px-3.5 py-1.5 text-xs font-semibold text-white bg-[#0F172A] dark:bg-blue-600 rounded-lg shadow-sm cursor-pointer"
          >
            Login
          </button>

          <button 
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-1.5 text-slate-600 dark:text-slate-300 hover:text-slate-900 rounded-md focus:outline-none cursor-pointer"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0b1c30] px-4 pt-3 pb-5 space-y-3">
          <button 
            type="button"
            onClick={() => scrollTo('top')}
            className="block w-full text-left py-2 text-sm font-medium text-slate-700 dark:text-slate-200 cursor-pointer"
          >
            Home
          </button>
          <button 
            type="button"
            onClick={() => scrollTo('problem-to-impact')}
            className="block w-full text-left py-2 text-sm font-medium text-slate-700 dark:text-slate-200 cursor-pointer"
          >
            How it Works
          </button>
          <button 
            type="button"
            onClick={() => scrollTo('about')}
            className="block w-full text-left py-2 text-sm font-medium text-slate-700 dark:text-slate-200 cursor-pointer"
          >
            About
          </button>
        </div>
      )}
    </header>
  )
}
