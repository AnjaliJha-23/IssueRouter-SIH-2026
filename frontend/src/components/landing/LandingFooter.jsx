export default function LandingFooter() {
  const scrollTo = (id) => {
    if (id === 'top') {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } else {
      const el = document.getElementById(id)
      if (el) el.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <footer id="about" className="bg-[#0F172A] text-slate-400 pt-16 pb-12 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Top Row: Left Brand Info & Right Nav Links */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-8 pb-10 border-b border-slate-800">
          
          {/* Left: Brand & Tagline */}
          <div className="space-y-2">
            <h3 
              onClick={() => scrollTo('top')}
              className="text-xl sm:text-2xl font-extrabold text-white tracking-tight cursor-pointer font-heading inline-block"
            >
              IssueRouter
            </h3>
            <p className="text-xs sm:text-sm text-slate-400 max-w-lg leading-relaxed">
              Societal Innovation Portal — Crowdsourcing civic challenges for collective impact
            </p>
          </div>

          {/* Right: About, Contact, Privacy */}
          <nav className="flex items-center gap-6 sm:gap-8 text-xs sm:text-sm">
            <button 
              onClick={() => scrollTo('top')}
              className="hover:text-white transition-colors cursor-pointer"
            >
              About
            </button>
            <a 
              href="mailto:support@issuerouter.gov.in"
              className="hover:text-white transition-colors"
            >
              Contact
            </a>
            <span className="hover:text-white transition-colors cursor-pointer">
              Privacy
            </span>
          </nav>

        </div>

        {/* Bottom Row: Copyright Notice */}
        <div className="pt-8 text-xs text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p>© 2026 IssueRouter • Government of Jharkhand • SIH 2026. All rights reserved.</p>
        </div>

      </div>
    </footer>
  )
}
