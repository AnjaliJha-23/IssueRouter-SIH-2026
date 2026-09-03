import { lifecyclePhases } from '../../data/landingData'
import { Radio, Brain, ShieldCheck, GitMerge, FlaskConical, Award } from 'lucide-react'

const ICON_MAP = {
  Radio,
  Brain,
  ShieldCheck,
  GitMerge,
  FlaskConical,
  Award,
}

export default function LifecycleFlow() {
  return (
    <section id="lifecycle-flow" className="py-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Outer Card Container */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 rounded-2xl p-5 sm:p-8 shadow-sm">
        
        {/* Section Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6 pb-4 border-b border-slate-100 dark:border-slate-800">
          <div>
            <div className="text-[11px] font-bold tracking-wider uppercase text-blue-700 dark:text-blue-400">
              End-to-End Governance Engine
            </div>
            <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white mt-1">
              Societal Problem Lifecycle Flow
            </h2>
          </div>

          {/* Real-time Status Indicator */}
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 rounded-full self-start sm:self-auto">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            <span className="text-[11px] font-semibold text-emerald-800 dark:text-emerald-300">
              Continuous Algorithmic Synchronization
            </span>
          </div>
        </div>

        {/* 6 Phases Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3 sm:gap-4">
          {lifecyclePhases.map((phase) => {
            const IconComponent = ICON_MAP[phase.icon] || Radio
            const isActive = phase.active

            return (
              <div
                key={phase.phase}
                className={`flex flex-col justify-between p-4 rounded-xl border transition-all ${
                  isActive
                    ? 'bg-blue-50/70 dark:bg-blue-950/30 border-blue-300 dark:border-blue-700 shadow-sm ring-1 ring-blue-400/30'
                    : 'bg-slate-50/70 dark:bg-slate-800/40 border-slate-200/80 dark:border-slate-750 hover:bg-slate-100/70 dark:hover:bg-slate-800/70'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
                    <span className="text-[10px] font-bold tracking-wider uppercase">
                      Phase {phase.phase}
                    </span>
                    <IconComponent className={`w-4 h-4 ${isActive ? 'text-blue-600 dark:text-blue-400' : 'text-slate-500'}`} />
                  </div>

                  <h3 className={`text-sm font-bold mb-1.5 ${isActive ? 'text-blue-900 dark:text-blue-200' : 'text-slate-900 dark:text-white'}`}>
                    {phase.title}
                  </h3>

                  <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                    {phase.desc}
                  </p>
                </div>

                <div className="mt-4 pt-2 border-t border-slate-200/60 dark:border-slate-700/60 flex items-center justify-between">
                  <span className={`text-[11px] font-bold ${
                    phase.badgeColor === 'emerald' ? 'text-emerald-700 dark:text-emerald-400' :
                    phase.badgeColor === 'blue' ? 'text-blue-700 dark:text-blue-400' :
                    'text-slate-700 dark:text-slate-300'
                  }`}>
                    {phase.badge}
                  </span>
                  <span className={`h-1.5 w-1.5 rounded-full ${
                    phase.badgeColor === 'emerald' ? 'bg-emerald-500' :
                    phase.badgeColor === 'blue' ? 'bg-blue-500' :
                    'bg-slate-400'
                  }`} />
                </div>
              </div>
            )
          })}
        </div>

      </div>
    </section>
  )
}
