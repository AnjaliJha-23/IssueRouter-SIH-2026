import { useState } from 'react'
import {
    ChevronDown,
    MapPin,
    Building2,
    TrendingUp,
    TrendingDown,
    Minus,
    CheckCircle2,
    ShieldCheck,
    Target
} from 'lucide-react'

const PRIORITY_STYLES = {
    85: { rank: 'bg-red-50 text-red-800', card: 'border-l-4 border-l-red-500' },
    70: { rank: 'bg-orange-50 text-orange-800', card: 'border-l-4 border-l-orange-400' },
    50: { rank: 'bg-blue-50 text-blue-800', card: 'border-l-4 border-l-blue-400' },
    0:  { rank: 'bg-gray-100 text-gray-600', card: 'border-l-4 border-l-gray-300' },
}

const getPriorityStyle = (score) => {
    if (score >= 85) return PRIORITY_STYLES[85]
    if (score >= 70) return PRIORITY_STYLES[70]
    if (score >= 50) return PRIORITY_STYLES[50]
    return PRIORITY_STYLES[0]
}

const getSeverity = (score) => {
    if (score >= 85) return { label: 'Critical', bg: 'bg-red-500/10 border border-red-500/30 text-red-600 dark:text-red-400', dot: 'bg-red-500 shadow-[0_0_6px_rgba(239,68,68,0.8)]' }
    if (score >= 70) return { label: 'High',     bg: 'bg-orange-500/10 border border-orange-500/30 text-orange-600 dark:text-orange-400', dot: 'bg-orange-500 shadow-[0_0_6px_rgba(249,115,22,0.8)]' }
    if (score >= 50) return { label: 'Medium',   bg: 'bg-blue-500/10 border border-blue-500/30 text-blue-600 dark:text-blue-400', dot: 'bg-blue-500 shadow-[0_0_6px_rgba(59,130,246,0.6)]' }
    return { label: 'Low',      bg: 'bg-gray-500/10 border border-gray-500/30 text-gray-600 dark:text-gray-400', dot: 'bg-gray-400' }
}

const STATUS_STYLES = {
    pending: 'bg-yellow-50 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    verified: 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
    matched: 'bg-purple-50 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
    in_project: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
    resolved: 'bg-gray-50 text-gray-700 dark:bg-gray-800 dark:text-gray-400',
}

const STATUS_LABELS = {
    pending: 'Pending Verification',
    verified: 'Verified & Routing',
    matched: 'Matches Suggested',
    in_project: 'Active Project',
    resolved: 'Resolved',
}

function TrendIcon({ trend }) {
    if (trend === 'up') return <TrendingUp size={14} className="text-red-500" />
    if (trend === 'down') return <TrendingDown size={14} className="text-emerald-600" />
    return <Minus size={14} className="text-gray-400" />
}

export default function ChallengeCard({ challenge, rank, expanded, onToggle, onVerify }) {
    const ps = getPriorityStyle(challenge.priority_score)
    const sev = getSeverity(challenge.priority_score)
    const liveStatusStyle = STATUS_STYLES[challenge.status] || STATUS_STYLES.pending
    const liveStatusLabel = STATUS_LABELS[challenge.status] || challenge.status

    return (
        <div className={`flex flex-col bg-white dark:bg-neutral-800 rounded-xl overflow-hidden shadow-sm border border-neutral-200 dark:border-neutral-700 ${ps.card} transition-all duration-300 h-full`}>
            {/* ── Card body ── */}
            <div className="p-4 relative flex flex-col flex-1">
                <div className={`absolute top-0 left-0 w-7 h-7 flex items-center justify-center text-[11px] font-semibold rounded-br-lg ${ps.rank}`}>
                    #{rank}
                </div>

                <div className="pl-6 flex flex-col flex-1 gap-2">
                    <div className="flex flex-wrap items-center gap-2">
                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold tracking-wide ${sev.bg}`}>
                            <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${sev.dot}`} />
                            {sev.label} ({challenge.priority_score})
                        </span>
                        <span className={`inline-flex items-center text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${liveStatusStyle}`}>
                            {liveStatusLabel}
                        </span>
                    </div>

                    <p className="text-[15px] font-bold text-neutral-900 dark:text-white leading-snug line-clamp-2 mt-1">
                        {challenge.title}
                    </p>
                    <p className="text-[12.5px] text-neutral-600 dark:text-neutral-400 leading-relaxed line-clamp-2 flex-1 mt-1">
                        {challenge.description}
                    </p>

                    <div className="flex flex-wrap gap-1.5 pt-2">
                        <span className="inline-flex items-center gap-1 text-[10px] uppercase font-bold bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-2 py-1 rounded-md border border-blue-200/50 dark:border-blue-700/30">
                            <Building2 size={12} />
                            {challenge.department || challenge.domain || 'General'}
                        </span>
                        <span className="inline-flex items-center gap-1 text-[10px] uppercase font-bold bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 px-2 py-1 rounded-md border border-neutral-200 dark:border-neutral-700">
                            <MapPin size={12} />
                            {challenge.location.split(',')[0]}
                        </span>
                    </div>
                </div>
            </div>

            {/* ── Stats row ── */}
            <div className="grid grid-cols-3 border-t border-neutral-100 dark:border-neutral-700/50 bg-neutral-50/50 dark:bg-neutral-800/30 flex-shrink-0">
                <div className="py-3 text-center border-r border-neutral-100 dark:border-neutral-700/50">
                    <p className="text-xl font-bold bg-gradient-to-br from-neutral-800 to-neutral-500 bg-clip-text text-transparent dark:from-white dark:to-neutral-400">
                        {challenge.complaint_count}
                    </p>
                    <p className="text-[9px] font-bold text-neutral-400 mt-0.5 uppercase tracking-wider">Reports</p>
                </div>
                <div className="py-3 text-center border-r border-neutral-100 dark:border-neutral-700/50">
                    <p className="text-xl font-bold bg-gradient-to-br from-neutral-800 to-neutral-500 bg-clip-text text-transparent dark:from-white dark:to-neutral-400">
                        {challenge.rt_reach.toLocaleString()}
                    </p>
                    <p className="text-[9px] font-bold text-neutral-400 mt-0.5 uppercase tracking-wider">Reach</p>
                </div>
                <div className="py-3 flex flex-col items-center justify-center gap-1">
                    <div className="bg-white dark:bg-neutral-700 p-1 rounded shadow-sm border border-neutral-100 dark:border-neutral-600">
                        <TrendIcon trend={challenge.trend} />
                    </div>
                    <p className="text-[9px] font-bold text-neutral-400 uppercase tracking-wider">Trend</p>
                </div>
            </div>

            {/* ── Expand toggle ── */}
            <button
                onClick={onToggle}
                className="w-full flex items-center justify-center gap-1.5 py-2.5 text-[11px] font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400 bg-blue-50/50 dark:bg-blue-900/10 hover:bg-blue-100/60 dark:hover:bg-blue-900/30 border-t border-neutral-100 dark:border-neutral-700/50 transition-colors flex-shrink-0"
            >
                <ChevronDown size={14} className={`transition-transform duration-300 ${expanded ? 'rotate-180' : ''}`} />
                {expanded ? 'Hide details' : 'View Action Details'}
            </button>

            {/* ── Expandable details ── */}
            {expanded && (
                <div className="border-t border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-900/50 p-4 space-y-4 animate-fade-in-up">
                    <div className="space-y-2 text-[12px]">
                        <div className="flex gap-2">
                            <span className="text-neutral-500 w-24 flex-shrink-0 font-medium">Challenge ID</span>
                            <span className="text-neutral-900 dark:text-neutral-300 font-mono text-[10px] bg-neutral-200 dark:bg-neutral-800 px-1 rounded">{challenge.id}</span>
                        </div>
                        <div className="flex gap-2">
                            <span className="text-neutral-500 w-24 flex-shrink-0 font-medium">Full location</span>
                            <span className="text-neutral-900 dark:text-neutral-300 font-medium">{challenge.location}</span>
                        </div>
                        <div className="flex gap-2">
                            <span className="text-neutral-500 w-24 flex-shrink-0 font-medium">Submitted</span>
                            <span className="text-neutral-900 dark:text-neutral-300 font-medium">{new Date(challenge.created_at).toLocaleString()}</span>
                        </div>
                    </div>

                    {/* Action buttons */}
                    <div className="pt-2">
                        {challenge.status === 'pending' ? (
                            <button
                                onClick={onVerify}
                                className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg text-xs font-bold bg-green-600 hover:bg-green-500 text-white transition-all duration-200 shadow shadow-green-600/20"
                            >
                                <ShieldCheck size={16} />
                                Verify & Send to Smart Router
                            </button>
                        ) : challenge.status === 'verified' || challenge.status === 'matched' ? (
                            <div className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg text-xs font-bold bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800">
                                <Target size={16} />
                                Routing to Organizations...
                            </div>
                        ) : (
                            <div className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg text-xs font-bold bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                                <CheckCircle2 size={16} />
                                Project Formed & Active
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}
