import { useAuth } from '../context/AuthContext'
import { User, Mail, Shield, Building, Calendar, CheckCircle2 } from 'lucide-react'

export default function Profile() {
  const { user } = useAuth()

  const initials = user?.name
    ? user.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    : (user?.role ? user.role.slice(0, 2).toUpperCase() : 'U')

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
          User Account & Identity
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Authenticated credentials and role profile on the SIC Portal.
        </p>
      </div>

      <div className="bg-white dark:bg-neutral-900 rounded-2xl border border-slate-200/80 dark:border-neutral-800 shadow-sm overflow-hidden">
        {/* Banner */}
        <div className="h-28 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 relative">
          <div className="absolute -bottom-8 left-6">
            <div className="w-18 h-18 rounded-2xl bg-white dark:bg-neutral-900 border-4 border-white dark:border-neutral-900 shadow-md flex items-center justify-center text-xl font-bold text-blue-600 dark:text-blue-400">
              {initials}
            </div>
          </div>
        </div>

        {/* Details header */}
        <div className="pt-10 px-6 pb-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-100 dark:border-neutral-800 pb-5">
            <div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                {user?.name || 'Citizen User'}
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                {user?.email || 'N/A'}
              </p>
            </div>
            <div>
              <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${
                user?.role === 'Citizen'
                  ? 'bg-purple-100 text-purple-800 dark:bg-purple-950/40 dark:text-purple-300 border border-purple-200 dark:border-purple-800'
                  : user?.role === 'Gov'
                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-950/40 dark:text-blue-300 border border-blue-200 dark:border-blue-800'
                  : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'
              }`}>
                <Shield size={12} />
                Role: {user?.role || 'Guest'}
              </span>
            </div>
          </div>

          {/* Identity Grid */}
          <div className="grid sm:grid-cols-2 gap-4 mt-6">
            <div className="p-4 rounded-xl bg-slate-50 dark:bg-neutral-800/60 border border-slate-100 dark:border-neutral-700/60 flex items-start gap-3">
              <div className="p-2 rounded-lg bg-blue-500/10 text-blue-600 dark:text-blue-400">
                <User size={18} />
              </div>
              <div>
                <p className="text-[11px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Full Legal Name</p>
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 mt-0.5">{user?.name || 'Citizen User'}</p>
                <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">Verified citizen profile</p>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 dark:bg-neutral-800/60 border border-slate-100 dark:border-neutral-700/60 flex items-start gap-3">
              <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">
                <Mail size={18} />
              </div>
              <div>
                <p className="text-[11px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Registered Email</p>
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 mt-0.5">{user?.email || 'N/A'}</p>
                <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">Primary notification inbox</p>
              </div>
            </div>

            {user?.organization && (
              <div className="p-4 rounded-xl bg-slate-50 dark:bg-neutral-800/60 border border-slate-100 dark:border-neutral-700/60 flex items-start gap-3 sm:col-span-2">
                <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                  <Building size={18} />
                </div>
                <div>
                  <p className="text-[11px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Affiliated Organization</p>
                  <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 mt-0.5">{user.organization.name}</p>
                  <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">Type: {user.organization.type}</p>
                </div>
              </div>
            )}
          </div>

          <div className="mt-6 p-4 rounded-xl bg-purple-50/60 dark:bg-purple-950/20 border border-purple-100 dark:border-purple-900/40 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <CheckCircle2 size={16} className="text-purple-600 dark:text-purple-400 flex-shrink-0" />
              <p className="text-xs text-purple-900 dark:text-purple-200 font-medium">
                Identity verified for SIC Portal SIH 2026 Participation
              </p>
            </div>
            <span className="text-[11px] text-purple-600 dark:text-purple-400 font-bold uppercase tracking-wider">Active</span>
          </div>
        </div>
      </div>
    </div>
  )
}
