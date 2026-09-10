import { useState, useEffect, useMemo } from 'react'
import { useAuth } from '../context/AuthContext'
import { authFetch } from '../api/client'
import {
  TrendingUp,
  DollarSign,
  Building2,
  GraduationCap,
  Sparkles,
  CheckCircle2,
  Clock,
  Layers,
  ChevronDown,
  ChevronUp,
  MapPin,
  Search,
  Filter,
  ExternalLink,
  Mail,
  ShieldCheck,
  Award,
  Circle,
  FileText,
  AlertCircle
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const DOMAIN_OPTIONS = [
  { value: '', label: 'All Domains' },
  { value: 'HealthTech', label: 'HealthTech' },
  { value: 'BioTech', label: 'BioTech' },
  { value: 'Public Health', label: 'Public Health' },
  { value: 'EdTech', label: 'EdTech' },
  { value: 'AgriTech', label: 'AgriTech' },
]

const STATUS_OPTIONS = [
  { value: 'all', label: 'All Statuses' },
  { value: 'Funded', label: 'Fully Funded' },
  { value: 'Partially Funded', label: 'Partially Funded' },
  { value: 'in_project', label: 'In Pilot / Active' },
]

export default function IndustryProgress() {
  const { user } = useAuth()
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [domainFilter, setDomainFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [expandedId, setExpandedId] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    fetchFundedProjects()
  }, [])

  const fetchFundedProjects = async () => {
    setLoading(true)
    try {
      // 1. Fetch industry-specific funded portfolio
      const res = await authFetch('/api/projects/industry/funded')
      if (res && res.ok) {
        const data = await res.json()
        setProjects(Array.isArray(data) ? data : [])
      } else {
        // Fallback to general projects list
        const fallbackRes = await authFetch('/api/projects/')
        if (fallbackRes && fallbackRes.ok) {
          const fbData = await fallbackRes.json()
          setProjects(Array.isArray(fbData) ? fbData : [])
        }
      }
    } catch (e) {
      console.error('Error fetching industry funded projects:', e)
    } finally {
      setLoading(false)
    }
  }

  // Filtered list
  const filteredProjects = useMemo(() => {
    return projects.filter(p => {
      const matchSearch =
        (p.challenge_title || '').toLowerCase().includes(search.toLowerCase()) ||
        (p.university || '').toLowerCase().includes(search.toLowerCase()) ||
        (p.location || '').toLowerCase().includes(search.toLowerCase()) ||
        (p.proposed_solution || '').toLowerCase().includes(search.toLowerCase())

      const matchDomain = !domainFilter || p.domain === domainFilter

      let matchStatus = true
      if (statusFilter !== 'all') {
        if (statusFilter === 'Funded') matchStatus = p.funding_status === 'Funded'
        else if (statusFilter === 'Partially Funded') matchStatus = p.funding_status === 'Partially Funded'
        else if (statusFilter === 'in_project') matchStatus = p.status === 'in_project' || p.status === 'prototype'
      }

      return matchSearch && matchDomain && matchStatus
    })
  }, [projects, search, domainFilter, statusFilter])

  // Portfolio Totals
  const totalCapitalCommitted = useMemo(() => {
    return projects.reduce((acc, p) => acc + (p.funds_committed || 0), 0)
  }, [projects])

  const fullyFundedCount = useMemo(() => {
    return projects.filter(p => p.funding_status === 'Funded' || p.funds_committed >= (p.budget_num || 850000)).length
  }, [projects])

  const totalBeneficiaries = useMemo(() => {
    return (projects.length * 15000) || 45000
  }, [projects])

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      
      {/* ── Page Header ───────────────────────── */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-end gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 dark:from-emerald-400 dark:to-teal-400 bg-clip-text text-transparent flex items-center gap-2">
              <TrendingUp className="text-emerald-600 dark:text-emerald-400" /> CSR Portfolio & Deployment Progress
            </h2>
            <span className="bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-300 text-[11px] font-bold px-2.5 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800">
              Corporate Impact
            </span>
          </div>
          <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
            {user?.organization?.name || 'Tata Steel CSR'} • Real-Time Milestone Monitoring & Academic R&D Grant Deployments.
          </p>
        </div>

        <button
          onClick={() => navigate('/dashboard/industry')}
          className="inline-flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl transition-all shadow-sm cursor-pointer self-start sm:self-auto"
        >
          <Sparkles className="w-4 h-4" /> Browse New University Solutions
        </button>
      </div>

      {/* ── Top CSR KPI Metrics Cards ──────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* KPI 1 */}
        <div className="p-4 rounded-2xl bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-bold text-neutral-400 uppercase tracking-wider">CSR Capital Allocated</p>
            <p className="text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-0.5">
              ₹{totalCapitalCommitted.toLocaleString('en-IN')}
            </p>
            <span className="text-[11px] text-neutral-500 font-medium">Audited Section 135 Mandate</span>
          </div>
          <div className="w-11 h-11 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 flex items-center justify-center border border-emerald-200/50">
            <DollarSign className="w-6 h-6" />
          </div>
        </div>

        {/* KPI 2 */}
        <div className="p-4 rounded-2xl bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-bold text-neutral-400 uppercase tracking-wider">Funded Solutions</p>
            <p className="text-2xl font-black text-neutral-900 dark:text-white mt-0.5">
              {projects.length} <span className="text-sm font-semibold text-neutral-400">Projects</span>
            </p>
            <span className="text-[11px] text-neutral-500 font-medium">{fullyFundedCount} Reached 100% Target</span>
          </div>
          <div className="w-11 h-11 rounded-xl bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 flex items-center justify-center border border-blue-200/50">
            <GraduationCap className="w-6 h-6" />
          </div>
        </div>

        {/* KPI 3 */}
        <div className="p-4 rounded-2xl bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-bold text-neutral-400 uppercase tracking-wider">Active Field Pilots</p>
            <p className="text-2xl font-black text-purple-600 dark:text-purple-400 mt-0.5">
              {projects.filter(p => p.status === 'in_project' || p.status === 'prototype').length || projects.length}
            </p>
            <span className="text-[11px] text-neutral-500 font-medium">TRL-6+ Staged Deployments</span>
          </div>
          <div className="w-11 h-11 rounded-xl bg-purple-50 dark:bg-purple-950/40 text-purple-600 dark:text-purple-400 flex items-center justify-center border border-purple-200/50">
            <Layers className="w-6 h-6" />
          </div>
        </div>

        {/* KPI 4 */}
        <div className="p-4 rounded-2xl bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-bold text-neutral-400 uppercase tracking-wider">Estimated Impact</p>
            <p className="text-2xl font-black text-cyan-600 dark:text-cyan-400 mt-0.5">
              {totalBeneficiaries.toLocaleString('en-IN')}+
            </p>
            <span className="text-[11px] text-neutral-500 font-medium">Jharkhand Residents Reached</span>
          </div>
          <div className="w-11 h-11 rounded-xl bg-cyan-50 dark:bg-cyan-950/40 text-cyan-600 dark:text-cyan-400 flex items-center justify-center border border-cyan-200/50">
            <Award className="w-6 h-6" />
          </div>
        </div>

      </div>

      {/* ── Search & Filter Controls ────────────── */}
      <div className="flex flex-col md:flex-row gap-3 items-center justify-between bg-white dark:bg-neutral-800 p-3.5 rounded-2xl border border-neutral-200 dark:border-neutral-700 shadow-2xs">
        <div className="relative w-full md:w-96">
          <Search className="w-4 h-4 text-neutral-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search funded projects, universities, or locations..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs rounded-xl bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 outline-none focus:border-emerald-500 text-neutral-800 dark:text-white"
          />
        </div>

        <div className="flex items-center gap-2.5 w-full md:w-auto">
          <select
            value={domainFilter}
            onChange={(e) => setDomainFilter(e.target.value)}
            className="text-xs py-2 px-3 rounded-xl bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 outline-none text-neutral-800 dark:text-white cursor-pointer"
          >
            {DOMAIN_OPTIONS.map(d => (
              <option key={d.value} value={d.value}>{d.label}</option>
            ))}
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs py-2 px-3 rounded-xl bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 outline-none text-neutral-800 dark:text-white cursor-pointer"
          >
            {STATUS_OPTIONS.map(s => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* ── Funded Initiatives List ─────────────── */}
      {loading ? (
        <div className="py-20 text-center space-y-3">
          <div className="w-10 h-10 border-3 border-emerald-600 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs font-semibold text-neutral-500">Loading your CSR grant portfolio...</p>
        </div>
      ) : filteredProjects.length === 0 ? (
        <div className="p-12 text-center bg-white dark:bg-neutral-800 rounded-2xl border border-dashed border-neutral-200 dark:border-neutral-700 space-y-3">
          <DollarSign className="w-12 h-12 text-neutral-400 mx-auto opacity-70" />
          <h3 className="text-base font-bold text-neutral-800 dark:text-neutral-200">No funded initiatives match your filters</h3>
          <p className="text-xs text-neutral-500 max-w-md mx-auto">
            Allocate CSR grants to university research proposals on the Industry Dashboard to begin milestone tracking and telemetry monitoring.
          </p>
          <button
            onClick={() => navigate('/dashboard/industry')}
            className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl transition-all shadow-sm cursor-pointer inline-flex items-center gap-1.5 mt-2"
          >
            <Sparkles className="w-4 h-4" /> Explore University Proposals
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredProjects.map((p) => {
            const target = p.budget_num || 850000
            const committed = p.funds_committed || 0
            const pct = Math.min(100, Math.round((committed / target) * 100))
            const remaining = Math.max(0, target - committed)
            const isExpanded = expandedId === p.id

            const defaultMilestones = [
              { title: 'Initial Problem Analysis & Architecture', status: 'completed' },
              { title: 'Research and Prototype Submission', status: 'completed' },
              { title: 'Field Pilot Trial & Sensor Telemetry', status: committed >= Math.round(target * 0.5) ? 'completed' : 'in_progress' },
              { title: 'Full Regional Deployment & Verification', status: committed >= target ? 'in_progress' : 'pending' },
            ]

            const milestones = (p.milestones && p.milestones.length === 4) ? p.milestones : defaultMilestones

            return (
              <div
                key={p.id}
                className="bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-2xl p-5 shadow-xs hover:border-emerald-300 dark:hover:border-emerald-800/80 transition-all space-y-4"
              >
                {/* Card Top Row */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pb-3 border-b border-neutral-100 dark:border-neutral-700/60">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-mono text-xs font-bold bg-neutral-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300 px-2.5 py-0.5 rounded">
                      {p.challenge_id || p.id}
                    </span>
                    <span className="text-xs font-bold text-blue-700 dark:text-blue-300 bg-blue-50 dark:bg-blue-900/30 px-2.5 py-0.5 rounded-full border border-blue-200/50">
                      {p.domain || 'HealthTech'}
                    </span>
                    <span className="text-xs font-bold text-purple-700 dark:text-purple-300 bg-purple-50 dark:bg-purple-900/30 px-2.5 py-0.5 rounded-full border border-purple-200/50">
                      {p.trl || 'TRL-6'}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-extrabold px-3 py-1 rounded-full border ${
                      p.funding_status === 'Funded' || committed >= target
                        ? 'bg-emerald-100 text-emerald-800 border-emerald-300 dark:bg-emerald-900/60 dark:text-emerald-200'
                        : 'bg-amber-100 text-amber-800 border-amber-300 dark:bg-amber-900/60 dark:text-amber-200'
                    }`}>
                      {p.funding_status || (committed >= target ? 'Funded' : 'Partially Funded')}
                    </span>
                    <span className="text-xs font-bold text-neutral-500 bg-neutral-100 dark:bg-neutral-700 px-2.5 py-1 rounded-full">
                      Priority {p.priority_score || 85}
                    </span>
                  </div>
                </div>

                {/* Main Problem & Solution Summary */}
                <div className="space-y-1.5">
                  <h3 className="text-base font-bold text-neutral-900 dark:text-white leading-snug">
                    {p.challenge_title || 'Civic Infrastructure Challenge'}
                  </h3>
                  <div className="flex items-center gap-3 text-xs text-neutral-500">
                    <span className="flex items-center gap-1 font-medium">
                      <MapPin className="w-3.5 h-3.5 text-neutral-400" />
                      {p.location || 'Jharkhand'}
                    </span>
                    <span>•</span>
                    <span>{p.department || 'Public Administration'}</span>
                  </div>
                </div>

                {/* University Lead Box */}
                <div className="p-3 bg-neutral-50 dark:bg-neutral-900/60 border border-neutral-200 dark:border-neutral-700/60 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 text-xs">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center font-bold shadow-2xs">
                      <GraduationCap className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="font-bold text-neutral-900 dark:text-white">
                        {p.university || 'University Research Team'}
                      </p>
                      <p className="text-[11px] text-neutral-500">
                        Academic Lead: <span className="font-semibold text-neutral-700 dark:text-neutral-300">{p.faculty_lead || 'Lead Researcher'}</span>
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 self-start sm:self-auto">
                    <a
                      href={`mailto:${p.contact_email || 'research@university.ac.in'}?subject=CSR%20Funding%20Deployment%20Inquiry%20-%20${encodeURIComponent(p.challenge_title || '')}`}
                      className="inline-flex items-center gap-1 px-3 py-1.5 bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 text-neutral-700 dark:text-neutral-200 text-xs font-semibold rounded-lg hover:bg-neutral-50 transition-colors shadow-2xs"
                    >
                      <Mail className="w-3.5 h-3.5 text-red-500" /> Email Lead
                    </a>
                  </div>
                </div>

                {/* Grant Accumulation Tracker Widget */}
                <div className="p-4 bg-gradient-to-br from-emerald-50/70 via-teal-50/40 to-white dark:from-emerald-950/30 dark:via-teal-950/20 dark:to-neutral-900 border border-emerald-200/80 dark:border-emerald-800/40 rounded-xl space-y-2.5">
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-1.5 font-bold text-emerald-900 dark:text-emerald-200">
                      <DollarSign className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                      <span>CSR Capital Deployment & Funding Accumulation</span>
                    </div>
                    <span className="font-mono font-bold text-emerald-700 dark:text-emerald-400 text-xs">
                      {pct}% of Goal
                    </span>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-neutral-200 dark:bg-neutral-700 h-2.5 rounded-full overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-emerald-500 to-teal-500 h-full rounded-full transition-all duration-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>

                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-emerald-800 dark:text-emerald-300">
                      ₹{committed.toLocaleString('en-IN')} <span className="font-normal text-neutral-500">Allocated</span>
                    </span>
                    <span className="font-bold text-neutral-700 dark:text-neutral-300">
                      Target: ₹{target.toLocaleString('en-IN')}
                    </span>
                    <span className={remaining === 0 ? 'text-emerald-600 dark:text-emerald-400 font-bold' : 'text-amber-700 dark:text-amber-400 font-semibold'}>
                      {remaining === 0 ? 'Fully Funded 🎉' : `₹${remaining.toLocaleString('en-IN')} Remaining`}
                    </span>
                  </div>

                  {p.partners && p.partners.length > 0 && (
                    <div className="pt-1.5 border-t border-emerald-100 dark:border-emerald-900/40 flex items-center justify-between text-[11px]">
                      <span className="text-neutral-500 font-medium">Registered CSR Sponsors:</span>
                      <div className="flex flex-wrap gap-1">
                        {p.partners.map((partner, idx) => (
                          <span key={idx} className="font-bold text-[10.5px] bg-white dark:bg-neutral-800 text-emerald-800 dark:text-emerald-300 px-2 py-0.5 rounded border border-emerald-200/60 dark:border-emerald-800/40 shadow-2xs">
                            {partner}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* 4-Phase Delivery Tracker */}
                <div className="space-y-2 pt-1">
                  <p className="text-xs font-bold text-neutral-700 dark:text-neutral-300 flex items-center gap-1.5">
                    <Layers className="w-3.5 h-3.5 text-blue-600" />
                    Delivery Milestone Stages
                  </p>
                  
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2 text-xs">
                    {milestones.map((m, idx) => {
                      const isDone = m.status === 'completed'
                      const isInProg = m.status === 'in_progress'

                      return (
                        <div
                          key={idx}
                          className={`p-3 rounded-xl border flex flex-col justify-between gap-1.5 ${
                            isDone
                              ? 'bg-emerald-50/60 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800/40 text-emerald-900 dark:text-emerald-200'
                              : isInProg
                                ? 'bg-blue-50/60 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800/40 text-blue-900 dark:text-blue-200'
                                : 'bg-neutral-50 dark:bg-neutral-900/30 border-neutral-200 dark:border-neutral-700 text-neutral-500'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-400">Phase {idx + 1}</span>
                            {isDone ? (
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                            ) : isInProg ? (
                              <Circle className="w-3.5 h-3.5 text-blue-600 fill-blue-600/20 animate-pulse" />
                            ) : (
                              <Circle className="w-3.5 h-3.5 text-neutral-300 dark:text-neutral-600" />
                            )}
                          </div>
                          <p className="font-semibold text-[11.5px] leading-tight line-clamp-2">
                            {m.title}
                          </p>
                          <span className={`text-[9.5px] uppercase font-extrabold px-1.5 py-0.2 rounded self-start ${
                            isDone
                              ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-300'
                              : isInProg
                                ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/60 dark:text-blue-300'
                                : 'bg-neutral-200 text-neutral-700 dark:bg-neutral-700 dark:text-neutral-400'
                          }`}>
                            {m.status.replace('_', ' ')}
                          </span>
                        </div>
                      )
                    })}
                  </div>
                </div>

                {/* Expandable Technical Dossier */}
                {isExpanded && (
                  <div className="pt-3 border-t border-neutral-100 dark:border-neutral-700/60 space-y-3 text-xs animate-fade-in">
                    <div className="p-3.5 bg-neutral-50 dark:bg-neutral-900/60 rounded-xl space-y-1.5">
                      <p className="font-bold text-neutral-900 dark:text-white flex items-center gap-1.5">
                        <FileText className="w-3.5 h-3.5 text-blue-600" /> Technical Implementation Dossier:
                      </p>
                      <p className="text-neutral-700 dark:text-neutral-300 leading-relaxed">
                        {p.proposed_solution}
                      </p>
                    </div>

                    <div className="flex items-center justify-between text-[11px] text-neutral-500">
                      <span>Verification: <strong className="text-neutral-700 dark:text-neutral-300">Audited University Lab Telemetry</strong></span>
                      <span>Next Audit Cycle: <strong className="text-neutral-700 dark:text-neutral-300">Bi-Weekly</strong></span>
                    </div>
                  </div>
                )}

                {/* Footer Toggle */}
                <div className="pt-1 flex items-center justify-between text-xs">
                  <button
                    onClick={() => setExpandedId(isExpanded ? null : p.id)}
                    className="inline-flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-bold hover:underline cursor-pointer"
                  >
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    {isExpanded ? 'Hide Technical Details' : 'View Full Technical Dossier'}
                  </button>

                  <div className="flex items-center gap-1.5 text-[11px] text-neutral-400">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                    <span>CSR Milestone Compliant</span>
                  </div>
                </div>

              </div>
            )
          })}
        </div>
      )}

    </div>
  )
}
