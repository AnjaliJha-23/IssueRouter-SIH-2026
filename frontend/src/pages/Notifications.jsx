import { useAuth } from '../context/AuthContext'
import { Bell, CheckCircle2, Clock, ArrowRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function Notifications() {
  const { user } = useAuth()
  const navigate = useNavigate()

  const sampleNotifications = [
    {
      id: 'notif-1',
      title: 'Challenge Submission Confirmed',
      message: 'Your report on local infrastructure has been safely received and queued for AI deduplication.',
      time: 'Just now',
      read: false,
      tag: 'Submission',
      action: '/progress'
    },
    {
      id: 'notif-2',
      title: 'System Update: Smart Router Active',
      message: 'Automated semantic routing to Jharkhand state universities is operating normally.',
      time: '2 hours ago',
      read: true,
      tag: 'System',
      action: null
    }
  ]

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
            Notifications & Updates
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Real-time status alerts regarding your submissions and platform activity.
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {sampleNotifications.map((notif) => (
          <div
            key={notif.id}
            className={`p-4 rounded-xl border transition-all ${
              notif.read
                ? 'bg-white dark:bg-neutral-900 border-slate-200/70 dark:border-neutral-800'
                : 'bg-blue-50/40 dark:bg-blue-950/20 border-blue-200/80 dark:border-blue-900/60 shadow-xs'
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-start gap-3">
                <div className={`p-2 rounded-lg mt-0.5 ${
                  notif.read
                    ? 'bg-slate-100 dark:bg-neutral-800 text-slate-500'
                    : 'bg-blue-500/10 text-blue-600 dark:text-blue-400'
                }`}>
                  <Bell size={16} />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                      {notif.title}
                    </h3>
                    {!notif.read && (
                      <span className="w-2 h-2 rounded-full bg-blue-600 dark:bg-blue-400" />
                    )}
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">
                    {notif.message}
                  </p>
                  <div className="flex items-center gap-2 mt-2 text-[11px] text-slate-400">
                    <Clock size={11} />
                    <span>{notif.time}</span>
                  </div>
                </div>
              </div>

              {notif.action && (
                <button
                  onClick={() => navigate(notif.action)}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950/40 transition-colors flex items-center gap-1 cursor-pointer"
                >
                  View <ArrowRight size={12} />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
