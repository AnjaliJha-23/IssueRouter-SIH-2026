import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { stakeholderRoles } from '../../data/landingData'
import { Landmark, GraduationCap, Factory, Users, Shield, ArrowRight } from 'lucide-react'

const ICON_MAP = {
  Landmark,
  GraduationCap,
  Factory,
  Users,
}

export default function StakeholderCards() {
  const navigate = useNavigate()
  const { token } = useAuth()

  const handleRoleAction = (role) => {
    if (token) {
      navigate(role.targetRoute)
    } else {
      navigate(`/login?role=${role.targetRole}&redirect=${role.targetRoute}`)
    }
  }

  return (
    <section id="stakeholders" className="py-12 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
        <div>
          <div className="text-[11px] font-bold tracking-wider uppercase text-blue-700 dark:text-blue-400">
            Multi-Stakeholder Federation
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white mt-1">
            One Platform. Every Stakeholder.
          </h2>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-2 max-w-2xl">
            Choose your institutional role to enter the authenticated workspace, unlock specialized governance privileges, or submit ground-truth challenge data.
          </p>
        </div>

        <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded text-xs font-semibold text-slate-700 dark:text-slate-300 self-start md:self-auto">
          <Shield className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
          <span>DigiLocker & National SSO Federated</span>
        </div>
      </div>

      {/* 4 Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {stakeholderRoles.map((role) => {
          const IconComponent = ICON_MAP[role.icon] || Landmark

          return (
            <div
              key={role.id}
              className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm hover:shadow-md hover:border-slate-300 dark:hover:border-slate-700 transition-all flex flex-col justify-between"
            >
              <div>
                {/* Header Icon + Role Badge */}
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${role.iconBg}`}>
                    <IconComponent className="w-5 h-5" />
                  </div>
                  <span className={`text-[10px] font-bold px-2.5 py-1 rounded border ${role.badgeStyle}`}>
                    {role.badge}
                  </span>
                </div>

                {/* Role Title & Mandate */}
                <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
                  {role.title}
                </h3>
                <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed min-h-[60px]">
                  {role.desc}
                </p>

                {/* Stats Container */}
                <div className="mt-4 p-3 bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-750 rounded-lg space-y-1.5">
                  {role.stats.map((st, idx) => (
                    <div key={idx} className="flex items-center justify-between text-xs">
                      <span className="text-slate-500 dark:text-slate-400">{st.label}:</span>
                      <span className={`font-bold tabular-nums ${st.highlight ? 'text-blue-700 dark:text-blue-400' : 'text-slate-800 dark:text-slate-200'}`}>
                        {st.value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Action Link / Button */}
              <div className="mt-6 pt-3 border-t border-slate-100 dark:border-slate-800">
                <button
                  onClick={() => handleRoleAction(role)}
                  className={`w-full inline-flex items-center justify-between text-xs font-bold py-1.5 transition-colors group ${role.ctaColor}`}
                >
                  <span>{role.ctaText}</span>
                  <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                </button>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
