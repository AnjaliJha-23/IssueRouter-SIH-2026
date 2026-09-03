import { X, MapPin, Building2, TrendingUp, AlertCircle, Sparkles, CheckCircle2 } from 'lucide-react'

export default function ChallengeDetailDrawer({ challenge, isOpen, onClose, onRoute }) {
    if (!isOpen || !challenge) return null;

    return (
        <>
            {/* Backdrop */}
            <div 
                className="fixed inset-0 bg-black/40 z-40 transition-opacity" 
                onClick={onClose}
            />

            {/* Drawer */}
            <div className="fixed top-0 right-0 h-full w-full max-w-2xl bg-white dark:bg-neutral-900 shadow-2xl z-50 flex flex-col transform transition-transform duration-300">
                
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-neutral-200 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-800/30">
                    <div className="flex items-center gap-3">
                        <span className="font-mono text-xs bg-neutral-200 dark:bg-neutral-700 text-neutral-600 dark:text-neutral-300 px-2 py-1 rounded">
                            {challenge.id}
                        </span>
                        <span className="text-xs font-bold uppercase tracking-wider text-neutral-500">
                            Challenge Intelligence
                        </span>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-neutral-200 dark:hover:bg-neutral-800 rounded-full transition-colors">
                        <X size={20} className="text-neutral-500" />
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 space-y-8">
                    
                    {/* Hero Section */}
                    <div>
                        <div className="flex items-center gap-2 mb-3">
                            <span className="px-3 py-1 rounded-full text-xs font-bold bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400">
                                Priority Score: {challenge.priority_score}
                            </span>
                            <span className="px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
                                {challenge.status.replace(/_/g, ' ').toUpperCase()}
                            </span>
                        </div>
                        <h2 className="text-2xl font-bold text-neutral-900 dark:text-white mb-2">
                            {challenge.title}
                        </h2>
                        <p className="text-[15px] text-neutral-600 dark:text-neutral-400 leading-relaxed">
                            {challenge.description}
                        </p>
                        
                        <div className="flex flex-wrap gap-4 mt-4 text-sm text-neutral-500 font-medium">
                            <div className="flex items-center gap-1.5">
                                <MapPin size={16} /> {challenge.location}
                            </div>
                            <div className="flex items-center gap-1.5">
                                <Building2 size={16} /> {challenge.domain || challenge.department}
                            </div>
                            <div className="flex items-center gap-1.5">
                                <AlertCircle size={16} /> Submitted {new Date(challenge.created_at).toLocaleDateString()}
                            </div>
                        </div>
                    </div>

                    {/* Evidence Gallery (Mock) */}
                    <div className="space-y-3">
                        <h3 className="text-sm font-bold uppercase tracking-wider text-neutral-900 dark:text-white flex items-center gap-2">
                            Challenge Evidence
                            <span className="bg-neutral-100 dark:bg-neutral-800 px-2 py-0.5 rounded text-xs">
                                {challenge.complaint_count} Total Reports
                            </span>
                        </h3>
                        
                        <div className="grid grid-cols-3 gap-3">
                            {/* We use mock gradients for images */}
                            <div className="aspect-video bg-gradient-to-br from-neutral-200 to-neutral-300 dark:from-neutral-700 dark:to-neutral-800 rounded-lg flex items-center justify-center text-xs font-medium text-neutral-500 shadow-inner">
                                Photo Evidence 1
                            </div>
                            <div className="aspect-video bg-gradient-to-bl from-neutral-200 to-neutral-300 dark:from-neutral-700 dark:to-neutral-800 rounded-lg flex items-center justify-center text-xs font-medium text-neutral-500 shadow-inner">
                                Photo Evidence 2
                            </div>
                            <div className="aspect-video bg-gradient-to-tr from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg border border-blue-100 dark:border-blue-800 flex flex-col items-center justify-center text-center p-2">
                                <span className="text-xl font-bold text-blue-600 dark:text-blue-400">{challenge.source_counts?.social || 0}</span>
                                <span className="text-[10px] uppercase font-bold text-blue-500">Social Signals</span>
                            </div>
                        </div>
                    </div>

                    {/* AI Analysis Panel */}
                    <div className="bg-indigo-50 dark:bg-indigo-900/10 border border-indigo-100 dark:border-indigo-800/50 rounded-xl p-5">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-sm font-bold uppercase tracking-wider text-indigo-900 dark:text-indigo-300 flex items-center gap-2">
                                <Sparkles size={16} />
                                AI Intelligence
                            </h3>
                            <span className="text-xs font-bold text-indigo-700 dark:text-indigo-400 bg-indigo-100 dark:bg-indigo-900/40 px-2 py-1 rounded">
                                Confidence: {Math.round((challenge.ai_confidence || 0) * 100)}%
                            </span>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-6">
                            <div>
                                <p className="text-xs font-semibold text-indigo-800/70 dark:text-indigo-300/70 mb-2">Priority Rationale</p>
                                <ul className="space-y-1.5 text-sm text-indigo-900 dark:text-indigo-200 font-medium">
                                    <li className="flex items-center justify-between">
                                        <span>Population Impact</span> <span className="text-green-600 dark:text-green-400">+25</span>
                                    </li>
                                    <li className="flex items-center justify-between">
                                        <span>Severity / Risk</span> <span className="text-green-600 dark:text-green-400">+20</span>
                                    </li>
                                    <li className="flex items-center justify-between">
                                        <span>Report Frequency</span> <span className="text-green-600 dark:text-green-400">+15</span>
                                    </li>
                                    <li className="flex items-center justify-between">
                                        <span>Verified Citizen Source</span> <span className="text-green-600 dark:text-green-400">+10</span>
                                    </li>
                                </ul>
                            </div>
                            
                            <div>
                                <p className="text-xs font-semibold text-indigo-800/70 dark:text-indigo-300/70 mb-2">Deduplication Engine</p>
                                <div className="bg-white/50 dark:bg-black/20 rounded-lg p-3">
                                    <p className="text-2xl font-bold text-indigo-900 dark:text-indigo-300">
                                        {Math.round((challenge.duplicate_risk || 0) * 100)}%
                                    </p>
                                    <p className="text-xs text-indigo-700 dark:text-indigo-400 mt-0.5">
                                        Duplicate Risk. No significant semantic matches found in active database.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Timeline / Routing */}
                    <div className="space-y-3">
                        <h3 className="text-sm font-bold uppercase tracking-wider text-neutral-900 dark:text-white">
                            Lifecycle
                        </h3>
                        <div className="border-l-2 border-neutral-200 dark:border-neutral-700 ml-2 pl-4 py-1 space-y-4">
                            <div className="relative">
                                <div className="absolute -left-[21px] top-0.5 w-2.5 h-2.5 rounded-full bg-blue-500 ring-4 ring-white dark:ring-neutral-900" />
                                <p className="text-sm font-bold text-neutral-900 dark:text-white">Challenge Detected</p>
                                <p className="text-xs text-neutral-500 mt-0.5">Aggregated from multiple sources.</p>
                            </div>
                            {challenge.verified && (
                                <div className="relative">
                                    <div className="absolute -left-[21px] top-0.5 w-2.5 h-2.5 rounded-full bg-green-500 ring-4 ring-white dark:ring-neutral-900" />
                                    <p className="text-sm font-bold text-neutral-900 dark:text-white">Government Verified</p>
                                    <p className="text-xs text-neutral-500 mt-0.5">Approved for university routing.</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Footer Actions */}
                <div className="p-4 border-t border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 flex justify-end gap-3">
                    <button 
                        onClick={onClose}
                        className="px-4 py-2 text-sm font-bold text-neutral-600 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-white transition-colors"
                    >
                        Close
                    </button>
                    {challenge.status === 'pending_verification' && (
                        <button
                            onClick={() => { onRoute(challenge.id); onClose(); }}
                            className="px-6 py-2 rounded-lg text-sm font-bold bg-green-600 hover:bg-green-500 text-white transition-all shadow-lg shadow-green-600/20 flex items-center gap-2"
                        >
                            <CheckCircle2 size={16} />
                            Verify Challenge
                        </button>
                    )}
                    {['verified', 'matches_suggested', 'ready_for_routing'].includes(challenge.status) && (
                        <button
                            onClick={() => { onRoute(challenge.id); onClose(); }}
                            className="px-6 py-2 rounded-lg text-sm font-bold bg-blue-600 hover:bg-blue-500 text-white transition-all shadow-lg shadow-blue-600/20 flex items-center gap-2"
                        >
                            View Matches & Route
                        </button>
                    )}
                </div>
            </div>
        </>
    )
}
