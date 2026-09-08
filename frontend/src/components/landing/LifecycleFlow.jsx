import { lifecyclePhases } from '../../data/landingData'
import { Search, ShieldCheck, GitFork, Handshake, CheckCircle2 } from 'lucide-react'

const ICON_MAP = {
  Search,
  ShieldCheck,
  GitFork,
  Handshake,
  CheckCircle2,
}

export default function LifecycleFlow() {
  return (
    <section id="problem-to-impact" className="py-16 md:py-24 bg-[#eff5ff]/70 dark:bg-slate-950/40 border-y border-blue-50 dark:border-slate-800/80 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-12 sm:mb-16">
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-[#0b1c30] dark:text-white tracking-tight font-heading">
            From Problem to Impact
          </h2>
          <p className="mt-3 text-sm sm:text-base text-slate-600 dark:text-slate-300 leading-relaxed">
            A streamlined transparent journey from citizen submission to verified resolution.
          </p>
        </div>

        {/* 5 Stages Horizontal Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 sm:gap-5">
          {lifecyclePhases.map((phase) => {
            const IconComponent = ICON_MAP[phase.icon] || Search
            const isFinalStage = phase.number === '05'

            return (
              <div
                key={phase.phase}
                className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 p-6 sm:p-7 shadow-[0_2px_8px_rgba(15,23,42,0.03)] hover:shadow-md transition-all duration-300 flex flex-col items-center text-center justify-center min-h-[190px]"
              >
                {/* Icon Container with Number Badge Overlay */}
                <div className="relative mb-5">
                  <div className={`w-14 h-14 rounded-full flex items-center justify-center ${
                    isFinalStage 
                      ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 border border-emerald-200/60 dark:border-emerald-800/60'
                      : 'bg-slate-50 dark:bg-slate-800/80 text-slate-700 dark:text-slate-200 border border-slate-200/60 dark:border-slate-700/60'
                  }`}>
                    <IconComponent className="w-6 h-6" />
                  </div>

                  {/* Top-Right Circular Number Badge */}
                  <span className={`absolute -top-1 -right-1 w-5 h-5 rounded-full text-[10px] font-bold flex items-center justify-center text-white shadow-sm ${
                    isFinalStage ? 'bg-emerald-600' : 'bg-[#0F172A] dark:bg-blue-600'
                  }`}>
                    {phase.number}
                  </span>
                </div>

                {/* Stage Title */}
                <h3 className="text-sm sm:text-[15px] font-bold text-slate-900 dark:text-white leading-snug font-heading max-w-[170px]">
                  {phase.title}
                </h3>
              </div>
            )
          })}
        </div>

      </div>
    </section>
  )
}
