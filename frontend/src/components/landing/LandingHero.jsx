import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { Send, Compass, ArrowRight } from 'lucide-react'

export default function LandingHero() {
  const navigate = useNavigate()
  const { token } = useAuth()

  const handleReportChallenge = () => {
    if (token) {
      navigate('/dashboard/citizen')
    } else {
      navigate('/login?redirect=/dashboard/citizen&role=Citizen')
    }
  }

  const handleExplore = () => {
    const el = document.getElementById('lifecycle-flow')
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <section className="pt-16 pb-12 sm:pt-20 sm:pb-16 text-center px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto">
      {/* Main Display Headline */}
      <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 dark:text-white tracking-tight leading-[1.15] sm:leading-[1.15]">
        From Societal Challenges to{' '}
        <span className="relative inline-block text-blue-700 dark:text-blue-400">
          Real-World
          <span className="block text-blue-700 dark:text-blue-400">
            Impact
          </span>
          <span className="absolute left-0 bottom-1 w-full h-[3px] bg-blue-600 dark:bg-blue-400 rounded-full" />
        </span>
      </h1>

      {/* Subtitle Description */}
      <p className="mt-6 sm:mt-8 text-base sm:text-lg text-slate-600 dark:text-slate-300 max-w-3xl mx-auto leading-relaxed">
        Discover emerging civic friction, verify ground realities, intelligently route problems to tri-party solution ecosystems, and track audited deliverables from lab innovation to permanent rural transformation.
      </p>

      {/* Action Buttons */}
      <div className="mt-8 sm:mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
        <button
          onClick={handleReportChallenge}
          className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 text-sm sm:text-base font-semibold text-white bg-blue-700 hover:bg-blue-800 dark:bg-blue-600 dark:hover:bg-blue-500 rounded shadow-md hover:shadow-lg transition-all"
        >
          <Send className="w-4 h-4" />
          <span>Report a Challenge</span>
          <ArrowRight className="w-4 h-4 ml-1" />
        </button>

        <button
          onClick={handleExplore}
          className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 text-sm sm:text-base font-semibold text-blue-700 dark:text-blue-300 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-750 border border-blue-200 dark:border-blue-800/60 rounded shadow-sm hover:shadow transition-all"
        >
          <Compass className="w-4 h-4 text-blue-600 dark:text-blue-400" />
          <span>Explore the Platform</span>
        </button>
      </div>
    </section>
  )
}
