import { caseStudyMetrics } from '../../data/landingData'
import { Activity, Network, ClipboardCheck, Gauge } from 'lucide-react'

const ICON_MAP = {
  Activity,
  Network,
  ClipboardCheck,
  Gauge,
}

export default function CaseStudySection() {
  return (
    <section className="py-12 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="text-center max-w-3xl mx-auto mb-10">
        <span className="inline-block text-[11px] font-bold tracking-wider uppercase text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 px-3 py-1 rounded-full mb-3">
          Audited Case Study
        </span>
        <h2 className="text-2xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight">
          Turning Public Challenges into Innovation
        </h2>
        <p className="mt-3 text-sm sm:text-base text-slate-600 dark:text-slate-300 leading-relaxed">
          Real-world testbed: How a cluster of 124 rural telemedicine complaints became an active digital health clinic network across 42 remote villages.
        </p>
      </div>

      {/* 4 Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {caseStudyMetrics.map((item) => {
          const IconComponent = ICON_MAP[item.icon] || Activity

          return (
            <div
              key={item.id}
              className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm flex flex-col items-center text-center hover:border-slate-300 dark:hover:border-slate-700 transition-all"
            >
              <div className="w-12 h-12 rounded-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex items-center justify-center mb-4">
                <IconComponent className={`w-6 h-6 ${item.iconColor}`} />
              </div>

              <div className="text-3xl sm:text-4xl font-extrabold text-blue-700 dark:text-blue-400 tracking-tight tabular-nums">
                {item.value}
              </div>

              <div className="text-sm font-bold text-slate-900 dark:text-white mt-1.5">
                {item.title}
              </div>

              <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">
                {item.subtext}
              </p>
            </div>
          )
        })}
      </div>
    </section>
  )
}
