import { useState, useEffect, useMemo } from 'react'
import { Layers, Clock, CheckCircle2, Target } from 'lucide-react'
import FilterBar from '../components/ui/FilterBar'
import ChallengeCard from '../components/ui/ChallengeCard'

const STATUS_FILTERS = [
  { key: 'all', label: 'All' },
  { key: 'pending', label: 'Pending Verification' },
  { key: 'verified', label: 'Verified & Routing' },
  { key: 'in_project', label: 'In Project' },
]

const DEFAULT_FILTERS = {
  search: '',
  type: '',
  location: '',
  department: '',
}

const INITIAL_VISIBLE = 9
const LOAD_MORE_COUNT = 9

function SkeletonCard() {
  return (
    <div className="glass-panel p-4 flex flex-col gap-3 animate-pulse border border-neutral-200 dark:border-neutral-700 rounded-xl h-48">
      <div className="flex gap-3 items-start">
        <div className="w-8 h-8 rounded-lg bg-gray-200 dark:bg-gray-700 flex-shrink-0" />
        <div className="flex-1 space-y-2">
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
          <div className="h-2.5 bg-gray-100 dark:bg-gray-700/50 rounded w-1/2" />
        </div>
      </div>
      <div className="space-y-1.5 mt-4">
        <div className="h-2 bg-gray-100 dark:bg-gray-700/50 rounded w-full" />
        <div className="h-2 bg-gray-100 dark:bg-gray-700/50 rounded w-5/6" />
      </div>
    </div>
  )
}

export default function GovDashboard() {
  const [statusFilter, setStatusFilter] = useState('all')
  const [filters, setFilters] = useState(DEFAULT_FILTERS)
  const [visibleCount, setVisibleCount] = useState(INITIAL_VISIBLE)
  const [expandedId, setExpandedId] = useState(null)
  
  const [challenges, setChallenges] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [chRes, stRes] = await Promise.all([
        fetch('http://localhost:8000/api/challenges/'),
        fetch('http://localhost:8000/api/stats/overview')
      ])
      if (chRes.ok) setChallenges(await chRes.json())
      if (stRes.ok) setStats(await stRes.json())
    } catch (e) {
      console.error("Error fetching gov data", e)
    } finally {
      setLoading(false)
    }
  }

  const filtered = useMemo(() => {
    return challenges.filter((c) => {
      if (statusFilter !== 'all' && c.status !== statusFilter) return false
      
      // We don't have perfect domain mapping to old filters, but we can do simple search
      if (filters.search) {
        const term = filters.search.toLowerCase()
        if (!c.title.toLowerCase().includes(term) && !c.description.toLowerCase().includes(term)) return false
      }
      if (filters.location && !c.location.includes(filters.location)) return false
      if (filters.department && c.department !== filters.department) return false
      
      return true
    })
  }, [challenges, statusFilter, filters])

  const counts = useMemo(() => {
    if (!stats) return { total: 0, pending: 0, verified: 0, in_project: 0 }
    return {
      total: stats.total_challenges,
      pending: stats.pending_verification,
      verified: challenges.filter(c => c.status === 'verified' || c.status === 'matched').length,
      in_project: stats.in_project + stats.resolved
    }
  }, [stats, challenges])

  const visibleClusters = filtered.slice(0, visibleCount)
  const hasMore = visibleCount < filtered.length
  const remaining = filtered.length - visibleCount

  const handleVerifyRoute = async (id) => {
    try {
      const res = await fetch(`http://localhost:8000/api/challenges/${id}/verify`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ verified: true })
      })
      if (res.ok) {
        fetchData()
      }
    } catch (e) {
      console.error(e)
    }
  }

  return (
    <div className="space-y-5">
      {/* ── Page header ───────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-2">
        <div className="flex flex-col">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400 bg-clip-text text-transparent">
            Government Intelligence Dashboard
          </h2>
          <p className="text-[13px] font-medium text-gray-500 dark:text-gray-400 mt-1 max-w-2xl">
            Review civic challenges and route them to university and industry partners.
          </p>
        </div>
        <span className="text-[12px] bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 px-3 py-1.5 rounded-full self-start sm:self-auto">
          Statewide
        </span>
      </div>

      {/* ── Summary stat cards ─────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          {
            label: 'Total Challenges',
            value: loading ? '…' : counts.total,
            sub: 'active civic issues',
            valueColor: 'from-gray-700 to-gray-500 dark:from-white dark:to-gray-400',
            iconBg: 'bg-gray-100 dark:bg-gray-700',
            icon: <Layers className="w-5 h-5 text-gray-600 dark:text-gray-300" />,
          },
          {
            label: 'Pending',
            value: loading ? '…' : counts.pending,
            sub: 'needs verification',
            valueColor: 'from-amber-600 to-orange-500',
            iconBg: 'bg-amber-50 dark:bg-amber-900/30',
            icon: <Clock className="w-5 h-5 text-amber-600 dark:text-amber-500" />,
          },
          {
            label: 'Verified & Routing',
            value: loading ? '…' : counts.verified,
            sub: 'waiting for partner',
            valueColor: 'from-blue-600 to-indigo-500',
            iconBg: 'bg-blue-50 dark:bg-blue-900/30',
            icon: <Target className="w-5 h-5 text-blue-600 dark:text-blue-500" />,
          },
          {
            label: 'Active Projects',
            value: loading ? '…' : counts.in_project,
            sub: 'solutions in progress',
            valueColor: 'from-green-600 to-emerald-500',
            iconBg: 'bg-green-50 dark:bg-green-900/30',
            icon: <CheckCircle2 className="w-5 h-5 text-green-600 dark:text-green-500" />,
          },
        ].map(({ label, value, sub, valueColor, iconBg, icon }, i) => (
          <div
            key={label}
            className={`bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-xl px-4 py-4 flex items-center gap-3 animate-fade-in-up shadow-sm`}
          >
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-xl flex-shrink-0 ${iconBg}`}>
              {icon}
            </div>
            <div className="min-w-0">
              <p className="text-[10.5px] font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wide mb-0.5">{label}</p>
              <p className={`text-2xl font-bold bg-gradient-to-r ${valueColor} bg-clip-text text-transparent`}>{value}</p>
              <p className="text-[10px] text-gray-400 mt-0.5 truncate">{sub}</p>
            </div>
          </div>
        ))}
      </div>

      {/* ── Filter bar ────────────────────────── */}
      <FilterBar filters={filters} onChange={f => { setFilters(f); setVisibleCount(INITIAL_VISIBLE) }} />

      {/* ── Status tabs + results count ───────── */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex gap-2 flex-wrap">
          {STATUS_FILTERS.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => { setStatusFilter(key); setVisibleCount(INITIAL_VISIBLE) }}
              className={`
                text-[12px] px-3.5 py-1.5 rounded-full border transition-colors font-medium
                ${statusFilter === key
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-400 border-gray-200 dark:border-gray-700 hover:border-gray-300'
                }
              `}
            >
              {label}
              <span className={`ml-1.5 text-[11px] ${statusFilter === key ? 'opacity-90 text-blue-100' : 'text-gray-400'}`}>
                {key === 'all' ? counts.total : counts[key]}
              </span>
            </button>
          ))}
        </div>

        {/* Results count */}
        {!loading && (
          <p className="text-[12px] text-gray-500 dark:text-gray-400">
            Showing{' '}
            <span className="font-medium text-gray-800 dark:text-gray-200">{visibleClusters.length}</span>
            {' '}of{' '}
            <span className="font-medium text-gray-800 dark:text-gray-200">{filtered.length}</span>
            {' '}challenges
          </p>
        )}
      </div>

      {/* ── Challenge cards grid ────────────────── */}
      {loading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 items-start">
          {Array.from({ length: 9 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16 border border-dashed border-gray-200 dark:border-gray-700 rounded-xl bg-white/50 dark:bg-neutral-800/50">
          <p className="text-sm text-gray-400 dark:text-gray-500">
            No challenges match the current filters.
          </p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 items-start">
            {visibleClusters.map((challenge, i) => (
              <ChallengeCard
                key={challenge.id}
                challenge={challenge}
                rank={i + 1}
                expanded={expandedId === challenge.id}
                onToggle={() => setExpandedId(prev => prev === challenge.id ? null : challenge.id)}
                onVerify={() => handleVerifyRoute(challenge.id)}
              />
            ))}
          </div>

          {/* ── Show more button ──────────────── */}
          {hasMore && (
            <div className="flex flex-col items-center gap-2 pt-2">
              <button
                onClick={() => setVisibleCount((n) => n + LOAD_MORE_COUNT)}
                className="
                  px-6 py-2.5 text-[13px] font-bold rounded-lg
                  border border-blue-200 dark:border-blue-900/50
                  text-blue-600 dark:text-blue-400
                  hover:bg-blue-50 dark:hover:bg-blue-900/20
                  transition-colors
                "
              >
                Show more
              </button>
              <p className="text-[11px] text-gray-400 dark:text-gray-500">
                {remaining} more challenges remaining
              </p>
            </div>
          )}
        </>
      )}
    </div>
  )
}
