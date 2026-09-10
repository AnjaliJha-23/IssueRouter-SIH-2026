import {
    MapPin,
    Building2,
    ShieldCheck,
    ArrowRight,
    Sparkles,
    GraduationCap,
    Clock,
    CheckCircle2,
    Share2,
    Users,
    Check,
    Image as ImageIcon
} from 'lucide-react'

const getPriorityBadge = (score) => {
    if (score >= 85) {
        return {
            label: `CRITICAL · ${score}`,
            style: 'bg-rose-50 text-rose-700 border-rose-200/80 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-900/50'
        }
    }
    if (score >= 70) {
        return {
            label: `HIGH · ${score}`,
            style: 'bg-amber-50 text-amber-700 border-amber-200/80 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-900/50'
        }
    }
    if (score >= 50) {
        return {
            label: `MEDIUM · ${score}`,
            style: 'bg-blue-50 text-blue-700 border-blue-200/80 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-900/50'
        }
    }
    return {
        label: `LOW · ${score}`,
        style: 'bg-neutral-100 text-neutral-600 border-neutral-200 dark:bg-neutral-800 dark:text-neutral-400 dark:border-neutral-700'
    }
}

const STATUS_CONFIG = {
    pending_verification: {
        label: 'Pending Verification',
        badge: 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/30 dark:text-amber-400 dark:border-amber-900/40',
        nextActionLabel: 'Review Evidence → Verify',
        nextActionType: 'verify'
    },
    verified: {
        label: 'Verified',
        badge: 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/30 dark:text-blue-400 dark:border-blue-900/40',
        nextActionLabel: 'Review Matches & Route',
        nextActionType: 'route'
    },
    matches_suggested: {
        label: 'Matches Suggested',
        badge: 'bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950/30 dark:text-purple-400 dark:border-purple-900/40',
        nextActionLabel: 'Select Universities → Route',
        nextActionType: 'route'
    },
    ready_for_routing: {
        label: 'Ready for Routing',
        badge: 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/30 dark:text-emerald-400 dark:border-emerald-900/40',
        nextActionLabel: 'Route Challenge',
        nextActionType: 'route'
    },
    routed: {
        label: 'Routed',
        badge: 'bg-indigo-50 text-indigo-700 border-indigo-200 dark:bg-indigo-950/30 dark:text-indigo-400 dark:border-indigo-900/40',
        nextActionLabel: 'Track Progress',
        nextActionType: 'track'
    },
    in_project: {
        label: 'Active Project',
        badge: 'bg-teal-50 text-teal-700 border-teal-200 dark:bg-teal-950/30 dark:text-teal-400 dark:border-teal-900/40',
        nextActionLabel: 'View Project Workspace',
        nextActionType: 'track'
    },
    resolved: {
        label: 'Resolved',
        badge: 'bg-gray-100 text-gray-700 border-gray-200 dark:bg-neutral-800 dark:text-gray-300 dark:border-neutral-700',
        nextActionLabel: 'View Audit Dossier',
        nextActionType: 'view'
    }
}

export default function ChallengeCard({ challenge, rank, onToggle, onVerify }) {
    const priority = getPriorityBadge(challenge.priority_score || 0)
    const statusCfg = STATUS_CONFIG[challenge.status] || STATUS_CONFIG.pending_verification

    // University summary derivation
    const matches = challenge.matches || []
    const topMatch = matches.length > 0 ? matches[0] : null
    const additionalMatches = matches.length > 1 ? matches.length - 1 : 0

    const handleActionClick = (e) => {
        e.stopPropagation()
        if (onVerify) {
            onVerify(challenge)
        }
    }

    return (
        <div
            onClick={onToggle}
            className="group relative flex flex-col justify-between bg-white dark:bg-neutral-900/90 rounded-xl border border-neutral-200/90 dark:border-neutral-800/90 hover:border-blue-500/50 dark:hover:border-blue-500/40 shadow-2xs hover:shadow-lg hover:shadow-blue-500/5 dark:hover:shadow-blue-500/10 hover:-translate-y-0.5 transition-all duration-200 cursor-pointer overflow-hidden h-full"
        >
            {/* ── Top Header Bar ── */}
            <div className="p-4 pb-2.5">
                <div className="flex items-center justify-between gap-2 mb-2">
                    <div className="flex items-center gap-1.5">
                        <span className="text-[10px] font-bold text-neutral-400 dark:text-neutral-500 px-1.5 py-0.5 rounded bg-neutral-100 dark:bg-neutral-800/80">
                            #{rank}
                        </span>
                        <span className="font-mono text-[11px] font-semibold text-neutral-500 dark:text-neutral-400">
                            {challenge.id?.slice(0, 13)}
                        </span>
                    </div>
                    <div className="flex items-center gap-1.5">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border tracking-wide uppercase ${priority.style}`}>
                            {priority.label}
                        </span>
                    </div>
                </div>

                {/* ── Title & Description ── */}
                <h3 className="text-[14.5px] font-bold text-neutral-900 dark:text-white leading-snug group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors line-clamp-2">
                    {challenge.title}
                </h3>
                <p className="text-[12px] text-neutral-500 dark:text-neutral-400 leading-relaxed mt-1 line-clamp-2">
                    {challenge.description || challenge.official_description}
                </p>

                {/* ── Location & Domain Tags ── */}
                <div className="flex flex-wrap items-center gap-1.5 mt-3">
                    <span className="inline-flex items-center gap-1 text-[10.5px] font-semibold bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 px-2 py-0.5 rounded border border-neutral-200/60 dark:border-neutral-700/60">
                        <Building2 size={11} className="text-neutral-400" />
                        {challenge.domain || challenge.department || 'General'}
                    </span>
                    <span className="inline-flex items-center gap-1 text-[10.5px] font-semibold bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 px-2 py-0.5 rounded border border-neutral-200/60 dark:border-neutral-700/60">
                        <MapPin size={11} className="text-neutral-400" />
                        {(challenge.location || 'Jharkhand').split(',')[0]}
                    </span>
                    <span className={`inline-flex items-center text-[10px] font-semibold px-2 py-0.5 rounded border uppercase ml-auto ${statusCfg.badge}`}>
                        {statusCfg.label}
                    </span>
                </div>
            </div>

            {/* ── Mid Section: Evidence & Intelligence Signals ── */}
            <div className="px-4 py-2.5 bg-neutral-50/70 dark:bg-neutral-800/40 border-t border-neutral-100 dark:border-neutral-800/60 flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-3 text-neutral-600 dark:text-neutral-300 font-medium">
                    <span className="flex items-center gap-1">
                        <Share2 size={11} className="text-blue-500" />
                        <span>{challenge.source_counts?.social || 0}</span>
                        <span className="text-neutral-400 text-[10px]">Social</span>
                    </span>
                    <span className="flex items-center gap-1">
                        <Users size={11} className="text-emerald-500" />
                        <span>{challenge.source_counts?.citizen || challenge.complaint_count || 1}</span>
                        <span className="text-neutral-400 text-[10px]">Citizen</span>
                    </span>
                    {challenge.media_urls && challenge.media_urls.length > 0 && (
                        <span className="inline-flex items-center gap-1 text-purple-600 dark:text-purple-400 font-semibold bg-purple-50 dark:bg-purple-950/40 px-1.5 py-0.5 rounded border border-purple-200/60 dark:border-purple-800/40 text-[10.5px]">
                            <ImageIcon size={11} />
                            <span>{challenge.media_urls.length}</span>
                            <span className="text-purple-500/80 dark:text-purple-400 text-[9.5px]">
                                {challenge.media_urls.length === 1 ? 'Photo' : 'Photos'}
                            </span>
                        </span>
                    )}
                </div>
                <div className="flex items-center gap-1 text-[11px] font-semibold text-neutral-600 dark:text-neutral-300">
                    <Sparkles size={11} className="text-indigo-500" />
                    <span>AI Conf. {Math.round((challenge.ai_confidence || 0.92) * 100)}%</span>
                </div>
            </div>

            {/* ── Compact University Match Info (State-Driven) ── */}
            {topMatch ? (
                <div className="px-4 py-2 bg-blue-50/40 dark:bg-blue-950/20 border-t border-blue-100/60 dark:border-blue-900/30 flex items-center justify-between text-[11px]">
                    <div className="flex items-center gap-1.5 truncate mr-2">
                        <GraduationCap size={13} className="text-blue-600 dark:text-blue-400 flex-shrink-0" />
                        <span className="font-semibold text-neutral-800 dark:text-neutral-200 truncate">
                            {topMatch.organization?.name || "Matched Partner"}
                        </span>
                    </div>
                    <div className="flex items-center gap-1.5 flex-shrink-0">
                        <span className="font-bold text-blue-700 dark:text-blue-300">
                            {topMatch.match_score}%
                        </span>
                        {additionalMatches > 0 && (
                            <span className="text-[10px] text-neutral-400 font-medium">
                                +{additionalMatches} more
                            </span>
                        )}
                    </div>
                </div>
            ) : challenge.status === 'routed' && challenge.active_deadline ? (
                <div className="px-4 py-2 bg-indigo-50/40 dark:bg-indigo-950/20 border-t border-indigo-100/60 dark:border-indigo-900/30 flex items-center justify-between text-[11px]">
                    <span className="flex items-center gap-1.5 font-medium text-indigo-800 dark:text-indigo-200">
                        <Clock size={12} className="text-indigo-500" />
                        Routed to Universities
                    </span>
                    <span className="text-[10.5px] font-semibold text-indigo-700 dark:text-indigo-300">
                        Deadline: {new Date(challenge.active_deadline).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                    </span>
                </div>
            ) : null}

            {/* ── Action Footer: Next Action Callout ── */}
            <div className="px-4 py-2.5 border-t border-neutral-100 dark:border-neutral-800/80 bg-white dark:bg-neutral-900 flex items-center justify-between">
                <div className="flex flex-col">
                    <span className="text-[9.5px] font-bold uppercase tracking-wider text-neutral-400">
                        Next Action
                    </span>
                    <span className="text-[11.5px] font-bold text-neutral-800 dark:text-neutral-200 flex items-center gap-1">
                        {statusCfg.nextActionLabel}
                    </span>
                </div>
                <button
                    onClick={handleActionClick}
                    className={`
                        inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-bold transition-all shadow-2xs
                        ${statusCfg.nextActionType === 'verify'
                            ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-600/20'
                            : 'bg-blue-600 hover:bg-blue-500 text-white shadow-blue-600/20'
                        }
                    `}
                >
                    {statusCfg.nextActionType === 'verify' && <ShieldCheck size={12} />}
                    {statusCfg.nextActionType === 'route' && <ArrowRight size={12} />}
                    {statusCfg.nextActionType === 'track' && <Check size={12} />}
                    <span>Proceed</span>
                </button>
            </div>
        </div>
    )
}
