import { useState, useEffect, useMemo } from 'react'
import { Layers, Clock, CheckCircle2, Target } from 'lucide-react'
import FilterBar from '../components/ui/FilterBar'
import ChallengeCard from '../components/ui/ChallengeCard'
import ChallengeDetailDrawer from '../components/ui/ChallengeDetailDrawer'
import RoutingModal from '../components/ui/RoutingModal'

const STATUS_FILTERS = [
  { key: 'all', label: 'All Active' },
  { key: 'pending_verification', label: 'Pending Verification' },
  { key: 'verified', label: 'Verified' },
  { key: 'matches_suggested', label: 'Matches Suggested' },
  { key: 'ready_for_routing', label: 'Ready for Routing' },
]

const DEFAULT_FILTERS = {
  search: '',
  domain: '',
  district: '',
  priority: '',
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
  const [selectedChallenge, setSelectedChallenge] = useState(null)
  const [routingChallenge, setRoutingChallenge] = useState(null)
  
  const [challenges, setChallenges] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [statusFilter, filters])

  const fetchData = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (statusFilter !== 'all') params.append('status', statusFilter)
      if (filters.search) params.append('search', filters.search)
      if (filters.domain) params.append('domain', filters.domain)
      if (filters.district) params.append('district', filters.district)
      if (filters.priority) params.append('priority', filters.priority)

      const qs = params.toString() ? `?${params.toString()}` : ''

      const [chRes, stRes] = await Promise.all([
        fetch(`/api/challenges/${qs}`).catch(() => fetch(`http://localhost:8000/api/challenges/${qs}`)),
        fetch('/api/stats/overview').catch(() => fetch('http://localhost:8000/api/stats/overview'))
      ])
      if (chRes && chRes.ok) {
        const data = await chRes.json()
        setChallenges(Array.isArray(data) ? data : [])
      }
      if (stRes && stRes.ok) setStats(await stRes.json())
    } catch (e) {
      console.error("Error fetching gov data", e)
    } finally {
      setLoading(false)
    }
  }

  const filtered = useMemo(() => {
    const list = Array.isArray(challenges) ? challenges : []
    return list.filter((c) => {
      if (!c) return false;
      // Exclude challenges that have left the active dashboard
      if (['routed', 'in_project', 'resolved'].includes(c.status)) return false;
      return true
    }).sort((a, b) => (b?.priority_score || 0) - (a?.priority_score || 0))
  }, [challenges])

  const counts = useMemo(() => {
    const list = Array.isArray(challenges) ? challenges : []
    const active = list.filter(c => c && !['routed', 'in_project', 'resolved'].includes(c.status));
    
    // Group counts dynamically
    const dynamicCounts = {
      total: active.length,
      pending_verification: 0,
      verified: 0,
      matches_suggested: 0,
      ready_for_routing: 0,
    };
    
    active.forEach(c => {
      if (c && dynamicCounts[c.status] !== undefined) {
        dynamicCounts[c.status]++;
      }
    });
    
    // Also add some meta stats for the top KPI row
    dynamicCounts.high_priority = active.filter(c => c && (c.priority_score || 0) >= 85).length;
    return dynamicCounts;
  }, [challenges])

  const visibleClusters = filtered.slice(0, visibleCount)
  const hasMore = visibleCount < filtered.length
  const remaining = filtered.length - visibleCount

  const handleAction = async (challenge) => {
    if (challenge.status === 'pending_verification') {
      try {
        const res = await fetch(`http://localhost:8000/api/challenges/${challenge.id}/verify`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ verified: true })
        })
        if (res.ok) {
          fetchData()
          // Re-select if drawer is open to update status visually
          if (selectedChallenge?.id === challenge.id) {
             const updated = await res.json();
             setSelectedChallenge(updated);
          }
        }
      } catch (e) {
        console.error(e)
      }
    } else {
      // It's verified or ready to route, open routing modal
      setRoutingChallenge(challenge)
    }
  }

  const handleConfirmRoute = async (id, orgId, note) => {
    try {
        const res = await fetch(`http://localhost:8000/api/challenges/${id}/route`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ org_id: orgId, note })
        });
        if (res.ok) {
            setRoutingChallenge(null);
            setSelectedChallenge(null); // Close drawer if open
            fetchData();
        }
    } catch (e) {
        console.error("Failed to route", e);
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
            label: 'Active Challenges',
            value: loading ? '…' : counts.total,
            sub: `${counts.pending_verification} pending verification`,
            valueColor: 'from-gray-700 to-gray-500 dark:from-white dark:to-gray-400',
            iconBg: 'bg-gray-100 dark:bg-gray-700',
            icon: <Layers className="w-5 h-5 text-gray-600 dark:text-gray-300" />,
          },
          {
            label: 'Pending Verification',
            value: loading ? '…' : counts.pending_verification,
            sub: 'requires review',
            valueColor: 'from-amber-600 to-orange-500',
            iconBg: 'bg-amber-50 dark:bg-amber-900/30',
            icon: <Clock className="w-5 h-5 text-amber-600 dark:text-amber-500" />,
          },
          {
            label: 'High Priority',
            value: loading ? '…' : counts.high_priority,
            sub: 'critical issues',
            valueColor: 'from-red-600 to-rose-500',
            iconBg: 'bg-red-50 dark:bg-red-900/30',
            icon: <Target className="w-5 h-5 text-red-600 dark:text-red-500" />,
          },
          {
            label: 'Ready for Routing',
            value: loading ? '…' : counts.ready_for_routing,
            sub: 'matches available',
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
                expanded={false} // Drawer replaces expansion
                onToggle={() => setSelectedChallenge(challenge)}
                onVerify={() => handleAction(challenge)}
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

      {/* ── Detail Drawer ─────────────────────── */}
      <ChallengeDetailDrawer
        challenge={selectedChallenge}
        isOpen={!!selectedChallenge}
        onClose={() => setSelectedChallenge(null)}
        onRoute={handleAction}
      />

      {/* ── Routing Modal ─────────────────────── */}
      <RoutingModal 
        challenge={routingChallenge}
        isOpen={!!routingChallenge}
        onClose={() => setRoutingChallenge(null)}
        onConfirm={handleConfirmRoute}
      />
    </div>
  )
}
