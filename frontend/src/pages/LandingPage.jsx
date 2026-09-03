import LandingNavbar from '../components/landing/LandingNavbar'
import LandingHero from '../components/landing/LandingHero'
import LifecycleFlow from '../components/landing/LifecycleFlow'
import StakeholderCards from '../components/landing/StakeholderCards'
import CaseStudySection from '../components/landing/CaseStudySection'
import MilestonePipeline from '../components/landing/MilestonePipeline'
import LandingFooter from '../components/landing/LandingFooter'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#faf8ff] via-[#f8fafc] to-[#f1f5f9] dark:from-[#0b1329] dark:via-[#090f20] dark:to-[#070b18] text-slate-900 dark:text-slate-100 font-sans antialiased selection:bg-blue-600 selection:text-white overflow-x-hidden">
      {/* Top Navbar */}
      <LandingNavbar />

      {/* Main Content Sections */}
      <main>
        {/* 1. Hero Section */}
        <LandingHero />

        {/* 2. End-to-End Governance Engine (6 Phases) */}
        <LifecycleFlow />

        {/* 3. Multi-Stakeholder Federation (4 Cards) */}
        <StakeholderCards />

        {/* 4. Audited Case Study & 4 Key Impact Metrics */}
        <CaseStudySection />

        {/* 5. Proof of Execution Flow (Milestone Pipeline) */}
        <MilestonePipeline />
      </main>

      {/* Footer */}
      <LandingFooter />
    </div>
  )
}
