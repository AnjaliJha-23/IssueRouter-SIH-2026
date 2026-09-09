import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { stakeholderRoles } from '../../data/landingData'
import { Building2, GraduationCap, Factory, Users, ArrowRight } from 'lucide-react'

const ICON_MAP = {
  Building2,
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
    <section id="roles" className="py-16 md:py-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      {/* Section Header */}
      <div className="text-center max-w-3xl mx-auto mb-12 sm:mb-16">
        <h2 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-[#0b1c30] dark:text-white tracking-tight font-heading">
          Choose Your Role to Continue
        </h2>
        <p className="mt-3 text-sm sm:text-base text-slate-600 dark:text-slate-300 leading-relaxed">
          Select your ecosystem role to access dedicated tools, challenge feeds, and resource pipelines.
        </p>
      </div>

      {/* 4 Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {stakeholderRoles.map((role) => {
          const IconComponent = ICON_MAP[role.icon] || Building2

          return (
            <div
              key={role.id}
              onClick={() => handleRoleAction(role)}
              className={`group bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 ${role.accentBorder} border-t-4 p-6 shadow-sm hover:shadow-lg transition-all duration-300 flex flex-col justify-between cursor-pointer hover:-translate-y-1`}
            >
              <div>
                {/* Top Icon */}
                <div className="mb-5">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${role.iconBg}`}>
                    <IconComponent className="w-6 h-6" />
                  </div>
                </div>

                {/* Role Title */}
                <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2.5 font-heading">
                  {role.title}
                </h3>

                {/* Description */}
                <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed min-h-[64px]">
                  {role.desc}
                </p>

                {/* Status / Category Badge with Indicator Dot */}
                <div className="mt-4 pt-1">
                  <span className={`inline-flex items-center gap-1.5 text-[11px] font-semibold px-2.5 py-1 rounded-full border ${role.badgeStyle}`}>
                    <span className="w-1.5 h-1.5 rounded-full bg-current opacity-80" />
                    <span>{role.badge}</span>
                  </span>
                </div>
              </div>

              {/* Action Link / CTA Button */}
              <div className="mt-8 pt-4 border-t border-slate-100 dark:border-slate-800">
                <div className={`inline-flex items-center gap-1 text-xs sm:text-sm font-bold ${role.accentColor} transition-colors group-hover:gap-2`}>
                  <span>{role.ctaText}</span>
                </div>
              </div>

            </div>
          )
        })}
      </div>

    </section>
  )
}
