import LandingNavbar from '../components/landing/LandingNavbar'
import LandingHero from '../components/landing/LandingHero'
import StakeholderCards from '../components/landing/StakeholderCards'
import LifecycleFlow from '../components/landing/LifecycleFlow'
import LandingFooter from '../components/landing/LandingFooter'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#f8f9ff] dark:bg-[#070e1c] text-slate-900 dark:text-slate-100 font-sans antialiased selection:bg-blue-600 selection:text-white overflow-x-hidden flex flex-col justify-between">
      {/* 1. Top Navbar */}
      <LandingNavbar />

      {/* Main Content Sections */}
      <main className="flex-1">
        {/* 2. Hero Section */}
        <LandingHero />

        {/* 3. Stakeholder Role Selection */}
        <StakeholderCards />

        {/* 4. "From Problem to Impact" Lifecycle Flow */}
        <LifecycleFlow />
      </main>

      {/* 5. Institutional Footer */}
      <LandingFooter />
    </div>
  )
}
