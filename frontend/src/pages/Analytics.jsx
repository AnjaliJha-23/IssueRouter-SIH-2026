import { useState, useEffect, useMemo, useRef } from 'react'
import { authFetch } from '../api/client'
import { AlertTriangle, Zap, Clock, BarChart3, TrendingUp, RefreshCw } from 'lucide-react'

const GRID_COLOR = 'rgba(99,102,241,0.06)'
const TICK_COLOR = '#9ca3af'
const DARK_TOOLTIP = {
    backgroundColor: 'rgba(15,15,30,0.92)',
    titleColor: '#e2e8f0',
    bodyColor: '#94a3b8',
    borderColor: 'rgba(99,102,241,0.3)',
    borderWidth: 1,
    padding: 12,
    cornerRadius: 10,
    titleFont: { size: 12, weight: 'bold' },
    bodyFont: { size: 12 },
    displayColors: true,
    boxPadding: 4,
}

function ChartCard({ title, sub, badge, children, className = '' }) {
    return (
        <div className={`glass-panel flex flex-col gap-3 p-5 ${className}`}>
            <div className="flex items-start justify-between gap-3">
                <div>
                    <p className="text-[14px] font-bold text-gray-800 dark:text-gray-100">{title}</p>
                    {sub && <p className="text-[11.5px] text-gray-400 dark:text-gray-500 mt-0.5">{sub}</p>}
                </div>
                {badge && (
                    <span className="flex-shrink-0 text-[10.5px] font-semibold px-2.5 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-300 border border-indigo-200/60 dark:border-indigo-700/40">
                        {badge}
                    </span>
                )}
            </div>
            {children}
        </div>
    )
}

function SkeletonChart({ height = 240 }) {
    return (
        <div className="w-full rounded-xl bg-gray-100 dark:bg-gray-800 animate-pulse" style={{ height }} />
    )
}

// ── Velocity chart ─────────────────────────────────────────────
function VelocityChart({ data }) {
    const ref = useRef(null)
    const instance = useRef(null)

    useEffect(() => {
        if (!window.Chart || !ref.current || !data) return
        instance.current?.destroy()
        const ctx = ref.current.getContext('2d')
        const gradient = ctx.createLinearGradient(0, 0, 0, 280)
        gradient.addColorStop(0,   'rgba(99,102,241,0.22)')
        gradient.addColorStop(0.7, 'rgba(99,102,241,0.04)')
        gradient.addColorStop(1,   'rgba(99,102,241,0)')
        instance.current = new window.Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Complaints filed',
                        data: data.complaints,
                        borderColor: '#6366f1',
                        backgroundColor: gradient,
                        borderWidth: 2.5,
                        pointRadius: 5,
                        pointHoverRadius: 8,
                        pointBackgroundColor: '#6366f1',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        tension: 0.45,
                        fill: true,
                    },
                    {
                        label: '7-day average',
                        data: data.avg_line,
                        borderColor: 'rgba(167,139,250,0.55)',
                        borderWidth: 1.5,
                        borderDash: [5, 4],
                        pointRadius: 0,
                        fill: false,
                    },
                ],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                animation: { duration: 900, easing: 'easeInOutQuart' },
                interaction: { mode: 'index', intersect: false },
                plugins: { legend: { display: false }, tooltip: { ...DARK_TOOLTIP } },
                scales: {
                    x: { grid: { color: GRID_COLOR }, ticks: { color: TICK_COLOR, font: { size: 11 } }, border: { display: false } },
                    y: { grid: { color: GRID_COLOR }, ticks: { color: TICK_COLOR, font: { size: 11 } }, border: { display: false }, beginAtZero: true },
                },
            },
        })
        return () => instance.current?.destroy()
    }, [data])

    return <div className="relative w-full h-[240px]"><canvas ref={ref} /></div>
}

// ── Dept chart ─────────────────────────────────────────────────
const DEPT_COLORS = ['#6366f1','#f97316','#22c55e','#8b5cf6','#06b6d4','#f43f5e','#eab308','#ec4899','#14b8a6','#84cc16']

function DeptChart({ data }) {
    const ref = useRef(null)
    const instance = useRef(null)

    useEffect(() => {
        if (!window.Chart || !ref.current || !data) return
        instance.current?.destroy()
        instance.current = new window.Chart(ref.current, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{ label: 'Complaints', data: data.counts, backgroundColor: DEPT_COLORS, borderRadius: 8, borderSkipped: false }],
            },
            options: {
                indexAxis: 'y', responsive: true, maintainAspectRatio: false,
                animation: { duration: 900, easing: 'easeInOutQuart' },
                plugins: { legend: { display: false }, tooltip: { ...DARK_TOOLTIP } },
                scales: {
                    x: { grid: { color: GRID_COLOR }, ticks: { color: TICK_COLOR, font: { size: 11 } }, border: { display: false }, beginAtZero: true, max: Math.max(...(data.counts || [1])) * 1.35 },
                    y: { grid: { display: false }, ticks: { color: '#6b7280', font: { size: 11, weight: 'bold' } }, border: { display: false } },
                },
            },
        })
        return () => instance.current?.destroy()
    }, [data])

    return <div className="relative w-full h-[280px]"><canvas ref={ref} /></div>
}

// ── Location chart ─────────────────────────────────────────────
function LocationChart({ data }) {
    const ref = useRef(null)
    const instance = useRef(null)

    useEffect(() => {
        if (!window.Chart || !ref.current || !data) return
        instance.current?.destroy()
        const locations = data.locations || []
        const labels  = locations.map(l => l.location.split(',')[0])
        const p1 = locations.map(l => l.p1 ?? (l.priority === 1 ? l.complaint_count : 0))
        const p2 = locations.map(l => l.p2 ?? (l.priority === 2 ? l.complaint_count : 0))
        const p3 = locations.map(l => l.p3 ?? (l.priority >= 3 ? l.complaint_count : 0))
        const maxVal = Math.max(...locations.map(l => l.complaint_count || 1), 1)

        instance.current = new window.Chart(ref.current, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    { label: 'Critical (P1)', data: p1, backgroundColor: 'rgba(239,68,68,0.82)', borderRadius: 7, borderSkipped: false },
                    { label: 'High (P2)',     data: p2, backgroundColor: 'rgba(249,115,22,0.82)', borderRadius: 7, borderSkipped: false },
                    { label: 'Medium+ (P3+)', data: p3, backgroundColor: 'rgba(99,102,241,0.82)', borderRadius: 7, borderSkipped: false },
                ],
            },
            options: {
                indexAxis: 'y', responsive: true, maintainAspectRatio: false,
                animation: { duration: 900, easing: 'easeInOutQuart' },
                interaction: { mode: 'index', intersect: false },
                plugins: { legend: { display: false }, tooltip: { ...DARK_TOOLTIP } },
                scales: {
                    x: { grid: { color: GRID_COLOR }, ticks: { color: TICK_COLOR, font: { size: 11 } }, border: { display: false }, beginAtZero: true, max: maxVal * 1.35 },
                    y: { grid: { display: false }, ticks: { color: '#6b7280', font: { size: 11, weight: '600' } }, border: { display: false } },
                },
            },
        })
        return () => instance.current?.destroy()
    }, [data])

    return <div className="relative w-full h-[340px]"><canvas ref={ref} /></div>
}

// ── Doughnut — resolution status ──────────────────────────────
function StatusChart({ overview }) {
    const ref = useRef(null)
    const instance = useRef(null)

    useEffect(() => {
        if (!window.Chart || !ref.current || !overview) return
        instance.current?.destroy()
        const total = overview.total_clusters || 1
        instance.current = new window.Chart(ref.current, {
            type: 'doughnut',
            data: {
                labels: ['Pending', 'In Progress', 'Resolved'],
                datasets: [{
                    data: [overview.pending, overview.inprogress, overview.resolved],
                    backgroundColor: ['rgba(249,115,22,0.85)', 'rgba(99,102,241,0.85)', 'rgba(34,197,94,0.85)'],
                    hoverBackgroundColor: ['#f97316', '#6366f1', '#22c55e'],
                    borderWidth: 3, borderColor: 'rgba(255,255,255,0.08)', hoverOffset: 8,
                }],
            },
            options: {
                responsive: true, maintainAspectRatio: false, cutout: '68%',
                animation: { animateRotate: true, duration: 900 },
                plugins: { legend: { display: false }, tooltip: { ...DARK_TOOLTIP } },
            },
        })
        return () => instance.current?.destroy()
    }, [overview])

    return (
        <div className="relative w-full h-[220px] flex items-center justify-center">
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <p className="text-3xl font-bold text-gray-800 dark:text-white">{overview?.total_clusters ?? '…'}</p>
                <p className="text-[10px] font-semibold uppercase tracking-widest text-gray-400 mt-0.5">Challenges</p>
            </div>
            <canvas ref={ref} />
        </div>
    )
}

// ── Main page ──────────────────────────────────────────────────
export default function Analytics() {
    const [challenges, setChallenges] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    const fetchData = async () => {
        setLoading(true)
        setError(null)
        try {
            const res = await authFetch('/api/challenges/')
            if (!res || !res.ok) {
                throw new Error(`Server returned status ${res?.status || 'network error'}`)
            }
            const data = await res.json()
            setChallenges(Array.isArray(data) ? data : [])
        } catch (err) {
            console.error('Error fetching analytics challenges:', err)
            setError(err.message || 'Failed to load challenge dataset')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchData()
    }, [])

    // ── Derive analytics from real challenge data ──────────────────
    const { ov, vel, dep, loc, pri } = useMemo(() => {
        const list = Array.isArray(challenges) ? challenges : []
        const totalClusters = list.length

        // Total complaints
        const totalComplaints = list.reduce((sum, c) => sum + (Number(c?.complaint_count) || 1), 0)

        // Active challenges (excluding resolved)
        const activeList = list.filter(c => c && c.status !== 'resolved')
        const activeCount = activeList.length

        // Unique departments
        const deptMap = {}
        list.forEach(c => {
            const dept = (c?.department || 'General Administration').trim()
            const count = Number(c?.complaint_count) || 1
            deptMap[dept] = (deptMap[dept] || 0) + count
        })
        const sortedDepts = Object.entries(deptMap)
            .map(([name, count]) => ({ name, count }))
            .sort((a, b) => b.count - a.count)
        const uniqueDeptCount = sortedDepts.length

        // Average RT reach per challenge
        const totalReach = list.reduce((sum, c) => sum + (Number(c?.rt_reach) || 0), 0)
        const avgReach = totalClusters > 0 ? Math.round(totalReach / totalClusters) : 0

        // Resolution status breakdown
        // Pending: pending_verification, verified
        // In Progress: matches_suggested, ready_for_routing, routed, in_project
        // Resolved: resolved
        let pendingCount = 0
        let inProgressCount = 0
        let resolvedCount = 0

        list.forEach(c => {
            if (!c) return
            if (c.status === 'resolved') {
                resolvedCount++
            } else if (c.status === 'pending_verification' || c.status === 'verified') {
                pendingCount++
            } else {
                // matches_suggested, ready_for_routing, routed, in_project or other active states
                inProgressCount++
            }
        })

        const resolutionRate = totalClusters > 0 ? Math.round((resolvedCount / totalClusters) * 100) : 0

        const overview = {
            total_clusters: totalClusters,
            total_complaints: totalComplaints,
            active_challenges: activeCount,
            department_count: uniqueDeptCount,
            avg_rt_reach: avgReach,
            resolution_rate: resolutionRate,
            pending: pendingCount,
            inprogress: inProgressCount,
            resolved: resolvedCount,
        }

        // Priority Load Distribution
        // P1: >= 85, P2: >= 70 & < 85, P3: >= 50 & < 70, P4: < 50
        let p1Count = 0
        let p2Count = 0
        let p3Count = 0
        let p4Count = 0

        list.forEach(c => {
            const score = Number(c?.priority_score) || 0
            const volume = Number(c?.complaint_count) || 1
            if (score >= 85) p1Count += volume
            else if (score >= 70) p2Count += volume
            else if (score >= 50) p3Count += volume
            else p4Count += volume
        })

        const priorityActiveTotal = p1Count + p2Count + p3Count + p4Count
        const calcPct = (cnt) => priorityActiveTotal > 0 ? Math.round((cnt / priorityActiveTotal) * 100) : 0

        const priorityLoad = {
            active_total: priorityActiveTotal,
            priorities: [
                { label: 'Critical (P1)', count: p1Count, pct: calcPct(p1Count) },
                { label: 'High (P2)',     count: p2Count, pct: calcPct(p2Count) },
                { label: 'Medium (P3)',   count: p3Count, pct: calcPct(p3Count) },
                { label: 'Low (P4)',      count: p4Count, pct: calcPct(p4Count) },
            ]
        }

        // Department load chart
        const deptLoad = {
            labels: sortedDepts.map(d => d.name),
            counts: sortedDepts.map(d => d.count),
        }

        // Location hotspots (top 10 by complaint volume)
        const locMap = {}
        list.forEach(c => {
            const locName = (c?.location || 'Unspecified').trim()
            if (!locMap[locName]) {
                locMap[locName] = { location: locName, complaint_count: 0, p1: 0, p2: 0, p3: 0 }
            }
            const volume = Number(c?.complaint_count) || 1
            const score = Number(c?.priority_score) || 0
            locMap[locName].complaint_count += volume

            if (score >= 85) locMap[locName].p1 += volume
            else if (score >= 70) locMap[locName].p2 += volume
            else locMap[locName].p3 += volume
        })

        const sortedLocations = Object.values(locMap)
            .sort((a, b) => b.complaint_count - a.complaint_count)
            .slice(0, 10)

        const locations = {
            locations: sortedLocations
        }

        // 7-day velocity chart
        // Determine the anchor date (latest challenge date or today)
        let anchorDate = new Date()
        for (const c of list) {
            if (c?.created_at) {
                const d = new Date(c.created_at)
                if (!isNaN(d.getTime()) && d > anchorDate) {
                    anchorDate = d
                }
            }
        }

        const dayKeys = []
        const dayLabels = []
        const dailyCounts = {}

        for (let i = 6; i >= 0; i--) {
            const d = new Date(anchorDate)
            d.setDate(d.getDate() - i)
            const yyyy = d.getFullYear()
            const mm = String(d.getMonth() + 1).padStart(2, '0')
            const dd = String(d.getDate()).padStart(2, '0')
            const key = `${yyyy}-${mm}-${dd}`
            dayKeys.push(key)
            dayLabels.push(d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }))
            dailyCounts[key] = 0
        }

        list.forEach(c => {
            if (c?.created_at) {
                const dateKey = String(c.created_at).slice(0, 10)
                if (dailyCounts[dateKey] !== undefined) {
                    dailyCounts[dateKey] += (Number(c?.complaint_count) || 1)
                }
            }
        })

        const complaintsSeries = dayKeys.map(k => dailyCounts[k])
        const sum7Day = complaintsSeries.reduce((a, b) => a + b, 0)
        const avg7Day = Math.round((sum7Day / 7) * 10) / 10
        const avgLine = Array(7).fill(avg7Day)

        const velocity = {
            labels: dayLabels,
            complaints: complaintsSeries,
            avg_line: avgLine,
        }

        return {
            ov: overview,
            vel: velocity,
            dep: deptLoad,
            loc: locations,
            pri: priorityLoad,
        }
    }, [challenges])

    const statCards = ov ? [
        { label: 'Total complaints',  value: ov.total_complaints.toLocaleString(), sub: `Across ${ov.total_clusters} challenges`, subColor: 'text-gray-400' },
        { label: 'Active challenges', value: ov.active_challenges,                 sub: `Across ${ov.department_count} departments`, subColor: 'text-gray-400' },
        { label: 'Avg. RT reach',     value: ov.avg_rt_reach.toLocaleString(),     sub: 'Per challenge',          subColor: 'text-green-600 dark:text-green-400' },
        { label: 'Resolution rate',   value: `${ov.resolution_rate}%`,             sub: `${ov.resolved} resolved`, subColor: ov.resolution_rate > 20 ? 'text-green-600 dark:text-green-400' : 'text-amber-500 dark:text-amber-400' },
    ] : []

    return (
        <div className="space-y-6">

            {/* Page header */}
            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
                <div className="max-w-3xl">
                    <h2 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400 bg-clip-text text-transparent">
                        Analytics &amp; Insights
                    </h2>
                    <p className="text-[13.5px] font-medium text-gray-500 dark:text-gray-400 mt-1.5 leading-relaxed">
                        Comprehensive overview of complaint trends, department performance, and resolution velocity.
                    </p>
                </div>
                <span className="text-[12px] bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 px-3 py-1.5 rounded-full self-start sm:self-auto flex-shrink-0">
                    Last 7 days
                </span>
            </div>

            {error && (
                <div className="flex items-center justify-between text-[13px] text-red-500 bg-red-50 dark:bg-red-900/20 px-4 py-3 rounded-xl border border-red-200 dark:border-red-800">
                    <span>⚠️ Could not load analytics: {error}.</span>
                    <button
                        onClick={fetchData}
                        className="flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded-lg bg-red-100 hover:bg-red-200 dark:bg-red-800 dark:hover:bg-red-700 text-red-700 dark:text-red-200 transition-colors cursor-pointer"
                    >
                        <RefreshCw size={12} /> Retry
                    </button>
                </div>
            )}

            {/* Stat cards */}
            <div className="grid grid-cols-2 xl:grid-cols-4 gap-3">
                {loading
                    ? Array.from({ length: 4 }).map((_, i) => (
                        <div key={i} className="glass-panel px-4 py-4 animate-pulse space-y-2">
                            <div className="h-2.5 bg-gray-200 dark:bg-gray-700 rounded w-2/3" />
                            <div className="h-7 bg-gray-200 dark:bg-gray-700 rounded w-1/2" />
                            <div className="h-2 bg-gray-100 dark:bg-gray-700/50 rounded w-3/4" />
                        </div>
                    ))
                    : statCards.map(({ label, value, sub, subColor }, i) => (
                        <div key={label} className={`glass-panel px-4 py-4 animate-fade-in-up animate-stagger-${i % 4 + 1}`}>
                            <p className="text-[10.5px] font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wide mb-1">{label}</p>
                            <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">{value}</p>
                            <p className={`text-[11px] mt-1 font-medium ${subColor}`}>{sub}</p>
                        </div>
                    ))
                }
            </div>

            {/* Velocity chart */}
            <ChartCard title="Complaint Volume Velocity" sub="Hover for daily breakdown vs 7-day average" badge="Last 7 days">
                {loading ? <SkeletonChart height={240} /> : <VelocityChart data={vel} />}
            </ChartCard>

            {/* Dept load */}
            <ChartCard title="Department Load Distribution" sub="Complaint burden per responsible department" badge={dep?.labels?.length ? `${dep.labels.length} departments` : ''}>
                {loading ? <SkeletonChart height={280} /> : <DeptChart data={dep} />}
            </ChartCard>

            {/* Location hotspot */}
            <ChartCard title="Location-wise Issue Hotspots" sub="Top 10 locations ranked by complaint volume — colour-coded by severity" badge={loc?.locations?.length ? `Top ${loc.locations.length} areas` : 'Top 10 areas'}>
                <div className="flex flex-wrap gap-4 -mt-1">
                    <span className="flex items-center gap-1.5 text-[11px] text-gray-500"><span className="w-3 h-3 rounded-sm bg-red-500 inline-block" /> Critical (P1)</span>
                    <span className="flex items-center gap-1.5 text-[11px] text-gray-500"><span className="w-3 h-3 rounded-sm bg-orange-500 inline-block" /> High (P2)</span>
                    <span className="flex items-center gap-1.5 text-[11px] text-gray-500"><span className="w-3 h-3 rounded-sm bg-indigo-500 inline-block" /> Medium+ (P3+)</span>
                </div>
                {loading ? <SkeletonChart height={340} /> : <LocationChart data={loc} />}
            </ChartCard>

            {/* Status + Priority */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <ChartCard title="Resolution Status Breakdown" sub="Distribution of all active challenges" badge={ov ? `${ov.total_clusters} total` : ''}>
                    {loading ? <SkeletonChart height={220} /> : <StatusChart overview={ov} />}
                    {ov && (
                        <div className="flex flex-col gap-2 mt-2">
                            {[
                                { label: 'Pending',     count: ov.pending,    pct: ov.total_clusters > 0 ? Math.round(ov.pending    / ov.total_clusters * 100) : 0, bg: 'bg-orange-500', icon: '⏳' },
                                { label: 'In Progress', count: ov.inprogress, pct: ov.total_clusters > 0 ? Math.round(ov.inprogress / ov.total_clusters * 100) : 0, bg: 'bg-indigo-500', icon: '🔧' },
                                { label: 'Resolved',    count: ov.resolved,   pct: ov.total_clusters > 0 ? Math.round(ov.resolved   / ov.total_clusters * 100) : 0, bg: 'bg-green-500',  icon: '✅' },
                            ].map(({ label, count, pct, bg, icon }) => (
                                <div key={label} className="flex items-center gap-3 rounded-xl border border-gray-100 dark:border-gray-700/50 bg-white/40 dark:bg-gray-900/30 px-3 py-2">
                                    <span className="text-base">{icon}</span>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="text-[12px] font-bold text-gray-700 dark:text-gray-200">{label}</span>
                                            <span className="text-[12px] font-bold text-gray-800 dark:text-white">{count} <span className="text-[10px] font-normal text-gray-400">challenges</span></span>
                                        </div>
                                        <div className="w-full h-1.5 bg-gray-100 dark:bg-gray-700/60 rounded-full overflow-hidden">
                                            <div className={`h-full rounded-full ${bg}`} style={{ width: `${pct}%` }} />
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </ChartCard>

                <ChartCard title="Priority Load Distribution" sub="Complaint volume by severity" badge={pri ? `${pri.active_total.toLocaleString()} complaints` : ''}>
                    {loading ? <SkeletonChart height={200} /> : pri && (
                        <div className="flex flex-col gap-3 mt-1">
                            {pri.priorities.map(({ label, count, pct }) => {
                                const colors = { 'Critical (P1)': 'bg-red-500', 'High (P2)': 'bg-orange-500', 'Medium (P3)': 'bg-indigo-500', 'Low (P4)': 'bg-gray-400' }
                                const dots   = { 'Critical (P1)': 'bg-red-500', 'High (P2)': 'bg-orange-500', 'Medium (P3)': 'bg-indigo-500', 'Low (P4)': 'bg-gray-400' }
                                const bar = colors[label] ?? 'bg-indigo-500'
                                const dot = dots[label]  ?? 'bg-indigo-500'
                                return (
                                    <div key={label} className="flex items-center gap-3">
                                        <div className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${dot}`} />
                                        <span className="text-[12.5px] font-semibold text-gray-600 dark:text-gray-300 w-36 flex-shrink-0">{label}</span>
                                        <div className="flex-1 h-2.5 bg-gray-100 dark:bg-gray-700/60 rounded-full overflow-hidden">
                                            <div className={`h-full rounded-full ${bar} transition-all duration-700`} style={{ width: `${pct}%` }} />
                                        </div>
                                        <span className="text-[12px] font-bold text-gray-700 dark:text-gray-200 w-10 text-right">{count}</span>
                                        <span className="text-[10.5px] text-gray-400 w-10 text-right">{pct}%</span>
                                    </div>
                                )
                            })}
                        </div>
                    )}
                </ChartCard>
            </div>

        </div>
    )
}