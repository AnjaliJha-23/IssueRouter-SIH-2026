import { useEffect, useMemo, useState } from 'react'
import { useIssues } from '../context/IssueContext'
import {
    ChevronDown,
    ChevronUp,
    Users,
    Building2,
    User,
    Activity,
    CheckCircle2,
    Clock,
    Wrench,
    CircleDot,
    Search,
    Filter,
    Image as ImageIcon,
    BadgeCheck,
    MapPin,
} from 'lucide-react'

const STEPS_INPROGRESS = [
    { id: 1, label: 'Complaint Registered', desc: 'Issue cluster identified and logged by IssueRouter AI.', done: true },
    { id: 2, label: 'Assigned to Department', desc: 'Cluster forwarded to the responsible department and officer.', done: true },
    { id: 3, label: 'Field Team Dispatched', desc: 'Ground team has been deployed to assess the situation.', done: true },
    { id: 4, label: 'Work In Progress', desc: 'Active repair / resolution underway.', done: false, active: true },
    { id: 5, label: 'Verification Pending', desc: 'Awaiting site inspection to confirm fix quality.', done: false },
    { id: 6, label: 'Resolved & Closed', desc: 'Issue fully resolved and marked closed.', done: false },
]

const STEPS_RESOLVED = [
    { id: 1, label: 'Complaint Registered', desc: 'Issue cluster identified and logged by IssueRouter AI.', done: true },
    { id: 2, label: 'Assigned to Department', desc: 'Cluster forwarded to the responsible department and officer.', done: true },
    { id: 3, label: 'Field Team Dispatched', desc: 'Ground team deployed to assess the situation.', done: true },
    { id: 4, label: 'Work In Progress', desc: 'Active repair / resolution was underway.', done: true },
    { id: 5, label: 'Verification Pending', desc: 'Site inspection confirmed the fix.', done: true },
    { id: 6, label: 'Resolved & Closed', desc: 'Issue fully resolved and marked closed.', done: true },
]

function formatDuration(ms) {
    if (ms == null) return 'Closed'
    if (ms <= 0) return 'Overdue'
    const totalMinutes = Math.floor(ms / 60000)
    const days = Math.floor(totalMinutes / (60 * 24))
    const hours = Math.floor((totalMinutes % (60 * 24)) / 60)
    const minutes = totalMinutes % 60

    if (days > 0) return `${days}d ${hours}h left`
    if (hours > 0) return `${hours}h ${minutes}m left`
    return `${minutes}m left`
}

function StatusBadge({ status }) {
    if (status === 'inprogress') {
        return (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-semibold rounded-full bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 border border-blue-100 dark:border-blue-800">
                <Wrench size={10} />
                In Progress
            </span>
        )
    }
    return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-semibold rounded-full bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300 border border-emerald-100 dark:border-emerald-800">
            <CheckCircle2 size={10} />
            Resolved
        </span>
    )
}

function OrderTracker({ status }) {
    const steps = status === 'resolved' ? STEPS_RESOLVED : STEPS_INPROGRESS

    return (
        <div className="relative pl-4 py-3 pr-2">
            <div className="absolute left-[22px] top-4 bottom-4 w-0.5 bg-gray-200 dark:bg-gray-700" />
            <div className="space-y-5">
                {steps.map((step) => {
                    const isDone = step.done
                    const isActive = step.active

                    return (
                        <div key={step.id} className="relative flex items-start gap-4 pl-3">
                            <div
                                className={`
                                    relative z-10 flex-shrink-0 w-5 h-5 rounded-full border-2 flex items-center justify-center
                                    transition-all duration-300
                                    ${isDone
                                        ? 'bg-indigo-600 border-indigo-600 dark:bg-indigo-500 dark:border-indigo-500'
                                        : isActive
                                        ? 'bg-white dark:bg-gray-800 border-indigo-500 ring-4 ring-indigo-100 dark:ring-indigo-900/40'
                                        : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600'
                                    }
                                `}
                            >
                                {isDone && <CheckCircle2 size={11} className="text-white" />}
                                {isActive && <CircleDot size={11} className="text-indigo-500 animate-pulse" />}
                            </div>
                            <div className="pb-1">
                                <p
                                    className={`text-[13px] font-semibold leading-tight ${
                                        isDone ? 'text-gray-800 dark:text-gray-100'
                                        : isActive ? 'text-indigo-600 dark:text-indigo-400'
                                        : 'text-gray-400 dark:text-gray-600'
                                    }`}
                                >
                                    {step.label}
                                </p>
                                <p
                                    className={`text-[11px] mt-0.5 ${
                                        isDone || isActive ? 'text-gray-500 dark:text-gray-400' : 'text-gray-300 dark:text-gray-700'
                                    }`}
                                >
                                    {step.desc}
                                </p>
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}

function EvidenceGallery({ title, photos }) {
    if (!photos?.length) {
        return (
            <div className="rounded-xl border border-dashed border-gray-200 dark:border-gray-700 bg-white/70 dark:bg-gray-900/40 px-4 py-5 text-center">
                <ImageIcon size={18} className="mx-auto text-gray-300 dark:text-gray-600" />
                <p className="mt-2 text-[12px] text-gray-400 dark:text-gray-500">{title}</p>
                <p className="mt-1 text-[11px] text-gray-300 dark:text-gray-600">No images uploaded yet.</p>
            </div>
        )
    }

    return (
        <div className="space-y-3">
            <div className="flex items-center gap-2">
                <ImageIcon size={13} className="text-indigo-500" />
                <p className="text-[12px] font-semibold text-gray-700 dark:text-gray-200">{title}</p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {photos.map((photo) => (
                    <div
                        key={photo.id}
                        className="overflow-hidden rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-sm"
                    >
                        <img src={photo.src} alt={photo.title} className="h-32 w-full object-cover" />
                        <div className="px-3 py-2">
                            <p className="text-[12px] font-semibold text-gray-800 dark:text-gray-100">{photo.title}</p>
                            <p className="text-[11px] text-gray-400 dark:text-gray-500">{photo.subtitle}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}

function AccountabilityPanel({ cluster, officer, timeLeft, dueAt, onResolve }) {
    const uploadedPhotos = cluster.officer_photos ?? []
    const resolvedPhotos = cluster.resolved_photos ?? []
    const isResolved = cluster.status === 'resolved'
    const hasOfficer = Boolean(officer)

    return (
        <div className="rounded-xl border border-emerald-100 dark:border-emerald-900/40 bg-emerald-50/60 dark:bg-emerald-950/20 overflow-hidden">
            <div className="px-4 py-3 border-b border-emerald-100 dark:border-emerald-900/40 flex items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                    <BadgeCheck size={13} className="text-emerald-600 dark:text-emerald-400" />
                    <span className="text-[12px] font-semibold text-emerald-800 dark:text-emerald-300">
                        Accountability Check
                    </span>
                </div>
                <StatusBadge status={cluster.status} />
            </div>

            <div className="p-4 space-y-4">
                <div className="grid gap-3 sm:grid-cols-2">
                    <div className="rounded-xl bg-white/80 dark:bg-gray-900/40 border border-white/60 dark:border-gray-700 px-3 py-3">
                        <p className="text-[10px] uppercase tracking-[0.2em] text-gray-400 dark:text-gray-500">Assigned Officer</p>
                        <p className="mt-1 text-[13px] font-semibold text-gray-800 dark:text-gray-100">
                            {hasOfficer ? officer.name : 'Not assigned yet'}
                        </p>
                        <p className="text-[11px] text-gray-500 dark:text-gray-400">
                            {hasOfficer ? `${officer.designation} - ${officer.id}` : 'Officer details will appear here after assignment.'}
                        </p>
                    </div>
                    <div className="rounded-xl bg-white/80 dark:bg-gray-900/40 border border-white/60 dark:border-gray-700 px-3 py-3">
                        <p className="text-[10px] uppercase tracking-[0.2em] text-gray-400 dark:text-gray-500">SLA Window</p>
                        <p className="mt-1 text-[13px] font-semibold text-gray-800 dark:text-gray-100">
                            {timeLeft}
                        </p>
                        <p className="text-[11px] text-gray-500 dark:text-gray-400">
                            {dueAt ? `Resolve by ${new Date(dueAt).toLocaleString()}` : 'Three-day response window applies after assignment.'}
                        </p>
                    </div>
                </div>

                {!isResolved ? (
                    <div className="rounded-xl border border-indigo-100 dark:border-indigo-900/40 bg-white/80 dark:bg-gray-900/40 px-4 py-3">
                        <div className="flex items-center gap-2 mb-3">
                            <ImageIcon size={13} className="text-indigo-500" />
                            <p className="text-[12px] font-semibold text-gray-700 dark:text-gray-200">
                                Officer uploaded images
                            </p>
                        </div>
                        <EvidenceGallery title="Photos uploaded by the assigned officer" photos={uploadedPhotos} />
                    </div>
                ) : (
                    <div className="rounded-xl border border-emerald-100 dark:border-emerald-900/40 bg-white/80 dark:bg-gray-900/40 px-4 py-3">
                        <div className="flex items-center gap-2 mb-3">
                            <CheckCircle2 size={13} className="text-emerald-500" />
                            <p className="text-[12px] font-semibold text-gray-700 dark:text-gray-200">
                                Resolved evidence
                            </p>
                        </div>
                        <EvidenceGallery title="Dummy resolved photos" photos={resolvedPhotos} />
                    </div>
                )}

                {!isResolved && (
                    <button
                        onClick={onResolve}
                        disabled={!hasOfficer}
                        className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-[12.5px] font-semibold bg-emerald-600 hover:bg-emerald-500 disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed text-white transition-all duration-200 shadow-[0_4px_14px_rgba(16,185,129,0.28)] hover:shadow-[0_4px_18px_rgba(16,185,129,0.42)]"
                    >
                        <CheckCircle2 size={14} />
                        Mark Resolved
                    </button>
                )}
            </div>
        </div>
    )
}

export default function Progress() {
    const { issues, assignments, discarded, resolveIssue } = useIssues()
    const [expandedId, setExpandedId] = useState(null)
    const [search, setSearch] = useState('')
    const [statusFilter, setStatusFilter] = useState('all')
    const [now, setNow] = useState(() => Date.now())

    useEffect(() => {
        const timer = setInterval(() => setNow(Date.now()), 30_000)
        return () => clearInterval(timer)
    }, [])

    const progressClusters = useMemo(() => {
        const active = issues.filter(
            (cluster) => (cluster.status === 'inprogress' || cluster.status === 'resolved') && !discarded.has(cluster.cluster_id)
        )

        return [...active].sort((a, b) => {
            const aAssigned = assignments[a.cluster_id] ? 1 : 0
            const bAssigned = assignments[b.cluster_id] ? 1 : 0
            return bAssigned - aAssigned
        })
    }, [issues, assignments, discarded])

    const filtered = useMemo(() => {
        return progressClusters.filter((cluster) => {
            const matchSearch =
                !search ||
                cluster.problem.toLowerCase().includes(search.toLowerCase()) ||
                cluster.location.toLowerCase().includes(search.toLowerCase()) ||
                cluster.department.toLowerCase().includes(search.toLowerCase())
            const matchStatus = statusFilter === 'all' || cluster.status === statusFilter
            return matchSearch && matchStatus
        })
    }, [progressClusters, search, statusFilter])

    const inprogressCount = progressClusters.filter((cluster) => cluster.status === 'inprogress').length
    const resolvedCount = progressClusters.filter((cluster) => cluster.status === 'resolved').length

    return (
        <div className="space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-2">
                <div>
                    <h2 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400 bg-clip-text text-transparent">
                        Progress Tracker
                    </h2>
                    <p className="text-[13px] font-medium text-gray-500 dark:text-gray-400 mt-1">
                        Live tracking of active complaints and resolved issue reviews.
                    </p>
                </div>
                <span className="text-[12px] bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 px-3 py-1.5 rounded-full self-start sm:self-auto">
                    {filtered.length} issue{filtered.length !== 1 ? 's' : ''}
                </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {[
                    { label: 'Total Tracked', value: progressClusters.length, color: 'from-indigo-600 to-purple-500', icon: <Activity size={18} className="text-indigo-500" />, bg: 'bg-indigo-50 dark:bg-indigo-900/30' },
                    { label: 'In Progress', value: inprogressCount, color: 'from-blue-600 to-indigo-500', icon: <Wrench size={18} className="text-blue-500" />, bg: 'bg-blue-50 dark:bg-blue-900/30' },
                    { label: 'Resolved', value: resolvedCount, color: 'from-emerald-600 to-green-500', icon: <CheckCircle2 size={18} className="text-emerald-500" />, bg: 'bg-emerald-50 dark:bg-emerald-900/30' },
                ].map(({ label, value, color, icon, bg }) => (
                    <div key={label} className="glass-panel px-4 py-4 flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${bg}`}>{icon}</div>
                        <div>
                            <p className="text-[10.5px] font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wide mb-0.5">{label}</p>
                            <p className={`text-2xl font-bold bg-gradient-to-r ${color} bg-clip-text text-transparent`}>{value}</p>
                        </div>
                    </div>
                ))}
            </div>

            <div className="glass-panel p-3.5 flex flex-wrap gap-3 items-center">
                <div className="relative flex-1 min-w-[200px]">
                    <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                    <input
                        type="text"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search by issue, location, department..."
                        className="w-full h-[34px] pl-8 pr-3 text-[12px] bg-gray-100 dark:bg-gray-700 border border-transparent rounded-lg outline-none text-gray-700 dark:text-gray-200 placeholder:text-gray-400 focus:border-indigo-400 focus:bg-white dark:focus:bg-gray-900 transition-colors"
                    />
                </div>
                <div className="flex items-center gap-2">
                    <Filter size={13} className="text-gray-400 flex-shrink-0" />
                    {['all', 'inprogress', 'resolved'].map((status) => (
                        <button
                            key={status}
                            onClick={() => setStatusFilter(status)}
                            className={`text-[12px] px-3 py-1.5 rounded-full border transition-colors ${
                                statusFilter === status
                                    ? 'bg-indigo-700 text-white border-indigo-700'
                                    : 'bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400 border-gray-200 dark:border-gray-700 hover:border-gray-300'
                            }`}
                        >
                            {status === 'all' ? 'All' : status === 'inprogress' ? 'In Progress' : 'Resolved'}
                        </button>
                    ))}
                </div>
            </div>

            <div className="glass-panel overflow-hidden">
                <div className="grid grid-cols-[2fr_1fr_1fr_1.2fr_1fr_40px] gap-4 px-5 py-3 bg-gray-50 dark:bg-gray-800/60 border-b border-gray-100 dark:border-gray-700">
                    {['Issue Name', 'Complainants', 'Department', 'Assigned Officer', 'Status', ''].map((heading) => (
                        <span key={heading} className="text-[10px] uppercase tracking-widest font-semibold text-gray-400 dark:text-gray-500">
                            {heading}
                        </span>
                    ))}
                </div>

                {filtered.length === 0 ? (
                    <div className="text-center py-14">
                        <p className="text-sm text-gray-400 dark:text-gray-600">No issues match your filters.</p>
                    </div>
                ) : (
                    <div className="divide-y divide-gray-100 dark:divide-gray-700/60">
                        {filtered.map((cluster) => {
                            const isExpanded = expandedId === cluster.cluster_id
                            const officerObj = assignments[cluster.cluster_id]
                            const officerName = officerObj ? officerObj.name : 'Unassigned'
                            const hasOfficer = Boolean(officerObj)
                            const isResolved = cluster.status === 'resolved'
                            const dueAt = officerObj?.dueAt || cluster.due_at
                            const remainingMs = dueAt ? new Date(dueAt).getTime() - now : null

                            return (
                                <div key={cluster.cluster_id} className={`transition-all ${hasOfficer ? 'ring-1 ring-indigo-200 dark:ring-indigo-800/50' : ''}`}>
                                    <div
                                        className="grid grid-cols-[2fr_1fr_1fr_1.2fr_1fr_40px] gap-4 px-5 py-4 items-center cursor-pointer hover:bg-gray-50/80 dark:hover:bg-gray-700/30 transition-colors group"
                                        onClick={() => setExpandedId((prev) => (prev === cluster.cluster_id ? null : cluster.cluster_id))}
                                    >
                                        <div className="min-w-0">
                                            <div className="flex items-center gap-2">
                                                <p className="text-[13px] font-semibold text-gray-800 dark:text-gray-100 truncate leading-tight">
                                                    {cluster.problem}
                                                </p>
                                                {hasOfficer && (
                                                    <span className="flex-shrink-0 text-[9px] font-bold uppercase tracking-wide px-1.5 py-0.5 rounded-full bg-indigo-100 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400">
                                                        Active
                                                    </span>
                                                )}
                                            </div>
                                            <p className="text-[10px] text-gray-400 dark:text-gray-500 mt-0.5">
                                                {cluster.cluster_id} - {cluster.location}
                                            </p>
                                        </div>

                                        <div className="flex items-center gap-1.5">
                                            <Users size={12} className="text-gray-400 flex-shrink-0" />
                                            <span className="text-[13px] font-medium text-gray-700 dark:text-gray-300">
                                                {cluster.complaint_count.toLocaleString()}
                                            </span>
                                        </div>

                                        <div className="flex items-center gap-1.5">
                                            <Building2 size={12} className="text-gray-400 flex-shrink-0" />
                                            <span className="text-[12px] text-gray-600 dark:text-gray-400 truncate">
                                                {cluster.department}
                                            </span>
                                        </div>

                                        <div className="flex items-center gap-2">
                                            <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${hasOfficer ? 'bg-indigo-200 dark:bg-indigo-800/60' : 'bg-gray-100 dark:bg-gray-700'}`}>
                                                <User size={11} className={hasOfficer ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-400'} />
                                            </div>
                                            <span className={`text-[12px] truncate ${hasOfficer ? 'text-indigo-600 dark:text-indigo-400 font-semibold' : 'text-gray-500 dark:text-gray-500'}`}>
                                                {officerName}
                                            </span>
                                        </div>

                                        <StatusBadge status={cluster.status} />

                                        <button className="flex items-center justify-center w-7 h-7 rounded-lg text-gray-400 group-hover:text-indigo-500 group-hover:bg-indigo-50 dark:group-hover:bg-indigo-900/20 transition-colors">
                                            {isExpanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
                                        </button>
                                    </div>

                                    {isExpanded && (
                                        <div className="mx-5 mb-5 mt-1 rounded-xl border border-indigo-100 dark:border-indigo-900/40 bg-indigo-50/40 dark:bg-indigo-950/20 overflow-hidden animate-fade-in-up">
                                            {officerObj && (
                                                <div className="px-4 py-2.5 bg-indigo-50 dark:bg-indigo-900/20 border-b border-indigo-100 dark:border-indigo-900/40 flex items-center gap-2">
                                                    <User size={12} className="text-indigo-500" />
                                                    <span className="text-[12px] text-indigo-700 dark:text-indigo-300">
                                                        <span className="font-semibold">{officerObj.name}</span>
                                                        <span className="text-indigo-400 dark:text-indigo-500">
                                                            {' '} - {officerObj.designation} - {officerObj.id}
                                                        </span>
                                                    </span>
                                                </div>
                                            )}

                                            <div className="px-4 py-3 border-b border-indigo-100 dark:border-indigo-900/40 flex items-center gap-2">
                                                <Clock size={13} className="text-indigo-500" />
                                                <span className="text-[12px] font-semibold text-indigo-700 dark:text-indigo-300">
                                                    Issue Resolution Timeline
                                                </span>
                                            </div>

                                            <div className="grid lg:grid-cols-[1.05fr_0.95fr] gap-4 p-4">
                                                <div className="rounded-xl border border-indigo-100 dark:border-indigo-900/40 bg-white/70 dark:bg-gray-900/40">
                                                    <OrderTracker status={cluster.status} />
                                                </div>

                                                <div className="space-y-3">
                                                    <div className="rounded-xl border border-emerald-100 dark:border-emerald-900/40 bg-white/80 dark:bg-gray-900/40 px-4 py-3">
                                                        <div className="flex items-center gap-2">
                                                            <MapPin size={12} className="text-emerald-500" />
                                                            <p className="text-[12px] font-semibold text-gray-700 dark:text-gray-200">
                                                                {cluster.location}
                                                            </p>
                                                        </div>
                                                        <p className="mt-2 text-[12px] text-gray-600 dark:text-gray-300 leading-relaxed">
                                                            {cluster.summary}
                                                        </p>
                                                        <p className="mt-3 text-[11px] text-gray-400 dark:text-gray-500">
                                                            {isResolved
                                                                ? 'Issue closed after evidence review.'
                                                                : dueAt
                                                                    ? `SLA ends ${new Date(dueAt).toLocaleString()}`
                                                                    : 'SLA starts once an officer is assigned.'}
                                                        </p>
                                                        <p className={`mt-1 text-[12px] font-semibold ${remainingMs != null && remainingMs <= 0 ? 'text-red-500' : 'text-emerald-600 dark:text-emerald-400'}`}>
                                                            {isResolved ? 'Closed' : formatDuration(remainingMs)}
                                                        </p>
                                                    </div>

                                                    <AccountabilityPanel
                                                        cluster={cluster}
                                                        officer={officerObj}
                                                        timeLeft={formatDuration(remainingMs)}
                                                        dueAt={dueAt}
                                                        onResolve={() => resolveIssue(cluster.cluster_id)}
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )
                        })}
                    </div>
                )}
            </div>
        </div>
    )
}
