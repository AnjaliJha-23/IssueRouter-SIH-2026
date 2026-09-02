import { useEffect, useRef } from 'react'
import useStats from '../hooks/useStats'
import { AlertTriangle, Zap, Clock, BarChart3, TrendingUp } from 'lucide-react'

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
        const p1 = locations.map(l => l.priority === 1 ? l.complaint_count : 0)
        const p2 = locations.map(l => l.priority === 2 ? l.complaint_count : 0)
        const p3 = locations.map(l => l.priority >= 3 ? l.complaint_count : 0)
        const maxVal = Math.max(...locations.map(l => l.complaint_count), 1)

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
                <p className="text-[10px] font-semibold uppercase tracking-widest text-gray-400 mt-0.5">Clusters</p>
            </div>
            <canvas ref={ref} />
        </div>
    )
}

// ── Main page ──────────────────────────────────────────────────
export default function Analytics() {
    const { stats, loading, error } = useStats()
    const ov  = stats?.overview
    const vel = stats?.velocity
    const dep = stats?.deptLoad
    const loc = stats?.locations
    const pri = stats?.priorityLoad

    const statCards = ov ? [
        { label: 'Total complaints',  value: ov.total_complaints.toLocaleString(), sub: `Across ${ov.total_clusters} clusters`, subColor: 'text-gray-400' },
        { label: 'Active clusters',   value: ov.total_clusters,                    sub: `${Object.keys({}).length || 'Multiple'} departments`, subColor: 'text-gray-400' },
        { label: 'Avg. RT reach',     value: ov.avg_rt_reach.toLocaleString(),     sub: 'Per cluster',          subColor: 'text-green-600 dark:text-green-400' },
        { label: 'Resolution rate',   value: `${ov.resolution_rate}%`,             sub: `${ov.resolved} resolved`, subColor: ov.resolution_rate > 20 ? 'text-green-600 dark:text-green-400' : 'text-red-500 dark:text-red-400' },
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
                <div className="text-[13px] text-red-500 bg-red-50 dark:bg-red-900/20 px-4 py-3 rounded-xl border border-red-200 dark:border-red-800">
                    ⚠️ Could not load analytics: {error}. Is the backend running?
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
            <ChartCard title="Department Load Distribution" sub="Complaint burden per responsible department" badge={dep ? `${dep.labels.length} departments` : ''}>
                {loading ? <SkeletonChart height={280} /> : <DeptChart data={dep} />}
            </ChartCard>

            {/* Location hotspot */}
            <ChartCard title="Location-wise Issue Hotspots" sub="Top 10 locations ranked by complaint volume — colour-coded by severity" badge="Top 10 areas">
                <div className="flex flex-wrap gap-4 -mt-1">
                    <span className="flex items-center gap-1.5 text-[11px] text-gray-500"><span className="w-3 h-3 rounded-sm bg-red-500 inline-block" /> Critical (P1)</span>
                    <span className="flex items-center gap-1.5 text-[11px] text-gray-500"><span className="w-3 h-3 rounded-sm bg-orange-500 inline-block" /> High (P2)</span>
                    <span className="flex items-center gap-1.5 text-[11px] text-gray-500"><span className="w-3 h-3 rounded-sm bg-indigo-500 inline-block" /> Medium+ (P3+)</span>
                </div>
                {loading ? <SkeletonChart height={340} /> : <LocationChart data={loc} />}
            </ChartCard>

            {/* Status + Priority */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <ChartCard title="Resolution Status Breakdown" sub="Distribution of all active clusters" badge={ov ? `${ov.total_clusters} total` : ''}>
                    {loading ? <SkeletonChart height={220} /> : <StatusChart overview={ov} />}
                    {ov && (
                        <div className="flex flex-col gap-2 mt-2">
                            {[
                                { label: 'Pending',     count: ov.pending,    pct: Math.round(ov.pending    / ov.total_clusters * 100), bg: 'bg-orange-500', icon: '⏳' },
                                { label: 'In Progress', count: ov.inprogress, pct: Math.round(ov.inprogress / ov.total_clusters * 100), bg: 'bg-indigo-500', icon: '🔧' },
                                { label: 'Resolved',    count: ov.resolved,   pct: Math.round(ov.resolved   / ov.total_clusters * 100), bg: 'bg-green-500',  icon: '✅' },
                            ].map(({ label, count, pct, bg, icon }) => (
                                <div key={label} className="flex items-center gap-3 rounded-xl border border-gray-100 dark:border-gray-700/50 bg-white/40 dark:bg-gray-900/30 px-3 py-2">
                                    <span className="text-base">{icon}</span>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="text-[12px] font-bold text-gray-700 dark:text-gray-200">{label}</span>
                                            <span className="text-[12px] font-bold text-gray-800 dark:text-white">{count} <span className="text-[10px] font-normal text-gray-400">clusters</span></span>
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