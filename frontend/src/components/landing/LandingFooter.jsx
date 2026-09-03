import { ShieldCheck } from 'lucide-react'
import logoImg from '../../assets/IssueRouter.png'

export default function LandingFooter() {
  const scrollTo = (id) => {
    const el = document.getElementById(id)
    if (el) el.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <footer className="mt-16 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          
          {/* Brand Info */}
          <div className="md:col-span-2 space-y-4">
            <div className="flex items-center gap-2.5">
              <img 
                src={logoImg} 
                alt="IssueRouter" 
                className="w-7 h-7 object-contain"
                onError={(e) => { e.target.style.display = 'none' }}
              />
              <span className="text-xl font-extrabold text-blue-700 dark:text-blue-400 tracking-tight">
                IssueRouter
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 bg-blue-100 dark:bg-blue-900/60 text-blue-800 dark:text-blue-300 rounded border border-blue-200 dark:border-blue-800">
                SIH 2026
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed max-w-md">
              IssueRouter Societal Innovation Portal • Smart India Hackathon 2026 Initiative.
              Official Public Innovation Platform connecting citizen intelligence with civic solutions.
            </p>
          </div>

          {/* Column: Platform */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white mb-3">
              Platform
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <button 
                  onClick={() => scrollTo('lifecycle-flow')}
                  className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                >
                  How It Works
                </button>
              </li>
              <li>
                <button 
                  onClick={() => scrollTo('lifecycle-flow')}
                  className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                >
                  Challenge Intelligence
                </button>
              </li>
              <li>
                <button 
                  onClick={() => scrollTo('lifecycle-flow')}
                  className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                >
                  Smart Router
                </button>
              </li>
            </ul>
          </div>

          {/* Column: Civic Trust */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white mb-3">
              Civic Trust
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <button 
                  onClick={() => scrollTo('stakeholders')}
                  className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                >
                  Impact
                </button>
              </li>
              <li>
                <span className="text-slate-400 dark:text-slate-500 cursor-not-allowed">
                  Privacy & Data Trust
                </span>
              </li>
              <li>
                <span className="text-slate-400 dark:text-slate-500 cursor-not-allowed">
                  Government Guidelines
                </span>
              </li>
            </ul>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="pt-6 border-t border-slate-100 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500 dark:text-slate-400">
          <div>
            © 2026 IssueRouter Civic Network. All rights reserved under National Innovation Framework.
          </div>
          
          <div className="inline-flex items-center gap-1.5 text-emerald-700 dark:text-emerald-400 font-semibold">
            <ShieldCheck className="w-4 h-4" />
            <span>verified public system</span>
          </div>
        </div>

      </div>
    </footer>
  )
}
