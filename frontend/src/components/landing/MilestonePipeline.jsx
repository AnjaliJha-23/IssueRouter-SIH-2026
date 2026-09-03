import { milestonePipeline } from '../../data/landingData'
import { Check } from 'lucide-react'

export default function MilestonePipeline() {
  return (
    <section className="py-8 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 sm:p-8 shadow-sm">
        
        {/* Header */}
        <div className="mb-6">
          <div className="text-[11px] font-bold tracking-wider uppercase text-blue-700 dark:text-blue-400">
            Proof of Execution Flow
          </div>
          <h3 className="text-lg sm:text-xl font-extrabold text-slate-900 dark:text-white mt-1">
            Verified Milestone Progress Pipeline
          </h3>
        </div>

        {/* 7-step horizontal pipeline */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
          {milestonePipeline.map((step) => {
            const isCompleted = step.status === 'completed'
            const isActive = step.status === 'active'

            return (
              <div
                key={step.id}
                className={`flex flex-col items-center text-center p-3.5 rounded-xl border transition-all ${
                  isActive
                    ? 'bg-blue-50 dark:bg-blue-950/40 border-blue-300 dark:border-blue-700 shadow-sm'
                    : isCompleted
                    ? 'bg-slate-50/80 dark:bg-slate-800/40 border-slate-200/80 dark:border-slate-750'
                    : 'bg-slate-50/40 dark:bg-slate-800/20 border-dashed border-slate-200 dark:border-slate-700'
                }`}
              >
                {/* Node icon */}
                <div className="mb-2">
                  {isCompleted ? (
                    <div className="w-7 h-7 rounded-full bg-emerald-600 text-white flex items-center justify-center shadow-xs">
                      <Check className="w-4 h-4 stroke-[3]" />
                    </div>
                  ) : isActive ? (
                    <div className="w-7 h-7 rounded-full bg-blue-700 text-white font-bold text-xs flex items-center justify-center shadow-xs">
                      {step.badge || '06'}
                    </div>
                  ) : (
                    <div className="w-7 h-7 rounded-full bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-600 text-slate-400 font-bold text-xs flex items-center justify-center">
                      {step.badge || '07'}
                    </div>
                  )}
                </div>

                {/* Title */}
                <div className={`text-xs font-bold ${isActive ? 'text-blue-900 dark:text-blue-200' : 'text-slate-900 dark:text-white'}`}>
                  {step.title}
                </div>

                {/* Subtitle / Status */}
                <div className={`text-[11px] mt-0.5 ${isActive ? 'text-blue-700 dark:text-blue-400 font-semibold' : 'text-slate-500 dark:text-slate-400'}`}>
                  {step.subtitle}
                </div>
              </div>
            )
          })}
        </div>

      </div>
    </section>
  )
}
