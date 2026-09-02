// ── Stat cards ────────────────────────────────────────────────
export const analyticsStats = [
    { label: 'Total complaints', value: '1,679', sub: '↑ 12% vs yesterday', subColor: 'text-green-600 dark:text-green-400' },
    { label: 'Active clusters', value: '10', sub: 'Across 6 departments', subColor: 'text-gray-400 dark:text-gray-500' },
    { label: 'Avg. RT reach', value: '1,364', sub: '↑ 8% engagement', subColor: 'text-green-600 dark:text-green-400' },
    { label: 'Resolution rate', value: '20%', sub: '↓ 5% this week', subColor: 'text-red-500 dark:text-red-400' },
]

// ── Complaint volume velocity — last 7 days ───────────────────
export const velocityData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    complaints: [180, 240, 210, 320, 290, 160, 140],
    avgLine: [220, 220, 220, 220, 220, 220, 220],
}

// ── Department load ───────────────────────────────────────────
export const deptData = {
    labels: ['MCD', 'PWD', 'DJB', 'BSES', 'NDMC', 'DDA'],
    counts: [703, 287, 310, 220, 134, 177],
}

// ── Priority load ─────────────────────────────────────────────
export const priorityData = {
    activeTotal: 1679,
    priorities: [
        { label: 'Critical (P1)', count: 699, color: 'bg-red-500', dot: 'bg-red-500', pct: 42 },
        { label: 'High (P2)', count: 570, color: 'bg-orange-500', dot: 'bg-orange-500', pct: 34 },
        { label: 'Medium (P3)', count: 409, color: 'bg-indigo-500', dot: 'bg-indigo-500', pct: 24 },
        { label: 'Low (P4)', count: 153, color: 'bg-gray-400', dot: 'bg-gray-400', pct: 9 },
    ],
}

// ── Resolution status (pie) ───────────────────────────────────
export const statusData = {
    labels: ['Pending', 'In progress', 'Resolved'],
    counts: [5, 3, 2],
    colors: ['#f97316', '#6366f1', '#22c55e'],
    legend: [
        { label: 'Pending', pct: '50%', color: 'bg-orange-500' },
        { label: 'In progress', pct: '30%', color: 'bg-indigo-500' },
        { label: 'Resolved', pct: '20%', color: 'bg-green-500' },
    ],
}