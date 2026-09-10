import { useState, useEffect, useMemo } from 'react'
import { authFetch } from '../api/client'
import {
  Building2,
  GraduationCap,
  Sparkles,
  DollarSign,
  Handshake,
  Mail,
  CheckCircle2,
  Search,
  X,
  Send,
  ArrowRight,
  TrendingUp,
  MapPin,
  Check,
  Award,
  ExternalLink,
  FileText,
  Cpu,
  Layers,
  ShieldCheck,
  Zap,
  BarChart3,
  FlaskConical,
  BookOpen,
  Target,
  Printer
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const FUNDING_TABS = [
  { key: 'all', label: 'All Proposals' },
  { key: 'open', label: 'Seeking CSR Funding' },
  { key: 'partial', label: 'Partially Funded' },
  { key: 'funded', label: 'Funded & In-Pilot' },
]

const DOMAIN_OPTIONS = [
  { value: '', label: 'All Domains' },
  { value: 'HealthTech', label: 'HealthTech' },
  { value: 'BioTech', label: 'BioTech' },
  { value: 'Public Health', label: 'Public Health' },
  { value: 'EdTech', label: 'EdTech' },
  { value: 'AgriTech', label: 'AgriTech' },
]

const UNIVERSITY_OPTIONS = [
  { value: '', label: 'All Universities' },
  { value: 'RIMS Ranchi', label: 'RIMS Ranchi' },
  { value: 'IIT ISM Dhanbad', label: 'IIT ISM Dhanbad' },
  { value: 'NIT Jamshedpur', label: 'NIT Jamshedpur' },
  { value: 'BIT Mesra', label: 'BIT Mesra' },
  { value: 'AIIMS Deoghar', label: 'AIIMS Deoghar' },
  { value: 'Birsa Agricultural University', label: 'Birsa Agricultural Univ' },
  { value: 'Kolhan University', label: 'Kolhan University' },
]

const DEPARTMENT_OPTIONS = [
  { value: '', label: 'All Departments' },
  { value: 'Rural Health', label: 'Rural Health' },
  { value: 'Public Health', label: 'Public Health' },
  { value: 'Medical Infrastructure', label: 'Medical Infrastructure' },
  { value: 'Child Welfare', label: 'Child Welfare' },
  { value: 'Water Dept', label: 'Water Dept' },
  { value: 'Energy', label: 'Energy' },
  { value: 'Education', label: 'Education' },
  { value: 'Agriculture', label: 'Agriculture' },
  { value: 'Sanitation', label: 'Sanitation' },
]

export default function IndustryDashboard() {
  const { user } = useAuth()
  const [proposals, setProposals] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [tabFilter, setTabFilter] = useState('all')
  const [visibleCount, setVisibleCount] = useState(9)

  // Filters
  const [filters, setFilters] = useState({
    search: '',
    domain: '',
    department: '',
    university: '',
  })

  // Modals & Drawer State
  const [selectedProposal, setSelectedProposal] = useState(null)
  const [collaborateProposal, setCollaborateProposal] = useState(null)
  const [fundProposal, setFundProposal] = useState(null)
  const [mailProposal, setMailProposal] = useState(null)

  // Toast Notification
  const [toast, setToast] = useState(null)

  const showToast = (message, type = 'success') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 4000)
  }

  useEffect(() => {
    fetchData()
  }, [filters, tabFilter])

  const fetchData = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (tabFilter !== 'all') params.append('funding_status', tabFilter)
      if (filters.search) params.append('search', filters.search)
      if (filters.domain) params.append('domain', filters.domain)
      if (filters.department) params.append('department', filters.department)
      if (filters.university) params.append('university', filters.university)

      const qs = params.toString() ? `?${params.toString()}` : ''

      const [propRes, statRes] = await Promise.all([
        authFetch(`/api/proposals/${qs}`),
        authFetch('/api/proposals/stats')
      ])

      if (propRes && propRes.ok) {
        const data = await propRes.json()
        setProposals(Array.isArray(data) ? data : [])
      }
      if (statRes && statRes.ok) {
        setStats(await statRes.json())
      }
    } catch (e) {
      console.error('Error fetching industry proposals', e)
    } finally {
      setLoading(false)
    }
  }

  const handleCollaborateSubmit = async (collabData) => {
    if (!collaborateProposal) return
    try {
      const res = await authFetch(`/api/proposals/${collaborateProposal.id}/collaborate`, {
        method: 'POST',
        body: JSON.stringify({
          partner_name: user?.organization?.name || 'Tata Steel CSR',
          collaboration_type: collabData.type,
          note: collabData.note,
          contact_person: user?.name || 'CSR Lead',
          contact_email: user?.email || 'csr@tatasteel.com'
        })
      })

      if (res.ok) {
        showToast(`Collaboration invitation sent to ${collaborateProposal.university}!`, 'success')
        setCollaborateProposal(null)
        fetchData()
      }
    } catch (e) {
      showToast('Failed to submit collaboration', 'error')
    }
  }

  const handleFundSubmit = async (fundData) => {
    if (!fundProposal) return
    try {
      const res = await authFetch(`/api/proposals/${fundProposal.id}/fund`, {
        method: 'POST',
        body: JSON.stringify({
          funder_name: user?.organization?.name || 'Tata Steel CSR',
          amount: Number(fundData.amount),
          csr_bucket: fundData.bucket,
          note: fundData.note
        })
      })

      if (res.ok) {
        showToast(`₹${Number(fundData.amount).toLocaleString('en-IN')} CSR Grant allocated successfully!`, 'success')
        setFundProposal(null)
        fetchData()
      }
    } catch (e) {
      showToast('Failed to submit CSR funding', 'error')
    }
  }

  const handleMailSubmit = async (mailData) => {
    if (!mailProposal) return

    // 1. Build the full formatted email body with suggestions and signature
    const suggestionBlock = mailData.suggestions && mailData.suggestions.length > 0
      ? `\n\nKey Improvement Suggestions:\n${mailData.suggestions.map(s => `• ${s}`).join('\n')}`
      : ''
    const signature = `\n\nBest regards,\n${user?.organization?.name || user?.name || 'Industry CSR Partner'}`
    const fullBody = `${mailData.message}${suggestionBlock}${signature}`

    // 2. Open directly in Gmail Web Compose (new tab)
    const gmailUrl = `https://mail.google.com/mail/?view=cm&fs=1&to=${encodeURIComponent(mailProposal.contact_email)}&su=${encodeURIComponent(mailData.subject)}&body=${encodeURIComponent(fullBody)}`
    window.open(gmailUrl, '_blank')

    // 3. Log to backend API
    try {
      await authFetch(`/api/proposals/${mailProposal.id}/feedback`, {
        method: 'POST',
        body: JSON.stringify({
          sender_name: user?.name || 'CSR Review Team',
          sender_email: user?.email || 'csr@tatasteel.com',
          subject: mailData.subject,
          suggestions: mailData.suggestions,
          message: mailData.message
        })
      })
    } catch (e) {
      console.warn('Feedback API logging skipped/failed', e)
    }

    showToast(`Opening Gmail compose for ${mailProposal.contact_email}!`, 'success')
    setMailProposal(null)
  }

  const visibleProposals = Array.isArray(proposals) ? proposals.slice(0, visibleCount) : []
  const hasMore = visibleCount < proposals.length

  return (
    <div className="space-y-6">
      {/* ── Toast Notification ───────────────── */}
      {toast && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-3 bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 px-5 py-3.5 rounded-xl shadow-2xl border border-neutral-700 animate-fade-in-up">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 dark:text-emerald-600 flex-shrink-0" />
          <p className="text-sm font-semibold">{toast.message}</p>
        </div>
      )}

      {/* ── Page Header ───────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h2 className="text-2xl font-extrabold bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 dark:from-emerald-400 dark:via-teal-400 dark:to-cyan-400 bg-clip-text text-transparent">
              Industry & CSR Collaboration Portal
            </h2>
            <span className="bg-emerald-100 dark:bg-emerald-900/40 text-emerald-800 dark:text-emerald-300 text-[11px] font-bold px-2.5 py-0.5 rounded-full border border-emerald-300/40">
              CSR Hub
            </span>
          </div>
          <p className="text-[13.5px] font-medium text-gray-500 dark:text-gray-400 mt-1 max-w-2xl">
            Discover verified University research proposals, co-pilot technological interventions, allocate CSR grants, and mentor academic innovators.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 px-3.5 py-1.5 rounded-xl shadow-sm self-start sm:self-auto">
          <Building2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          <span className="text-xs font-bold text-neutral-800 dark:text-neutral-200">
            {user?.organization?.name || 'Tata Steel CSR Foundation'}
          </span>
        </div>
      </div>

      {/* ── KPI Summary Stat Cards ─────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5">
        {[
          {
            label: 'University Proposals',
            value: loading ? '…' : stats?.total_proposals || proposals.length,
            sub: `${stats?.participating_universities || 7} academic institutes`,
            valueColor: 'from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400',
            iconBg: 'bg-blue-50 dark:bg-blue-900/30',
            icon: <GraduationCap className="w-5 h-5 text-blue-600 dark:text-blue-400" />,
          },
          {
            label: 'Seeking CSR Funding',
            value: loading ? '…' : stats?.seeking_funding || 0,
            sub: 'high impact civic pilots',
            valueColor: 'from-amber-600 to-orange-500',
            iconBg: 'bg-amber-50 dark:bg-amber-900/30',
            icon: <DollarSign className="w-5 h-5 text-amber-600 dark:text-amber-500" />,
          },
          {
            label: 'Active Collaborations',
            value: loading ? '…' : stats?.active_collaborations || 0,
            sub: 'joint industry pilots',
            valueColor: 'from-purple-600 to-indigo-600 dark:from-purple-400 dark:to-indigo-400',
            iconBg: 'bg-purple-50 dark:bg-purple-900/30',
            icon: <Handshake className="w-5 h-5 text-purple-600 dark:text-purple-400" />,
          },
          {
            label: 'CSR Capital Committed',
            value: loading ? '…' : `₹${((stats?.total_capital_committed || 0) / 10000000).toFixed(2)} Cr`,
            sub: 'allocated across Jharkhand',
            valueColor: 'from-emerald-600 to-teal-500 dark:from-emerald-400 dark:to-teal-400',
            iconBg: 'bg-emerald-50 dark:bg-emerald-900/30',
            icon: <Award className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />,
          },
        ].map(({ label, value, sub, valueColor, iconBg, icon }) => (
          <div
            key={label}
            className="bg-white dark:bg-neutral-800 border border-neutral-200/90 dark:border-neutral-700/80 rounded-xl px-4 py-4 flex items-center gap-3.5 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className={`w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0 ${iconBg}`}>
              {icon}
            </div>
            <div className="min-w-0">
              <p className="text-[11px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-0.5">
                {label}
              </p>
              <p className={`text-2xl font-extrabold bg-gradient-to-r ${valueColor} bg-clip-text text-transparent`}>
                {value}
              </p>
              <p className="text-[11px] text-gray-500 dark:text-gray-400 mt-0.5 truncate">{sub}</p>
            </div>
          </div>
        ))}
      </div>

      {/* ── Filter & Search Bar ───────────────── */}
      <div className="bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-xl p-4 shadow-sm space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 items-end">
          {/* Search Box */}
          <div className="sm:col-span-2 flex flex-col gap-1">
            <span className="text-[10.5px] font-bold uppercase tracking-wider text-gray-400 dark:text-gray-500">
              Search Problem or Solution
            </span>
            <div className="relative">
              <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={filters.search}
                onChange={(e) => {
                  setFilters(prev => ({ ...prev, search: e.target.value }))
                  setVisibleCount(9)
                }}
                placeholder="Search keywords (e.g. Telemedicine, Water, IIT ISM)..."
                className="w-full h-9 pl-9 pr-8 text-xs bg-gray-50 dark:bg-neutral-900 border border-gray-200 dark:border-neutral-700 rounded-lg outline-none text-neutral-800 dark:text-white placeholder-gray-400 focus:border-emerald-500 transition-colors"
              />
              {filters.search && (
                <button
                  onClick={() => setFilters(prev => ({ ...prev, search: '' }))}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 cursor-pointer"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>

          {/* Domain Filter */}
          <div className="flex flex-col gap-1">
            <span className="text-[10.5px] font-bold uppercase tracking-wider text-gray-400 dark:text-gray-500">
              Domain
            </span>
            <select
              value={filters.domain}
              onChange={(e) => {
                setFilters(prev => ({ ...prev, domain: e.target.value }))
                setVisibleCount(9)
              }}
              className="h-9 px-2.5 text-xs bg-gray-50 dark:bg-neutral-900 border border-gray-200 dark:border-neutral-700 rounded-lg outline-none text-neutral-800 dark:text-white cursor-pointer focus:border-emerald-500"
            >
              {DOMAIN_OPTIONS.map(d => (
                <option key={d.value} value={d.value}>{d.label}</option>
              ))}
            </select>
          </div>

          {/* Department Filter */}
          <div className="flex flex-col gap-1">
            <span className="text-[10.5px] font-bold uppercase tracking-wider text-gray-400 dark:text-gray-500">
              Department
            </span>
            <select
              value={filters.department}
              onChange={(e) => {
                setFilters(prev => ({ ...prev, department: e.target.value }))
                setVisibleCount(9)
              }}
              className="h-9 px-2.5 text-xs bg-gray-50 dark:bg-neutral-900 border border-gray-200 dark:border-neutral-700 rounded-lg outline-none text-neutral-800 dark:text-white cursor-pointer focus:border-emerald-500"
            >
              {DEPARTMENT_OPTIONS.map(d => (
                <option key={d.value} value={d.value}>{d.label}</option>
              ))}
            </select>
          </div>

          {/* University Filter */}
          <div className="flex flex-col gap-1">
            <span className="text-[10.5px] font-bold uppercase tracking-wider text-gray-400 dark:text-gray-500">
              University / Institute
            </span>
            <select
              value={filters.university}
              onChange={(e) => {
                setFilters(prev => ({ ...prev, university: e.target.value }))
                setVisibleCount(9)
              }}
              className="h-9 px-2.5 text-xs bg-gray-50 dark:bg-neutral-900 border border-gray-200 dark:border-neutral-700 rounded-lg outline-none text-neutral-800 dark:text-white cursor-pointer focus:border-emerald-500"
            >
              {UNIVERSITY_OPTIONS.map(u => (
                <option key={u.value} value={u.value}>{u.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Reset button if filters active */}
        {(filters.search || filters.domain || filters.department || filters.university) && (
          <div className="flex items-center justify-between pt-2 border-t border-gray-100 dark:border-neutral-700/50">
            <span className="text-[11px] text-gray-500">Filters applied</span>
            <button
              onClick={() => setFilters({ search: '', domain: '', department: '', university: '' })}
              className="text-xs font-semibold text-emerald-600 hover:text-emerald-700 flex items-center gap-1 cursor-pointer"
            >
              <X className="w-3.5 h-3.5" /> Clear all filters
            </button>
          </div>
        )}
      </div>

      {/* ── Status Tabs & Results Count ───────── */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex gap-2 flex-wrap">
          {FUNDING_TABS.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => {
                setTabFilter(key)
                setVisibleCount(9)
              }}
              className={`
                text-[12.5px] px-4 py-1.5 rounded-full border transition-all font-semibold cursor-pointer
                ${tabFilter === key
                  ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm'
                  : 'bg-white dark:bg-neutral-800 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-neutral-700 hover:border-gray-300'
                }
              `}
            >
              {label}
            </button>
          ))}
        </div>

        {!loading && (
          <p className="text-[12px] text-gray-500 dark:text-gray-400">
            Showing <span className="font-bold text-neutral-800 dark:text-neutral-200">{visibleProposals.length}</span> of{' '}
            <span className="font-bold text-neutral-800 dark:text-neutral-200">{proposals.length}</span> proposals
          </p>
        )}
      </div>

      {/* ── Proposal Cards Grid ────────────────── */}
      {loading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-5">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-2xl p-5 animate-pulse space-y-4 h-96">
              <div className="h-4 bg-gray-200 dark:bg-neutral-700 rounded w-2/3" />
              <div className="h-3 bg-gray-100 dark:bg-neutral-700/50 rounded w-full" />
              <div className="h-24 bg-gray-100 dark:bg-neutral-700/30 rounded-xl" />
              <div className="h-8 bg-gray-200 dark:bg-neutral-700 rounded" />
            </div>
          ))}
        </div>
      ) : proposals.length === 0 ? (
        <div className="text-center py-20 border-2 border-dashed border-gray-200 dark:border-neutral-700 rounded-2xl bg-white/40 dark:bg-neutral-800/40">
          <GraduationCap className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <h3 className="text-base font-bold text-neutral-800 dark:text-neutral-200">No proposals found</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 max-w-sm mx-auto">
            Try resetting your filters or search terms to browse other university solutions.
          </p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-5 items-stretch">
            {visibleProposals.map((item) => {
              const isFunded = item.funding_status === 'Funded'
              const isPartnered = item.collaboration_status === 'Partnered'

              return (
                <div
                  key={item.id}
                  className="flex flex-col bg-white dark:bg-neutral-800 border border-neutral-200/90 dark:border-neutral-700/80 rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden group hover:border-emerald-500/50"
                >
                  {/* Card Header & Problem Info */}
                  <div className="p-5 pb-3.5 space-y-2.5 flex-1">
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono text-[10px] bg-neutral-100 dark:bg-neutral-700 text-neutral-600 dark:text-neutral-300 font-bold px-2 py-0.5 rounded">
                          {item.id.replace('PROP-', '')}
                        </span>
                        <span className="bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 text-[10.5px] font-bold px-2 py-0.5 rounded-full border border-emerald-200/50">
                          {item.domain}
                        </span>
                      </div>

                      <span
                        className={`text-[10px] uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full border ${
                          isFunded
                            ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300'
                            : item.funding_status === 'Partially Funded'
                            ? 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300'
                            : 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300'
                        }`}
                      >
                        {item.funding_status}
                      </span>
                    </div>

                    {/* Problem Title */}
                    <h3 className="text-base font-bold text-neutral-900 dark:text-white leading-snug group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">
                      {item.problem}
                    </h3>

                    {/* Department & Location Badges */}
                    <div className="flex flex-wrap items-center gap-1.5 text-xs text-neutral-500">
                      <span className="inline-flex items-center gap-1 bg-neutral-100 dark:bg-neutral-700/60 text-neutral-700 dark:text-neutral-300 px-2 py-0.5 rounded-md font-medium text-[11px]">
                        <Building2 className="w-3 h-3 text-neutral-500" />
                        {item.department}
                      </span>
                      <span className="inline-flex items-center gap-1 bg-neutral-100 dark:bg-neutral-700/60 text-neutral-700 dark:text-neutral-300 px-2 py-0.5 rounded-md font-medium text-[11px]">
                        <MapPin className="w-3 h-3 text-neutral-500" />
                        {item.location}
                      </span>
                    </div>

                    {/* Problem Description */}
                    <p className="text-xs text-neutral-600 dark:text-neutral-400 line-clamp-2 leading-relaxed">
                      <span className="font-semibold text-neutral-700 dark:text-neutral-300">Problem: </span>
                      {item.description}
                    </p>

                    {/* ── HIGHLIGHTED PROPOSED SOLUTION BOX ── */}
                    <div className="mt-3 p-3.5 bg-gradient-to-br from-emerald-50/70 via-teal-50/40 to-white dark:from-emerald-950/20 dark:via-teal-950/10 dark:to-neutral-800/90 border border-emerald-200/80 dark:border-emerald-800/40 rounded-xl space-y-2">
                      <div className="flex items-center justify-between gap-1">
                        <div className="flex items-center gap-1.5 text-emerald-800 dark:text-emerald-300 font-bold text-xs">
                          <Sparkles className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                          Proposed Solution
                        </div>
                        <span className="text-[10px] font-bold text-emerald-700 dark:text-emerald-400 bg-emerald-100/80 dark:bg-emerald-900/40 px-2 py-0.5 rounded">
                          {item.trl}
                        </span>
                      </div>

                      <p className="text-[12.5px] font-medium text-neutral-800 dark:text-neutral-200 leading-relaxed line-clamp-3">
                        {item.proposed_solution}
                      </p>

                      {/* University Details */}
                      <div className="pt-2 border-t border-emerald-200/50 dark:border-emerald-800/30 flex items-center justify-between text-xs">
                        <div className="flex items-center gap-1.5 min-w-0">
                          <GraduationCap className="w-4 h-4 text-emerald-700 dark:text-emerald-400 flex-shrink-0" />
                          <span className="font-bold text-neutral-900 dark:text-white truncate">
                            {item.university}
                          </span>
                        </div>
                        <span className="text-[11px] font-semibold text-emerald-800 dark:text-emerald-300">
                          Req: {item.budget_required}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Card Footer with 3 Core Actions */}
                  <div className="p-4 bg-gray-50/80 dark:bg-neutral-850/60 border-t border-neutral-100 dark:border-neutral-700/60 flex flex-col gap-2">
                    {/* Impact snippet */}
                    <p className="text-[11px] text-neutral-500 dark:text-neutral-400 truncate">
                      🎯 <span className="font-semibold text-neutral-700 dark:text-neutral-300">Impact: </span>
                      {item.impact_metrics}
                    </p>

                    {/* 3 Action Buttons */}
                    <div className="grid grid-cols-3 gap-2 pt-1">
                      {/* Button 1: Collaborate */}
                      <button
                        onClick={() => setCollaborateProposal(item)}
                        className={`flex items-center justify-center gap-1 px-2 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                          isPartnered
                            ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300 border border-purple-300/40'
                            : 'bg-white dark:bg-neutral-700 hover:bg-purple-50 dark:hover:bg-purple-950/40 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-700/60 shadow-xs'
                        }`}
                        title="Collaborate with University"
                      >
                        <Handshake className="w-3.5 h-3.5" />
                        <span className="truncate">{isPartnered ? 'Partnered' : 'Collaborate'}</span>
                      </button>

                      {/* Button 2: Fund the solution */}
                      <button
                        onClick={() => setFundProposal(item)}
                        className="flex items-center justify-center gap-1 px-2 py-2 rounded-lg text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm transition-all cursor-pointer"
                        title="Fund this research solution"
                      >
                        <DollarSign className="w-3.5 h-3.5" />
                        <span className="truncate">Fund</span>
                      </button>

                      {/* Button 3: Mail for improvement */}
                      <button
                        onClick={() => setMailProposal(item)}
                        className="flex items-center justify-center gap-1 px-2 py-2 rounded-lg text-xs font-bold bg-white dark:bg-neutral-700 hover:bg-blue-50 dark:hover:bg-blue-950/40 text-blue-600 dark:text-blue-300 border border-blue-200 dark:border-blue-700/60 transition-all cursor-pointer"
                        title="Send feedback or iteration advice"
                      >
                        <Mail className="w-3.5 h-3.5" />
                        <span className="truncate">Mail</span>
                      </button>
                    </div>

                    {/* Prominent View Full Research Report Button */}
                    <button
                      onClick={() => setSelectedProposal(item)}
                      className="w-full mt-1 py-2 px-3 rounded-xl text-xs font-bold bg-neutral-100/80 hover:bg-emerald-50 dark:bg-neutral-800 dark:hover:bg-emerald-950/40 text-neutral-700 dark:text-neutral-200 hover:text-emerald-700 dark:hover:text-emerald-300 border border-neutral-200/80 dark:border-neutral-700 hover:border-emerald-400 dark:hover:border-emerald-700 transition-all flex items-center justify-center gap-2 cursor-pointer shadow-2xs group"
                    >
                      <FileText className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 group-hover:scale-110 transition-transform" />
                      <span>View Full Research Report & Dossier</span>
                      <ArrowRight className="w-3.5 h-3.5 text-gray-400 group-hover:text-emerald-600 group-hover:translate-x-1 transition-all" />
                    </button>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Show More Pagination */}
          {hasMore && (
            <div className="flex flex-col items-center gap-2 pt-4">
              <button
                onClick={() => setVisibleCount(n => n + 6)}
                className="px-6 py-2.5 text-xs font-bold rounded-xl border border-emerald-500 text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-950/30 transition-colors shadow-sm cursor-pointer"
              >
                Load More University Proposals
              </button>
              <p className="text-[11px] text-gray-400">
                {proposals.length - visibleCount} more available
              </p>
            </div>
          )}
        </>
      )}

      {/* ── MODAL 1: COLLABORATE MODAL ────────── */}
      {collaborateProposal && (
        <CollaborateModal
          proposal={collaborateProposal}
          onClose={() => setCollaborateProposal(null)}
          onSubmit={handleCollaborateSubmit}
        />
      )}

      {/* ── MODAL 2: FUND THE SOLUTION MODAL ──── */}
      {fundProposal && (
        <FundSolutionModal
          proposal={fundProposal}
          onClose={() => setFundProposal(null)}
          onSubmit={handleFundSubmit}
        />
      )}

      {/* ── MODAL 3: MAIL FOR IMPROVEMENT MODAL ── */}
      {mailProposal && (
        <ImprovementMailModal
          proposal={mailProposal}
          onClose={() => setMailProposal(null)}
          onSubmit={handleMailSubmit}
        />
      )}

      {/* ── DRAWER: FULL TECHNICAL SPECS ──────── */}
      {selectedProposal && (
        <ProposalDetailDrawer
          proposal={selectedProposal}
          isOpen={!!selectedProposal}
          onClose={() => setSelectedProposal(null)}
          onCollaborate={() => {
            setCollaborateProposal(selectedProposal)
          }}
          onFund={() => {
            setFundProposal(selectedProposal)
          }}
          onMail={() => {
            setMailProposal(selectedProposal)
          }}
        />
      )}
    </div>
  )
}

/* ─────────────────────────────────────────────────────────────────────────────
   MODAL 1: Collaborate Modal
───────────────────────────────────────────────────────────────────────────── */
function CollaborateModal({ proposal, onClose, onSubmit }) {
  const [type, setType] = useState('Joint Pilot Deployment')
  const [note, setNote] = useState('')

  const COLLAB_TYPES = [
    { title: 'Joint Pilot Deployment', desc: 'Provide industrial field sites, infrastructure & operational testing.' },
    { title: 'Technical Mentorship & Lab Access', desc: 'Share corporate R&D lab equipment, compute clusters, & engineering mentors.' },
    { title: 'Talent & Internship Pipeline', desc: 'Sponsor PhD / B.Tech student researchers and create hire pathways.' },
    { title: 'Commercialization & Licensing', desc: 'Jointly file patents and scale product to market.' }
  ]

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({ type, note })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-fade-in">
      <div className="bg-white dark:bg-neutral-850 border border-neutral-200 dark:border-neutral-700 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl space-y-4">
        <div className="px-6 py-4 border-b border-neutral-200 dark:border-neutral-700 flex items-center justify-between bg-neutral-50 dark:bg-neutral-800/50">
          <div className="flex items-center gap-2">
            <Handshake className="w-5 h-5 text-purple-600" />
            <h3 className="text-base font-bold text-neutral-900 dark:text-white">
              Initiate Industry Collaboration
            </h3>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 cursor-pointer">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-2 space-y-4">
          <div className="p-3 bg-purple-50/60 dark:bg-purple-950/30 border border-purple-200/60 dark:border-purple-800/30 rounded-xl text-xs space-y-1">
            <p className="font-bold text-purple-900 dark:text-purple-200">
              University: {proposal.university}
            </p>
            <p className="text-purple-800 dark:text-purple-300 font-medium">
              Lead: {proposal.faculty_lead} ({proposal.contact_email})
            </p>
            <p className="text-neutral-600 dark:text-neutral-400 pt-1">
              Solution: {proposal.proposed_solution}
            </p>
          </div>

          <div>
            <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-2">
              Select Collaboration Mode
            </label>
            <div className="space-y-2">
              {COLLAB_TYPES.map(c => (
                <label
                  key={c.title}
                  onClick={() => setType(c.title)}
                  className={`flex items-start gap-3 p-2.5 rounded-xl border text-xs cursor-pointer transition-colors ${
                    type === c.title
                      ? 'bg-purple-50 dark:bg-purple-950/40 border-purple-500 text-purple-900 dark:text-purple-200'
                      : 'border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-800 text-neutral-700 dark:text-neutral-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="collabType"
                    checked={type === c.title}
                    onChange={() => setType(c.title)}
                    className="mt-0.5 text-purple-600"
                  />
                  <div>
                    <p className="font-bold">{c.title}</p>
                    <p className="text-[11px] text-neutral-500 dark:text-neutral-400">{c.desc}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
              Custom Collaboration Note / Objective
            </label>
            <textarea
              rows={3}
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="e.g. We can provide our Jamshedpur facility for 3-month field telemetry trials and co-fund testing sensors..."
              className="w-full text-xs p-3 bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl outline-none focus:border-purple-500 text-neutral-900 dark:text-white"
            />
          </div>

          <div className="pt-2 pb-4 flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2.5 text-xs font-bold rounded-xl border border-neutral-300 dark:border-neutral-700 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 py-2.5 text-xs font-bold rounded-xl bg-purple-600 hover:bg-purple-700 text-white shadow-md flex items-center justify-center gap-2 cursor-pointer"
            >
              <Send className="w-3.5 h-3.5" /> Send Collaboration Invite
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

/* ─────────────────────────────────────────────────────────────────────────────
   MODAL 2: Fund The Solution Modal
───────────────────────────────────────────────────────────────────────────── */
function FundSolutionModal({ proposal, onClose, onSubmit }) {
  const reqBudget = proposal.budget_num || (
    proposal.budget_required
      ? Number(String(proposal.budget_required).replace(/[^0-9]/g, '')) || 850000
      : 850000
  )
  const [customBudget, setCustomBudget] = useState(reqBudget)
  const [bucket, setBucket] = useState('Healthcare CSR 2026')
  const [note, setNote] = useState('')

  // Fixed based on the original proposal's required budget
  const TIERS = [
    { pct: 25, label: '25% (Phase 1)', val: Math.round(reqBudget * 0.25) },
    { pct: 50, label: '50% (Pilot)', val: Math.round(reqBudget * 0.50) },
    { pct: 75, label: '75% (Full Setup)', val: Math.round(reqBudget * 0.75) },
    { pct: 100, label: '100% (Full Budget)', val: reqBudget },
  ]

  const BUCKETS = [
    'Healthcare CSR 2026',
    'Rural Development & Infrastructure',
    'Clean Water & Sanitation',
    'Tribal Community Empowerment',
    'STEM Innovation & Education'
  ]

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({ amount: Number(customBudget) || 0, bucket, note })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-fade-in">
      <div className="bg-white dark:bg-neutral-850 border border-neutral-200 dark:border-neutral-700 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl space-y-4">
        <div className="px-6 py-4 border-b border-neutral-200 dark:border-neutral-700 flex items-center justify-between bg-neutral-50 dark:bg-neutral-800/50">
          <div className="flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-emerald-600" />
            <h3 className="text-base font-bold text-neutral-900 dark:text-white">
              Allocate CSR Grant / Funding
            </h3>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 cursor-pointer">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-2 space-y-4">
          <div className="p-3.5 bg-emerald-50/70 dark:bg-emerald-950/30 border border-emerald-200/60 dark:border-emerald-800/30 rounded-xl space-y-1.5 text-xs">
            <div className="flex justify-between font-bold text-emerald-900 dark:text-emerald-200">
              <span>{proposal.problem}</span>
              <span>Req: {proposal.budget_required}</span>
            </div>
            <p className="text-emerald-800 dark:text-emerald-300 font-medium">
              Recipient: {proposal.university} ({proposal.faculty_lead})
            </p>
          </div>

          <div>
            <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
              Custom Budget (₹)
            </label>
            <input
              type="number"
              min="0"
              value={customBudget}
              onChange={(e) => setCustomBudget(e.target.value === '' ? '' : Number(e.target.value))}
              placeholder="Enter custom grant budget..."
              className="w-full text-xs p-2.5 bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl outline-none focus:border-emerald-500 text-neutral-900 dark:text-white font-bold"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-2">
              Select Grant Tier
            </label>
            <div className="grid grid-cols-2 gap-2">
              {TIERS.map(t => (
                <button
                  type="button"
                  key={t.pct}
                  onClick={() => setCustomBudget(t.val)}
                  className={`p-2.5 rounded-xl border text-xs font-bold text-left transition-colors cursor-pointer flex flex-col justify-between gap-1 ${
                    Number(customBudget) === t.val
                      ? 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-500 text-emerald-800 dark:text-emerald-200 shadow-xs'
                      : 'border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-800 text-neutral-700 dark:text-neutral-300'
                  }`}
                >
                  <span className="text-[11px] font-semibold">{t.label}</span>
                  <span className="font-mono font-bold text-xs">
                    ₹{t.val.toLocaleString('en-IN')}
                  </span>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
              CSR Fund Category / Bucket
            </label>
            <select
              value={bucket}
              onChange={(e) => setBucket(e.target.value)}
              className="w-full text-xs p-2.5 bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl outline-none text-neutral-900 dark:text-white cursor-pointer"
            >
              {BUCKETS.map(b => (
                <option key={b} value={b}>{b}</option>
              ))}
            </select>
          </div>

          <div className="pt-2 pb-4 flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2.5 text-xs font-bold rounded-xl border border-neutral-300 dark:border-neutral-700 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 py-2.5 text-xs font-bold rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white shadow-md flex items-center justify-center gap-2 cursor-pointer transition-colors"
            >
              <Check className="w-3.5 h-3.5" /> Proceed to University Portal
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

/* ─────────────────────────────────────────────────────────────────────────────
   MODAL 3: Mail For Improvement Modal
───────────────────────────────────────────────────────────────────────────── */
function ImprovementMailModal({ proposal, onClose, onSubmit }) {
  const [subject, setSubject] = useState(`Technical Feedback on "${proposal.problem}" - CSR Review`)
  const [suggestions, setSuggestions] = useState([])
  const [message, setMessage] = useState(
    `Dear ${proposal.faculty_lead},\n\nWe reviewed your proposed solution at ${proposal.university}. Our technical CSR team is highly interested and suggests the following improvements before finalizing deployment sponsorship:`
  )

  const QUICK_CHIPS = [
    'Add Solar / Offline Battery Backup',
    'Improve Cost & Component Efficiency',
    'Include Field Testing in Bokaro / Dhanbad',
    'Provide Open Source APIs & Telemetry',
    'Add Bilingual (Hindi/Santhali) UI'
  ]

  const toggleChip = (chip) => {
    if (suggestions.includes(chip)) {
      setSuggestions(suggestions.filter(s => s !== chip))
    } else {
      setSuggestions([...suggestions, chip])
    }
  }

  const handleOpenGmail = (e) => {
    e.preventDefault()
    onSubmit({ subject, suggestions, message })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-fade-in">
      <div className="bg-white dark:bg-neutral-850 border border-neutral-200 dark:border-neutral-700 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl space-y-4">
        <div className="px-6 py-4 border-b border-neutral-200 dark:border-neutral-700 flex items-center justify-between bg-neutral-50 dark:bg-neutral-800/50">
          <div className="flex items-center gap-2">
            <Mail className="w-5 h-5 text-red-600 dark:text-red-400" />
            <h3 className="text-base font-bold text-neutral-900 dark:text-white">
              Compose Feedback for University
            </h3>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 cursor-pointer">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleOpenGmail} className="px-6 py-2 space-y-3.5">
          <div className="text-xs space-y-1 bg-red-50/60 dark:bg-red-950/30 border border-red-200/60 dark:border-red-800/30 p-3 rounded-xl">
            <p className="font-bold text-neutral-900 dark:text-white flex items-center justify-between">
              <span>Recipient: {proposal.faculty_lead}</span>
              <span className="text-[10.5px] font-semibold text-red-600 dark:text-red-400">Opens in Gmail</span>
            </p>
            <p className="text-gray-600 dark:text-gray-300 font-mono text-[11px]">
              {proposal.contact_email} • {proposal.university}
            </p>
          </div>

          <div>
            <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
              Subject
            </label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="w-full text-xs p-2.5 bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl outline-none focus:border-red-500 text-neutral-900 dark:text-white font-medium"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1.5">
              Quick Suggestion Tags (appended to email)
            </label>
            <div className="flex flex-wrap gap-1.5">
              {QUICK_CHIPS.map(chip => (
                <button
                  type="button"
                  key={chip}
                  onClick={() => toggleChip(chip)}
                  className={`text-[11px] px-2.5 py-1 rounded-full border transition-colors cursor-pointer font-medium ${
                    suggestions.includes(chip)
                      ? 'bg-red-600 text-white border-red-600 shadow-xs'
                      : 'bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-300 border-neutral-200 dark:border-neutral-700 hover:border-neutral-300'
                  }`}
                >
                  {suggestions.includes(chip) ? '✓ ' : '+ '} {chip}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1">
              Feedback Body
            </label>
            <textarea
              rows={4}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="w-full text-xs p-3 bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-xl outline-none focus:border-red-500 text-neutral-900 dark:text-white leading-relaxed font-sans"
            />
          </div>

          <div className="pt-2 pb-4 flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2.5 text-xs font-bold rounded-xl border border-neutral-300 dark:border-neutral-700 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-2 py-2.5 text-xs font-bold rounded-xl bg-red-600 hover:bg-red-700 text-white shadow-md flex items-center justify-center gap-2 cursor-pointer transition-all"
            >
              <ExternalLink className="w-3.5 h-3.5" /> Open in Gmail Compose
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

/* ─────────────────────────────────────────────────────────────────────────────
   DRAWER: Detailed Blueprint & Full Technical Research Dossier
───────────────────────────────────────────────────────────────────────────── */
function ProposalDetailDrawer({ proposal, isOpen, onClose, onCollaborate, onFund, onMail }) {
  if (!isOpen || !proposal) return null

  const report = proposal.research_report || {}
  const summary = proposal.solution_summary || proposal.proposed_solution
  const [activeTab, setActiveTab] = useState('overview')

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-xs transition-opacity animate-fade-in"
        onClick={onClose}
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-4 sm:pl-10">
        <div className="w-screen max-w-2xl sm:max-w-3xl bg-white dark:bg-neutral-900 shadow-2xl border-l border-neutral-200 dark:border-neutral-800 flex flex-col animate-slide-left">
          
          {/* Drawer Header */}
          <div className="p-6 border-b border-neutral-200 dark:border-neutral-800 flex items-start justify-between bg-neutral-50/80 dark:bg-neutral-850/80 backdrop-blur-xs sticky top-0 z-10">
            <div className="space-y-1.5 pr-4">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-xs font-bold bg-neutral-200 dark:bg-neutral-700 px-2.5 py-0.5 rounded text-neutral-700 dark:text-neutral-300">
                  {proposal.id}
                </span>
                <span className="text-xs font-bold text-emerald-700 dark:text-emerald-300 bg-emerald-100/80 dark:bg-emerald-900/40 border border-emerald-300/50 px-2.5 py-0.5 rounded-full">
                  {proposal.trl}
                </span>
                <span className="text-xs font-bold text-blue-700 dark:text-blue-300 bg-blue-100/70 dark:bg-blue-900/30 border border-blue-300/40 px-2.5 py-0.5 rounded-full">
                  {proposal.domain}
                </span>
              </div>
              <h2 className="text-xl font-extrabold text-neutral-900 dark:text-white leading-snug">
                {proposal.problem}
              </h2>
            </div>
            <div className="flex items-center gap-1.5 flex-shrink-0">
              <button
                onClick={() => window.print()}
                title="Print or Export Research Dossier PDF"
                className="p-2 rounded-xl text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-200 hover:bg-neutral-200/60 dark:hover:bg-neutral-800 transition-colors cursor-pointer"
              >
                <Printer className="w-4 h-4" />
              </button>
              <button
                onClick={onClose}
                className="p-2 rounded-xl text-neutral-400 hover:text-neutral-600 hover:bg-neutral-200/60 dark:hover:bg-neutral-800 transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Drawer Navigation Tabs */}
          <div className="px-6 border-b border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 flex gap-4 overflow-x-auto text-xs font-bold scrollbar-none">
            {[
              { id: 'overview', label: 'Executive Summary', icon: <FileText className="w-3.5 h-3.5" /> },
              { id: 'methodology', label: 'Technical Report & Specs', icon: <Cpu className="w-3.5 h-3.5" /> },
              { id: 'budget', label: 'Itemized Budget', icon: <DollarSign className="w-3.5 h-3.5" /> },
            ].map(t => (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id)}
                className={`py-3 flex items-center gap-1.5 border-b-2 transition-colors cursor-pointer whitespace-nowrap ${
                  activeTab === t.id
                    ? 'border-emerald-600 text-emerald-600 dark:border-emerald-400 dark:text-emerald-400 font-extrabold'
                    : 'border-transparent text-gray-500 hover:text-gray-800 dark:hover:text-gray-200'
                }`}
              >
                {t.icon}
                {t.label}
              </button>
            ))}
          </div>

          {/* Drawer Content Body */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            
            {/* University & Lead info banner */}
            <div className="p-4 rounded-2xl bg-gradient-to-br from-emerald-500/10 via-teal-500/5 to-cyan-500/5 dark:from-emerald-950/30 dark:to-neutral-850 border border-emerald-500/20 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center flex-shrink-0 shadow-md">
                  <GraduationCap className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-extrabold text-neutral-900 dark:text-white text-sm">
                    {proposal.university}
                  </h3>
                  <p className="text-xs text-neutral-600 dark:text-neutral-400">
                    Lead: <span className="font-bold text-neutral-800 dark:text-neutral-200">{proposal.faculty_lead}</span>
                  </p>
                </div>
              </div>
              <div className="text-left sm:text-right">
                <p className="text-[11px] font-mono text-emerald-800 dark:text-emerald-300 font-medium">
                  {proposal.contact_email}
                </p>
                <p className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">
                  Direct Institutional Lead
                </p>
              </div>
            </div>

            {/* TAB 1: EXECUTIVE SUMMARY */}
            {activeTab === 'overview' && (
              <div className="space-y-5 animate-fade-in">
                
                {/* 1. Solution Summary Card */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5" />
                      Solution Summary
                    </h4>
                    <span className="text-[11px] font-semibold text-gray-500">
                      Executive Overview
                    </span>
                  </div>
                  <div className="p-4 bg-emerald-50/70 dark:bg-emerald-950/20 border border-emerald-200/80 dark:border-emerald-800/40 rounded-2xl text-xs font-medium text-neutral-900 dark:text-neutral-100 leading-relaxed shadow-xs">
                    {summary}
                  </div>
                </div>

                {/* 2. Detailed Abstract */}
                {report.abstract && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-neutral-500 flex items-center gap-1.5">
                      <BookOpen className="w-3.5 h-3.5 text-neutral-400" />
                      Research Motivation & Abstract
                    </h4>
                    <p className="text-xs text-neutral-700 dark:text-neutral-300 bg-neutral-50 dark:bg-neutral-800/80 p-4 rounded-2xl leading-relaxed border border-neutral-200/70 dark:border-neutral-700/60 font-sans">
                      {report.abstract}
                    </p>
                  </div>
                )}

                {/* 3. Problem Statement & Ground Issue */}
                <div className="space-y-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-neutral-500 flex items-center gap-1.5">
                    <Building2 className="w-3.5 h-3.5 text-neutral-400" />
                    Citizen Grievance & Ground Issue
                  </h4>
                  <div className="p-4 bg-neutral-50 dark:bg-neutral-800/80 rounded-2xl border border-neutral-200/70 dark:border-neutral-700/60 space-y-3">
                    <p className="text-xs text-neutral-700 dark:text-neutral-300 leading-relaxed">
                      {proposal.description}
                    </p>
                    <div className="flex flex-wrap items-center gap-3 pt-2 border-t border-neutral-200/60 dark:border-neutral-700/60 text-xs text-neutral-600 dark:text-neutral-400">
                      <span>📍 Location: <b>{proposal.location}</b></span>
                      <span>🏢 Dept: <b>{proposal.department}</b></span>
                      <span>👥 Reach: <b>{proposal.complaint_count * 120}+ residents</b></span>
                    </div>
                  </div>
                </div>

                {/* 4. KPI Stat Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  <div className="p-4 bg-neutral-50 dark:bg-neutral-800/90 rounded-2xl border border-neutral-200/80 dark:border-neutral-700/80">
                    <p className="text-[10px] uppercase tracking-wider text-neutral-400 font-bold">Grant Required</p>
                    <p className="text-lg font-extrabold text-emerald-600 dark:text-emerald-400 mt-1">{proposal.budget_required}</p>
                    <p className="text-[10px] text-neutral-500 mt-0.5">Hardware & Field Pilot</p>
                  </div>

                  <div className="p-4 bg-neutral-50 dark:bg-neutral-800/90 rounded-2xl border border-neutral-200/80 dark:border-neutral-700/80">
                    <p className="text-[10px] uppercase tracking-wider text-neutral-400 font-bold">Readiness Level</p>
                    <p className="text-sm font-extrabold text-blue-600 dark:text-blue-400 mt-1.5">{proposal.trl}</p>
                    <p className="text-[10px] text-neutral-500 mt-0.5">Tested & Verified</p>
                  </div>

                  <div className="p-4 bg-neutral-50 dark:bg-neutral-800/90 rounded-2xl border border-neutral-200/80 dark:border-neutral-700/80 col-span-2 sm:col-span-1">
                    <p className="text-[10px] uppercase tracking-wider text-neutral-400 font-bold">Target Beneficiaries</p>
                    <p className="text-lg font-extrabold text-purple-600 dark:text-purple-400 mt-1">{proposal.complaint_count * 120}+</p>
                    <p className="text-[10px] text-neutral-500 mt-0.5">Direct civic reach</p>
                  </div>
                </div>

                {/* 5. Key Innovations */}
                {report.key_innovations && report.key_innovations.length > 0 && (
                  <div className="space-y-2.5">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-neutral-500 flex items-center gap-1.5">
                      <Zap className="w-3.5 h-3.5 text-amber-500" />
                      Key Scientific & Technical Innovations
                    </h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {report.key_innovations.map((inn, i) => (
                        <div
                          key={i}
                          className="p-3 bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200/60 dark:border-amber-900/30 rounded-xl text-xs text-neutral-800 dark:text-neutral-200 flex items-start gap-2"
                        >
                          <CheckCircle2 className="w-4 h-4 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
                          <span className="font-medium">{inn}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 6. Impact Metric Goal */}
                <div className="p-4 bg-purple-50/70 dark:bg-purple-950/30 border border-purple-200 dark:border-purple-900/40 rounded-2xl space-y-1">
                  <p className="text-[11px] font-bold text-purple-900 dark:text-purple-300 uppercase tracking-wide flex items-center gap-1.5">
                    <Target className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" />
                    Impact Projection & Societal ROI
                  </p>
                  <p className="text-xs font-medium text-purple-950 dark:text-purple-200 leading-relaxed">
                    {proposal.impact_metrics}
                  </p>
                </div>
              </div>
            )}

            {/* TAB 2: TECHNICAL METHODOLOGY & SPECS */}
            {activeTab === 'methodology' && (
              <div className="space-y-5 animate-fade-in">
                
                {/* Architecture */}
                <div className="space-y-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-neutral-500 flex items-center gap-1.5">
                    <Cpu className="w-3.5 h-3.5 text-emerald-500" />
                    Technical Architecture & Protocol
                  </h4>
                  <div className="p-4 bg-neutral-50 dark:bg-neutral-800/80 rounded-2xl border border-neutral-200/70 dark:border-neutral-700/60 text-xs text-neutral-800 dark:text-neutral-200 leading-relaxed space-y-3 font-mono">
                    <p className="font-sans font-medium text-xs leading-relaxed text-neutral-800 dark:text-neutral-200">
                      {report.technical_architecture || 'Detailed system hardware and algorithmic pipeline engineered by faculty lab.'}
                    </p>
                  </div>
                </div>

                {/* Tech Stack Chips */}
                {report.tech_stack && report.tech_stack.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-neutral-500 flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5 text-blue-500" />
                      Components & Technology Stack
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {report.tech_stack.map((t, idx) => (
                        <span
                          key={idx}
                          className="text-xs font-bold bg-blue-50 dark:bg-blue-950/40 text-blue-800 dark:text-blue-300 border border-blue-200 dark:border-blue-800/40 px-3 py-1.5 rounded-xl shadow-xs flex items-center gap-1.5"
                        >
                          <Cpu className="w-3 h-3 text-blue-600 dark:text-blue-400" />
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Validation Benchmarks */}
                <div className="space-y-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-neutral-500 flex items-center gap-1.5">
                    <FlaskConical className="w-3.5 h-3.5 text-teal-500" />
                    Experimental Testing & Lab Validation Data
                  </h4>
                  <div className="p-4 bg-teal-50/60 dark:bg-teal-950/20 border border-teal-200 dark:border-teal-800/40 rounded-2xl text-xs text-neutral-800 dark:text-neutral-200 leading-relaxed space-y-2">
                    <p className="font-medium">
                      {report.validation_data || 'Tested and verified against institutional benchmarks with >90% precision.'}
                    </p>
                    <div className="flex items-center gap-2 pt-2 border-t border-teal-200/50 dark:border-teal-800/30 text-[11px] text-teal-800 dark:text-teal-300 font-semibold">
                      <ShieldCheck className="w-4 h-4 text-teal-600 dark:text-teal-400" />
                      NABL / Lab Safety & Efficacy Protocol Validated
                    </div>
                  </div>
                </div>

                {/* Jharkhand Ground Rollout */}
                <div className="space-y-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-neutral-500 flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-red-500" />
                    Jharkhand Ground Deployment Plan
                  </h4>
                  <p className="p-4 bg-neutral-50 dark:bg-neutral-800/80 rounded-2xl border border-neutral-200/70 dark:border-neutral-700/60 text-xs text-neutral-800 dark:text-neutral-200 leading-relaxed font-medium">
                    {report.jharkhand_deployment_plan || `Targeted rollout across ${proposal.location} and surrounding rural blocks in 3 phases.`}
                  </p>
                </div>

                {/* IP & Publications */}
                {report.ip_and_publications && (
                  <div className="p-3.5 bg-neutral-100 dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2 text-neutral-700 dark:text-neutral-300">
                      <Award className="w-4 h-4 text-amber-500 flex-shrink-0" />
                      <span className="font-bold">IP & Publication Citation:</span>
                    </div>
                    <span className="text-[11px] font-mono font-semibold text-neutral-900 dark:text-white truncate max-w-xs">
                      {report.ip_and_publications}
                    </span>
                  </div>
                )}
              </div>
            )}

            {/* TAB 3: ITEMIZED BUDGET */}
            {activeTab === 'budget' && (
              <div className="space-y-5 animate-fade-in">
                <div className="p-4 bg-emerald-50/70 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800/40 rounded-2xl flex items-center justify-between">
                  <div>
                    <p className="text-xs font-bold text-emerald-800 dark:text-emerald-300 uppercase tracking-wider">
                      Total CSR Grant Required
                    </p>
                    <p className="text-2xl font-black text-emerald-700 dark:text-emerald-400 mt-0.5">
                      {proposal.budget_required}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-bold px-3 py-1 bg-emerald-600 text-white rounded-full shadow-xs">
                      {proposal.funding_status}
                    </span>
                    <p className="text-[10.5px] text-gray-500 mt-1 font-medium">
                      Committed: ₹{Number(proposal.funds_committed || 0).toLocaleString('en-IN')}
                    </p>
                  </div>
                </div>

                {/* Budget Item Table */}
                <div className="space-y-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-neutral-500 flex items-center gap-1.5">
                    <BarChart3 className="w-3.5 h-3.5 text-neutral-400" />
                    Resource & Capital Allocation Breakdown
                  </h4>
                  <div className="border border-neutral-200 dark:border-neutral-700 rounded-2xl overflow-hidden divide-y divide-neutral-200 dark:divide-neutral-700/60 bg-white dark:bg-neutral-800/60 shadow-xs">
                    {(report.budget_breakdown && report.budget_breakdown.length > 0 ? report.budget_breakdown : [
                      { item: 'Core Hardware & Sensor Fabric', cost: '₹2,00,000' },
                      { item: 'Field Pilot & Community Trial Kits', cost: '₹1,50,000' },
                      { item: 'Training & Community Honorarium', cost: '₹80,000' },
                      { item: 'Cloud Telemetry & Certification', cost: '₹70,000' },
                    ]).map((b, i) => (
                      <div key={i} className="p-3.5 flex items-center justify-between text-xs hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors">
                        <div className="flex items-center gap-2">
                          <span className="w-5 h-5 rounded-full bg-emerald-100 dark:bg-emerald-900/50 text-emerald-800 dark:text-emerald-300 font-bold text-[10px] flex items-center justify-center">
                            {i + 1}
                          </span>
                          <span className="font-semibold text-neutral-800 dark:text-neutral-200">{b.item}</span>
                        </div>
                        <span className="font-mono font-bold text-emerald-700 dark:text-emerald-400">{b.cost}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="p-3.5 bg-blue-50/60 dark:bg-blue-950/20 border border-blue-200/60 dark:border-blue-900/30 rounded-xl text-xs text-blue-900 dark:text-blue-200 flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-blue-600 flex-shrink-0" />
                  <span>All CSR allocations are audited with milestone-based fund release upon university lab verification.</span>
                </div>
              </div>
            )}
          </div>

          {/* Drawer Footer Actions */}
          <div className="p-4 border-t border-neutral-200 dark:border-neutral-800 bg-neutral-50/90 dark:bg-neutral-850/90 backdrop-blur-xs grid grid-cols-3 gap-2.5">
            <button
              onClick={onCollaborate}
              className="py-2.5 px-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-bold shadow-md transition-all flex items-center justify-center gap-1.5 cursor-pointer"
            >
              <Handshake className="w-4 h-4" /> Collaborate
            </button>
            <button
              onClick={onFund}
              className="py-2.5 px-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-md transition-all flex items-center justify-center gap-1.5 cursor-pointer"
            >
              <DollarSign className="w-4 h-4" /> Fund Pilot
            </button>
            <button
              onClick={onMail}
              className="py-2.5 px-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-md transition-all flex items-center justify-center gap-1.5 cursor-pointer"
            >
              <Mail className="w-4 h-4" /> Send Mail
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
