import { useState, useMemo } from 'react'
import useClusters from '../hooks/useClusters'
import { useIssues } from '../context/IssueContext'
import ClusterCard from '../components/ui/ClusterCard'
import FilterBar from '../components/ui/FilterBar'
import { Layers, Clock, Wrench, CheckCircle2 } from 'lucide-react'

const STATUS_FILTERS = [
  { key: 'all', label: 'All' },
  { key: 'pending', label: 'Pending' },
  { key: 'inprogress', label: 'In progress' },
  { key: 'resolved', label: 'Resolved' },
]

const DEFAULT_FILTERS = {
  search: '',
  type: '',
  location: '',
  department: '',
}

const INITIAL_VISIBLE = 9
const LOAD_MORE_COUNT = 9

// ── Skeleton loader card ──────────────────────────────────────────
function SkeletonCard() {
  return (
    <div className="glass-panel p-4 flex flex-col gap-3 animate-pulse">
      <div className="flex gap-3 items-start">
        <div className="w-8 h-8 rounded-lg bg-gray-200 dark:bg-gray-700 flex-shrink-0" />
        <div className="flex-1 space-y-2">
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
          <div className="h-2.5 bg-gray-100 dark:bg-gray-700/50 rounded w-1/2" />
        </div>
      </div>
      <div className="space-y-1.5">
        <div className="h-2 bg-gray-100 dark:bg-gray-700/50 rounded w-full" />
        <div className="h-2 bg-gray-100 dark:bg-gray-700/50 rounded w-5/6" />
      </div>
      <div className="flex gap-2">
        <div className="h-5 bg-gray-100 dark:bg-gray-700/50 rounded-full w-16" />
        <div className="h-5 bg-gray-100 dark:bg-gray-700/50 rounded-full w-20" />
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [statusFilter, setStatusFilter] = useState('pending')
  const [filters, setFilters] = useState(DEFAULT_FILTERS)
  const [visibleCount, setVisibleCount] = useState(INITIAL_VISIBLE)
  const [expandedId, setExpandedId] = useState(null)

  // Context — live issues (with assignment / discard updates)
  const { issues: contextIssues, discarded } = useIssues()

  // API fetch still used for server-side filtering (search, dept)
  const apiFilters = useMemo(() => {
    const f = {}
    if (statusFilter !== 'all') f.status = statusFilter
    if (filters.department) f.department = filters.department
    if (filters.search) f.search = filters.search
    return f
  }, [statusFilter, filters.search, filters.department])

  const { clusters: apiClusters, loading, error } = useClusters(apiFilters)

  // Merge: use context status overrides, exclude discarded
  const clusters = useMemo(() => {
    return apiClusters
      .filter(c => !discarded.has(c.cluster_id))
      .map(c => {
        const live = contextIssues.find(ci => ci.cluster_id === c.cluster_id)
        return live ? { ...c, status: live.status } : c
      })
      // Re-apply status filter after merging live status
      .filter(c => statusFilter === 'all' || c.status === statusFilter)
  }, [apiClusters, contextIssues, discarded, statusFilter])

  // Client-side: complaint type + location exact match
  const filtered = useMemo(() => {
    return clusters.filter((c) => {
      if (filters.type && c.problem.split('—')[0].trim() !== filters.type) return false
      if (filters.location && c.location !== filters.location) return false
      return true
    })
  }, [clusters, filters.type, filters.location])

  // Counts from full context issues (minus discarded)
  const liveClusters = contextIssues.filter(c => !discarded.has(c.cluster_id))
  const counts = useMemo(() => ({
    total:      liveClusters.length,
    pending:    liveClusters.filter(c => c.status === 'pending').length,
    inprogress: liveClusters.filter(c => c.status === 'inprogress').length,
    resolved:   liveClusters.filter(c => c.status === 'resolved').length,
  }), [liveClusters])

  const handleFiltersChange = (newFilters) => {
    setFilters(newFilters)
    setVisibleCount(INITIAL_VISIBLE)
  }

  const handleStatusChange = (status) => {
    setStatusFilter(status)
    setVisibleCount(INITIAL_VISIBLE)
  }

  const visibleClusters = filtered.slice(0, visibleCount)
  const hasMore = visibleCount < filtered.length
  const remaining = filtered.length - visibleCount

  return (
    <div className="space-y-5">

      {/* ── Page header ───────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-2">
        <div className="flex flex-col">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400 bg-clip-text text-transparent">
            Priority Complains
          </h2>
          <p className="text-[13px] font-medium text-gray-500 dark:text-gray-400 mt-1 max-w-2xl">
            Showing critical complaints of people that need immediate attention.
          </p>
        </div>
        <span className="text-[12px] bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 px-3 py-1.5 rounded-full self-start sm:self-auto">
          Last 24 hours
        </span>
      </div>

      {/* ── Summary stat cards ─────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          {
            label: 'Total Clusters',
            value: loading ? '…' : counts.total,
            sub: 'active complaints',
            valueColor: 'from-gray-700 to-gray-500 dark:from-white dark:to-gray-400',
            iconBg: 'bg-gray-100 dark:bg-gray-700',
            icon: <Layers className="w-5 h-5 text-gray-600 dark:text-gray-300" />,
          },
          {
            label: 'Pending',
            value: loading ? '…' : counts.pending,
            sub: 'awaiting action',
            valueColor: 'from-amber-600 to-orange-500',
            iconBg: 'bg-amber-50 dark:bg-amber-900/30',
            icon: <Clock className="w-5 h-5 text-amber-600 dark:text-amber-500" />,
          },
          {
            label: 'In Progress',
            value: loading ? '…' : counts.inprogress,
            sub: 'being handled',
            valueColor: 'from-blue-600 to-indigo-500',
            iconBg: 'bg-blue-50 dark:bg-blue-900/30',
            icon: <Wrench className="w-5 h-5 text-blue-600 dark:text-blue-500" />,
          },
          {
            label: 'Resolved',
            value: loading ? '…' : counts.resolved,
            sub: 'successfully closed',
            valueColor: 'from-green-600 to-emerald-500',
            iconBg: 'bg-green-50 dark:bg-green-900/30',
            icon: <CheckCircle2 className="w-5 h-5 text-green-600 dark:text-green-500" />,
          },
        ].map(({ label, value, sub, valueColor, iconBg, icon }, i) => (
          <div
            key={label}
            className={`glass-panel px-4 py-4 flex items-center gap-3 animate-fade-in-up animate-stagger-${i + 1}`}
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
      <FilterBar filters={filters} onChange={handleFiltersChange} />

      {/* ── Status tabs + results count ───────── */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex gap-2 flex-wrap">
          {STATUS_FILTERS.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => handleStatusChange(key)}
              className={`
                text-[12px] px-3.5 py-1.5 rounded-full border transition-colors
                ${statusFilter === key
                  ? 'bg-indigo-700 text-white border-indigo-700'
                  : 'bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400 border-gray-200 dark:border-gray-700 hover:border-gray-300'
                }
              `}
            >
              {label}
              <span className={`ml-1.5 text-[11px] ${statusFilter === key ? 'opacity-75' : 'text-gray-400'}`}>
                {key === 'all' ? counts.total : counts[key]}
              </span>
            </button>
          ))}
        </div>

        {/* API error banner */}
        {error && (
          <p className="text-[12px] text-red-500 bg-red-50 dark:bg-red-900/20 px-3 py-1.5 rounded-lg border border-red-200 dark:border-red-800">
            ⚠️ Backend error: {error}
          </p>
        )}

        {/* Results count */}
        {!loading && (
          <p className="text-[12px] text-gray-400 dark:text-gray-500">
            Showing{' '}
            <span className="font-medium text-gray-700 dark:text-gray-300">{visibleClusters.length}</span>
            {' '}of{' '}
            <span className="font-medium text-gray-700 dark:text-gray-300">{filtered.length}</span>
            {' '}clusters
          </p>
        )}
      </div>

      {/* ── Cluster cards grid ────────────────── */}
      {loading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 items-start">
          {Array.from({ length: 9 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16 border border-dashed border-gray-200 dark:border-gray-700 rounded-xl">
          <p className="text-sm text-gray-400 dark:text-gray-600">
            No clusters match the current filters.
          </p>
          <button
            onClick={() => { setFilters(DEFAULT_FILTERS); setStatusFilter('all') }}
            className="mt-3 text-[12px] text-indigo-500 hover:underline"
          >
            Clear all filters
          </button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 items-start">
            {visibleClusters.map((cluster, i) => (
              <div key={cluster.cluster_id} className={`animate-fade-in-up animate-stagger-${(i % 5) + 1} flex`}>
                <ClusterCard
                  cluster={cluster}
                  rank={i + 1}
                  expanded={expandedId === cluster.cluster_id}
                  onToggle={() => setExpandedId(prev => prev === cluster.cluster_id ? null : cluster.cluster_id)}
                />
              </div>
            ))}
          </div>

          {/* ── Show more button ──────────────── */}
          {hasMore && (
            <div className="flex flex-col items-center gap-2 pt-2">
              <button
                onClick={() => setVisibleCount((n) => n + LOAD_MORE_COUNT)}
                className="
                  px-6 py-2.5 text-[13px] font-medium rounded-lg
                  border border-indigo-300 dark:border-indigo-700
                  text-indigo-600 dark:text-indigo-400
                  hover:bg-indigo-50 dark:hover:bg-indigo-900/20
                  transition-colors
                "
              >
                Show more
              </button>
              <p className="text-[11px] text-gray-400 dark:text-gray-500">
                {remaining} more cluster{remaining !== 1 ? 's' : ''} remaining
              </p>
            </div>
          )}
        </>
      )}
    </div>
  )
}