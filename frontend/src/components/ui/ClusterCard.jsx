import { useState, useEffect } from 'react'
import {
    ChevronDown,
    MapPin,
    Building2,
    TrendingUp,
    TrendingDown,
    Minus,
    X as XIcon,
    ShieldCheck,
    Mail,
    Trash2,
    Sparkles,
    User,
    CheckCircle2,
    Bell,
    Search,
    Image as ImageIcon,
} from 'lucide-react'
import { useIssues } from '../../context/IssueContext'
import { OFFICERS_BY_DEPT } from '../../data/Officers'

const PRIORITY_STYLES = {
    1: { rank: 'bg-red-50 text-red-800', card: 'border-l-4 border-l-red-500' },
    2: { rank: 'bg-amber-50 text-amber-800', card: 'border-l-4 border-l-orange-400' },
    3: { rank: 'bg-blue-50 text-blue-800', card: 'border-l-4 border-l-blue-400' },
    4: { rank: 'bg-gray-100 text-gray-600', card: 'border-l-4 border-l-gray-300' },
}

const STATUS_STYLES = {
    pending: 'bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
    inprogress: 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
    resolved: 'bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300',
}

const STATUS_LABELS = {
    pending: 'Pending',
    inprogress: 'In progress',
    resolved: 'Resolved',
}

const SEVERITY = {
    1: { label: 'Critical', bg: 'bg-red-500/10 border border-red-500/30 text-red-500 dark:text-red-400', dot: 'bg-red-500 shadow-[0_0_6px_rgba(239,68,68,0.8)]' },
    2: { label: 'High',     bg: 'bg-orange-500/10 border border-orange-500/30 text-orange-500 dark:text-orange-400', dot: 'bg-orange-500 shadow-[0_0_6px_rgba(249,115,22,0.8)]' },
    3: { label: 'Medium',   bg: 'bg-blue-500/10 border border-blue-500/30 text-blue-600 dark:text-blue-400', dot: 'bg-blue-500 shadow-[0_0_6px_rgba(99,102,241,0.6)]' },
    4: { label: 'Low',      bg: 'bg-gray-400/10 border border-gray-400/30 text-gray-500 dark:text-gray-400', dot: 'bg-gray-400' },
}

function TrendIcon({ trend }) {
    if (trend === 'up') return <TrendingUp size={14} className="text-red-500" />
    if (trend === 'down') return <TrendingDown size={14} className="text-green-600" />
    return <Minus size={14} className="text-gray-400" />
}

function PhotoStrip({ photos }) {
    if (!photos?.length) return null

    return (
        <div className="space-y-2">
            <div className="flex items-center gap-1.5">
                <ImageIcon size={12} className="text-emerald-500" />
                <p className="text-[11px] font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
                    Resolved photos
                </p>
            </div>
            <div className="grid grid-cols-2 gap-2">
                {photos.slice(0, 4).map((photo) => (
                    <div key={photo.id} className="overflow-hidden rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                        <img src={photo.src} alt={photo.title} className="h-20 w-full object-cover" />
                    </div>
                ))}
            </div>
        </div>
    )
}

// ── Officer Picker Modal ────────────────────────────────────────────────────
function OfficerModal({ department, onSelect, onClose }) {
    const [query, setQuery] = useState('')
    const officers = OFFICERS_BY_DEPT[department] || []
    const filtered = officers.filter(
        o => o.name.toLowerCase().includes(query.toLowerCase()) ||
             o.designation.toLowerCase().includes(query.toLowerCase())
    )

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
            onClick={onClose}
        >
            <div
                className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-md border border-gray-200 dark:border-gray-700 animate-fade-in-up"
                onClick={e => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100 dark:border-gray-700">
                    <div>
                        <p className="text-[14px] font-bold text-gray-800 dark:text-gray-100">Select Officer</p>
                        <p className="text-[11px] text-gray-400 mt-0.5">{department} Department — {officers.length} officers available</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="w-7 h-7 rounded-full flex items-center justify-center text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                        <XIcon size={14} />
                    </button>
                </div>

                {/* Search */}
                <div className="px-4 pt-3 pb-2">
                    <div className="relative">
                        <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                        <input
                            type="text"
                            value={query}
                            onChange={e => setQuery(e.target.value)}
                            placeholder="Search by name or designation..."
                            autoFocus
                            className="w-full pl-8 pr-3 py-2 text-[12px] rounded-lg bg-gray-100 dark:bg-gray-700 outline-none text-gray-700 dark:text-gray-200 placeholder:text-gray-400 focus:ring-1 focus:ring-indigo-400 transition-all"
                        />
                    </div>
                </div>

                {/* Officer list */}
                <div className="px-3 pb-3 max-h-72 overflow-y-auto space-y-1">
                    {filtered.length === 0 ? (
                        <p className="text-center text-[12px] text-gray-400 py-6">No officers match your search.</p>
                    ) : (
                        filtered.map(officer => (
                            <button
                                key={officer.id}
                                onClick={() => onSelect(officer)}
                                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-indigo-50 dark:hover:bg-indigo-900/30 transition-colors text-left group"
                            >
                                <div className="w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center flex-shrink-0 group-hover:bg-indigo-200 dark:group-hover:bg-indigo-800/50 transition-colors">
                                    <User size={14} className="text-indigo-600 dark:text-indigo-400" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="text-[12.5px] font-semibold text-gray-800 dark:text-gray-100 truncate">{officer.name}</p>
                                    <p className="text-[11px] text-gray-400 truncate">{officer.designation}</p>
                                </div>
                                <span className="text-[10px] font-mono text-gray-300 dark:text-gray-600 group-hover:text-indigo-400 transition-colors">{officer.id}</span>
                            </button>
                        ))
                    )}
                </div>
            </div>
        </div>
    )
}

// ── Notification Toast ──────────────────────────────────────────────────────
function Toast({ officer, onDone }) {
    useEffect(() => {
        const t = setTimeout(onDone, 3500)
        return () => clearTimeout(t)
    }, [onDone])

    return (
        <div className="fixed bottom-6 right-6 z-50 animate-fade-in-up">
            <div className="flex items-start gap-3 bg-gray-900 dark:bg-gray-800 text-white px-4 py-3.5 rounded-2xl shadow-2xl border border-white/10 max-w-xs">
                <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Bell size={14} className="text-emerald-400" />
                </div>
                <div>
                    <p className="text-[13px] font-semibold">Officer Notified</p>
                    <p className="text-[11px] text-gray-300 mt-0.5 leading-relaxed">
                        <span className="text-emerald-400 font-medium">{officer.name}</span> has been assigned and notified about this issue.
                    </p>
                </div>
                <button onClick={onDone} className="ml-1 text-gray-500 hover:text-gray-300 transition-colors flex-shrink-0">
                    <XIcon size={12} />
                </button>
            </div>
        </div>
    )
}

// ── Main ClusterCard ────────────────────────────────────────────────────────
export default function ClusterCard({ cluster, rank, expanded, onToggle }) {
    const { assignOfficer, discardIssue, assignments, discarded, issues } = useIssues()

    const [showModal, setShowModal] = useState(false)
    const [showToast, setShowToast] = useState(false)
    const [discarding, setDiscarding] = useState(false)

    // Live status and assignment from context
    const liveIssue = issues.find(c => c.cluster_id === cluster.cluster_id) || cluster
    const currentStatus = liveIssue.status
    const assignedOfficer = assignments[cluster.cluster_id]
    const isDiscarded = discarded.has(cluster.cluster_id)

    // Derive dept email
    const deptEmail = `${cluster.department.toLowerCase().replace(/\s+/g, '.')}@delhi.gov.in`
    const mailSubject = encodeURIComponent(`[IssueRouter Alert] ${cluster.problem} — ${cluster.location}`)
    const mailBody = encodeURIComponent(
`Dear ${cluster.department} Department,

This is an automated escalation from IssueRouter for a civic complaint cluster requiring immediate attention.

ISSUE SUMMARY
--------------
Cluster ID   : ${cluster.cluster_id}
Problem      : ${cluster.problem}
Location     : ${cluster.location}
Severity     : ${['', 'Critical', 'High', 'Medium', 'Low'][cluster.priority]}
Status       : ${currentStatus}
Complaint Count : ${cluster.complaint_count} citizens affected
RT Reach     : ${cluster.rt_reach.toLocaleString()}
Time Window  : ${cluster.time_window}

AI RECOMMENDED ACTION
---------------------
${cluster.recommended_action}

Please treat this as a priority matter and respond with a timeline for resolution.

Regards,
IssueRouter Civic Triage System`
    )

    const ps = PRIORITY_STYLES[cluster.priority] ?? PRIORITY_STYLES[4]
    const sev = SEVERITY[cluster.priority] ?? SEVERITY[4]
    const liveStatusStyle = STATUS_STYLES[currentStatus] ?? STATUS_STYLES.pending
    const liveStatusLabel = STATUS_LABELS[currentStatus] ?? currentStatus

    const handleOfficerSelect = (officer) => {
        setShowModal(false)
        assignOfficer(cluster.cluster_id, officer)
        setShowToast(true)
    }

    const handleDiscard = () => {
        setDiscarding(true)
        setTimeout(() => {
            discardIssue(cluster.cluster_id)
        }, 400)
    }

    if (isDiscarded) return null

    return (
        <>
            {/* Officer picker modal */}
            {showModal && (
                <OfficerModal
                    department={cluster.department}
                    onSelect={handleOfficerSelect}
                    onClose={() => setShowModal(false)}
                />
            )}

            {/* Notification toast */}
            {showToast && (
                <Toast
                    officer={assignedOfficer}
                    onDone={() => setShowToast(false)}
                />
            )}

            {/* Card — fades + shrinks out on discard */}
            <div
                className={`flex flex-col glass-panel rounded-xl overflow-hidden ${ps.card} h-full
                    transition-all duration-400 ease-in-out
                    ${discarding ? 'opacity-0 scale-95 pointer-events-none' : 'opacity-100 scale-100'}
                `}
            >
                {/* ── Card body ── */}
                <div className="p-4 relative flex flex-col flex-1">
                    <div className={`absolute top-0 left-0 w-7 h-7 flex items-center justify-center text-[11px] font-semibold rounded-tl-xl rounded-br-lg ${ps.rank}`}>
                        #{rank}
                    </div>

                    <div className="pl-6 flex flex-col flex-1 gap-2">
                        <div className="flex flex-wrap items-center gap-2">
                            <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold tracking-wide ${sev.bg}`}>
                                <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${sev.dot}`} />
                                {sev.label}
                            </span>
                            <span className={`inline-flex items-center text-[11px] px-2 py-0.5 rounded-full font-medium ${liveStatusStyle}`}>
                                {liveStatusLabel}
                            </span>
                        </div>

                        <p className="text-[15px] font-bold text-gray-800 dark:text-gray-100 leading-snug line-clamp-2">
                            {cluster.problem}
                        </p>
                        <p className="text-[12.5px] text-gray-500 dark:text-gray-400 leading-relaxed line-clamp-2 flex-1">
                            {cluster.summary}
                        </p>

                        <div className="flex flex-wrap gap-1.5 pt-1">
                            <span className="inline-flex items-center gap-1 text-[11px] bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 px-2 py-0.5 rounded-full border border-indigo-200/50 dark:border-indigo-700/30">
                                <Building2 size={10} />
                                {cluster.department}
                            </span>
                            <span className="inline-flex items-center gap-1 text-[11px] bg-teal-50 dark:bg-teal-900/30 text-teal-700 dark:text-teal-300 px-2 py-0.5 rounded-full border border-teal-200/50 dark:border-teal-700/30">
                                <MapPin size={10} />
                                {cluster.location.split(',')[0]}
                            </span>
                        </div>
                    </div>
                </div>

                {/* ── Stats row ── */}
                <div className="grid grid-cols-3 border-t border-gray-200/50 dark:border-gray-700/50 bg-gray-50/50 dark:bg-gray-800/30 flex-shrink-0">
                    <div className="py-3 text-center border-r border-gray-200/50 dark:border-gray-700/50">
                        <p className="text-xl font-bold bg-gradient-to-br from-gray-800 to-gray-500 bg-clip-text text-transparent dark:from-white dark:to-gray-400">
                            {cluster.complaint_count}
                        </p>
                        <p className="text-[10px] font-semibold text-gray-400 mt-0.5 uppercase tracking-wide">Complaints</p>
                    </div>
                    <div className="py-3 text-center border-r border-gray-200/50 dark:border-gray-700/50">
                        <p className="text-xl font-bold bg-gradient-to-br from-gray-800 to-gray-500 bg-clip-text text-transparent dark:from-white dark:to-gray-400">
                            {cluster.rt_reach.toLocaleString()}
                        </p>
                        <p className="text-[10px] font-semibold text-gray-400 mt-0.5 uppercase tracking-wide">RT Reach</p>
                    </div>
                    <div className="py-3 flex flex-col items-center justify-center gap-1">
                        <div className="bg-white dark:bg-gray-800 p-1.5 rounded-full shadow-sm">
                            <TrendIcon trend={cluster.trend} />
                        </div>
                        <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Trend</p>
                    </div>
                </div>

                {/* ── Expand toggle ── */}
                <button
                    onClick={onToggle}
                    className="w-full flex items-center justify-center gap-1.5 py-2 text-[12px] font-semibold text-indigo-500 dark:text-indigo-400 bg-indigo-50/50 dark:bg-indigo-900/20 hover:bg-indigo-100/60 dark:hover:bg-indigo-900/40 border-t border-gray-200/50 dark:border-gray-700/50 transition-colors flex-shrink-0"
                >
                    <ChevronDown size={13} className={`transition-transform duration-300 ${expanded ? 'rotate-180' : ''}`} />
                    {expanded ? 'Hide details' : 'View details + tweets'}
                </button>

                {/* ── Expandable details ── */}
                {expanded && (
                    <div className="border-t border-gray-200/50 dark:border-gray-700/50 bg-gray-50/80 dark:bg-gray-900/50 p-4 space-y-4 animate-fade-in-up">
                        <div className="space-y-2 text-[12px]">
                            <div className="flex gap-2">
                                <span className="text-gray-400 dark:text-gray-500 w-28 flex-shrink-0">Cluster ID</span>
                                <span className="text-gray-700 dark:text-gray-300 font-mono">{cluster.cluster_id}</span>
                            </div>
                            <div className="flex gap-2">
                                <span className="text-gray-400 dark:text-gray-500 w-28 flex-shrink-0">Full location</span>
                                <span className="text-gray-700 dark:text-gray-300">{cluster.location}</span>
                            </div>
                            <div className="flex gap-2">
                                <span className="text-gray-400 dark:text-gray-500 w-28 flex-shrink-0">Time window</span>
                                <span className="text-gray-700 dark:text-gray-300">{cluster.time_window}</span>
                            </div>
                            {assignedOfficer && (
                                <div className="flex gap-2">
                                    <span className="text-gray-400 dark:text-gray-500 w-28 flex-shrink-0">Assigned to</span>
                                    <span className="text-indigo-600 dark:text-indigo-400 font-medium">{assignedOfficer.name} ({assignedOfficer.designation})</span>
                                </div>
                            )}
                        </div>

                        {/* AI Recommendation box */}
                        <div className="rounded-xl border border-indigo-200/60 dark:border-indigo-700/40 bg-gradient-to-br from-indigo-50/80 to-purple-50/60 dark:from-indigo-950/50 dark:to-purple-950/30 p-3.5">
                            <div className="flex items-center gap-1.5 mb-2">
                                <Sparkles size={12} className="text-indigo-500" />
                                <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-500 dark:text-indigo-400">AI Recommendation</span>
                            </div>
                            <p className="text-[12.5px] text-indigo-800 dark:text-indigo-200 leading-relaxed">{cluster.recommended_action}</p>
                        </div>

                        <div>
                            <p className="text-[11px] text-gray-400 dark:text-gray-500 mb-2 flex items-center gap-1">
                                <XIcon size={11} /> Sample tweets
                            </p>
                            <div className="space-y-2">
                                {cluster.sample_tweets.map((tweet, i) => (
                                    <div key={i} className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2">
                                        <p className="text-[11px] font-medium text-blue-600 dark:text-blue-400 mb-0.5">{tweet.handle}</p>
                                        <p className="text-[12px] text-gray-600 dark:text-gray-300 leading-relaxed">{tweet.text}</p>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {cluster.status === 'resolved' && (
                            <PhotoStrip photos={cluster.resolved_photos} />
                        )}

                        {/* Action buttons */}
                        <div className="grid grid-cols-1 gap-2 pt-1">
                            {/* 1. Assign Officer */}
                            {assignedOfficer || currentStatus === 'inprogress' || currentStatus === 'resolved' ? (
                                <div className="flex items-center justify-center gap-2 py-2.5 rounded-xl text-[12.5px] font-semibold bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-300 border border-blue-100 dark:border-blue-800">
                                    <CheckCircle2 size={14} />
                                    {assignedOfficer ? `Assigned: ${assignedOfficer.name}` : 'Officer Assigned — In Progress'}
                                </div>
                            ) : (
                                <button
                                    onClick={() => setShowModal(true)}
                                    className="flex items-center justify-center gap-2 py-2.5 rounded-xl text-[12.5px] font-semibold bg-blue-600 hover:bg-blue-500 text-white transition-all duration-200 shadow-[0_4px_14px_rgba(37,99,235,0.35)] hover:shadow-[0_4px_18px_rgba(37,99,235,0.5)]"
                                >
                                    <ShieldCheck size={14} />
                                    Assign Officer
                                </button>
                            )}

                            {/* 2. Mail Department */}
                            <a
                                href={`mailto:${deptEmail}?subject=${mailSubject}&body=${mailBody}`}
                                className="flex items-center justify-center gap-2 py-2.5 rounded-xl text-[12.5px] font-semibold border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 shadow-sm transition-all duration-200"
                            >
                                <Mail size={14} />
                                Mail {cluster.department} Department
                            </a>

                            {/* 3. Discard Complaint */}
                            <button
                                onClick={handleDiscard}
                                className="flex items-center justify-center gap-2 py-2.5 rounded-xl text-[12.5px] font-semibold border border-red-400 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 hover:border-red-500 transition-all duration-200"
                            >
                                <Trash2 size={14} />
                                Discard Complaint
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </>
    )
}
