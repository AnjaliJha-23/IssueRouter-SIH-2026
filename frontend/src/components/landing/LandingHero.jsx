import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { Share2, CheckCircle2, Globe } from 'lucide-react'
import heroImg from '../../assets/homeimage.png'

export default function LandingHero() {
  const navigate = useNavigate()
  const { token } = useAuth()

  const handleReportChallenge = () => {
    if (token) {
      navigate('/dashboard/citizen')
    } else {
      navigate('/login?role=Citizen&redirect=/dashboard/citizen')
    }
  }

  const handleLearnMore = () => {
    const el = document.getElementById('problem-to-impact')
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <section className="relative pt-12 pb-16 md:pt-16 md:pb-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto overflow-hidden">
      {/* Background Dot Grid Effect */}
      <div 
        className="absolute inset-0 pointer-events-none opacity-[0.4] dark:opacity-[0.1]"
        style={{
          backgroundImage: 'radial-gradient(#94a3b8 1px, transparent 1px)',
          backgroundSize: '24px 24px'
        }}
      />

      <div className="relative grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
        
        {/* Left Column (58% / 7 cols) */}
        <div className="lg:col-span-7 flex flex-col items-start text-left space-y-6 sm:space-y-8">
          
          {/* Main Headline */}
          <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-[52px] font-extrabold text-[#0b1c30] dark:text-white tracking-tight leading-[1.15] font-heading">
            Crowdsourcing Societal <br className="hidden sm:inline" />
            Challenges. <br className="hidden sm:inline" />
            Solving Them Together.
          </h1>

          {/* Supporting Text */}
          <p className="text-base sm:text-lg text-slate-600 dark:text-slate-300 max-w-2xl leading-relaxed">
            Connecting citizens, government bodies, academic institutions, and industry leaders into a single collaborative problem-solving network.
          </p>

          {/* Action CTAs */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 w-full sm:w-auto pt-2">
            <button
              type="button"
              id="hero-report-btn"
              onClick={handleReportChallenge}
              className="inline-flex items-center justify-center px-7 py-3.5 text-sm sm:text-base font-semibold text-white bg-[#0F172A] hover:bg-[#1E293B] dark:bg-blue-600 dark:hover:bg-blue-700 rounded-lg shadow-sm hover:shadow transition-all cursor-pointer"
            >
              Report a Challenge
            </button>

            <button
              type="button"
              id="hero-learn-btn"
              onClick={handleLearnMore}
              className="inline-flex items-center justify-center px-7 py-3.5 text-sm sm:text-base font-semibold text-slate-800 dark:text-slate-200 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-750 border border-slate-300 dark:border-slate-700 rounded-lg shadow-sm hover:shadow transition-all cursor-pointer"
            >
              Learn More
            </button>
          </div>

          {/* Small Trust / Value Indicators */}
          <div className="pt-4 flex flex-wrap items-center gap-2.5 sm:gap-3 text-xs text-slate-600 dark:text-slate-300">
            <div className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-full shadow-[0_1px_2px_rgba(0,0,0,0.04)]">
              <Share2 className="w-3.5 h-3.5 text-slate-700 dark:text-slate-300" />
              <span className="font-medium">4 Stakeholder Roles</span>
            </div>

            <span className="text-slate-300 dark:text-slate-700 hidden sm:inline">•</span>

            <div className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-full shadow-[0_1px_2px_rgba(0,0,0,0.04)]">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
              <span className="font-medium">Verified Impact Tracking</span>
            </div>

            <span className="text-slate-300 dark:text-slate-700 hidden sm:inline">•</span>

            <div className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-full shadow-[0_1px_2px_rgba(0,0,0,0.04)]">
              <Globe className="w-3.5 h-3.5 text-slate-700 dark:text-slate-300" />
              <span className="font-medium">Open Civic Collaboration</span>
            </div>
          </div>

        </div>

        {/* Right Column: Hero Illustration Image (42% / 5 cols) */}
        <div className="lg:col-span-5 flex justify-center lg:justify-end">
          <div className="relative w-full max-w-md lg:max-w-none bg-white dark:bg-slate-850 p-2 sm:p-3 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-[0_12px_40px_rgba(15,23,42,0.07)] dark:shadow-[0_12px_40px_rgba(0,0,0,0.3)]">
            <img 
              src={heroImg} 
              alt="IssueRouter Societal Innovation Collaboration Portal" 
              className="w-full h-auto object-contain rounded-xl"
              loading="eager"
            />
          </div>
        </div>

      </div>
    </section>
  )
}
