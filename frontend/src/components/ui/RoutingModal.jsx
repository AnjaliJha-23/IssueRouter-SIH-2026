import { useState, useEffect } from 'react'
import { X, Building2, Target, CheckCircle2, AlertCircle } from 'lucide-react'

export default function RoutingModal({ challenge, isOpen, onClose, onConfirm }) {
    const [matches, setMatches] = useState([]);
    const [selectedOrgId, setSelectedOrgId] = useState(null);
    const [loading, setLoading] = useState(false);
    const [note, setNote] = useState("");

    useEffect(() => {
        if (isOpen && challenge) {
            fetchMatches();
        } else {
            setMatches([]);
            setSelectedOrgId(null);
            setNote("");
        }
    }, [isOpen, challenge]);

    const fetchMatches = async () => {
        setLoading(true);
        try {
            const res = await fetch(`http://localhost:8000/api/matches/generate/${challenge.id}`, { method: 'POST' });
            if (res.ok) {
                const data = await res.json();
                setMatches(data);
                if (data.length > 0) {
                    setSelectedOrgId(data[0].org_id); // Auto-select highest match
                }
            }
        } catch (e) {
            console.error("Failed to generate matches", e);
        } finally {
            setLoading(false);
        }
    };

    const handleConfirm = () => {
        if (selectedOrgId) {
            onConfirm(challenge.id, selectedOrgId, note);
        }
    };

    if (!isOpen || !challenge) return null;

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
            <div className="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity" onClick={onClose} />
            
            <div className="bg-white dark:bg-neutral-900 rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden relative z-[61] animate-fade-in-up">
                
                {/* Header */}
                <div className="px-6 py-4 border-b border-neutral-200 dark:border-neutral-800 flex items-center justify-between bg-neutral-50/50 dark:bg-neutral-800/30">
                    <div>
                        <h2 className="text-lg font-bold text-neutral-900 dark:text-white flex items-center gap-2">
                            <Target className="text-blue-600 dark:text-blue-400" size={20} />
                            Route Challenge
                        </h2>
                        <p className="text-xs text-neutral-500 mt-0.5">{challenge.id} • {challenge.location}</p>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-neutral-200 dark:hover:bg-neutral-800 rounded-full transition-colors">
                        <X size={20} className="text-neutral-500" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    
                    {/* Universities List */}
                    <div>
                        <h3 className="text-sm font-bold text-neutral-900 dark:text-white mb-3 flex justify-between items-end">
                            Recommended Partners
                            {loading && <span className="text-xs text-blue-500 font-medium">Generating matches...</span>}
                        </h3>
                        
                        <div className="space-y-3 max-h-60 overflow-y-auto pr-1">
                            {!loading && matches.length === 0 && (
                                <div className="text-center py-6 bg-neutral-50 dark:bg-neutral-800/50 rounded-xl border border-dashed border-neutral-200 dark:border-neutral-700">
                                    <AlertCircle className="w-8 h-8 text-neutral-400 mx-auto mb-2" />
                                    <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400">No suitable matches found.</p>
                                    <p className="text-xs text-neutral-500 mt-1">Try routing manually to a broad department.</p>
                                </div>
                            )}

                            {matches.map(match => (
                                <div 
                                    key={match.org_id}
                                    onClick={() => setSelectedOrgId(match.org_id)}
                                    className={`
                                        p-4 rounded-xl border-2 cursor-pointer transition-all
                                        ${selectedOrgId === match.org_id 
                                            ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20' 
                                            : 'border-neutral-200 dark:border-neutral-700 hover:border-blue-300 dark:hover:border-blue-700'
                                        }
                                    `}
                                >
                                    <div className="flex justify-between items-start mb-2">
                                        <div className="flex items-center gap-2">
                                            <div className="w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center text-indigo-700 dark:text-indigo-400">
                                                <Building2 size={16} />
                                            </div>
                                            <div>
                                                <p className="text-sm font-bold text-neutral-900 dark:text-white leading-tight">
                                                    {match.organization?.name || "Partner Institution"}
                                                </p>
                                                <p className="text-[10px] uppercase font-bold text-neutral-500">
                                                    {match.organization?.type || "University"}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="flex flex-col items-end">
                                            <span className="text-sm font-bold text-blue-700 dark:text-blue-400">
                                                {match.match_score}% MATCH
                                            </span>
                                        </div>
                                    </div>
                                    <div className="pl-10 space-y-1">
                                        <p className="text-xs text-neutral-600 dark:text-neutral-400 flex items-center gap-1.5">
                                            <CheckCircle2 size={12} className="text-emerald-500" />
                                            {match.match_reason}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Routing Note */}
                    <div>
                        <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-2 uppercase tracking-wider">
                            Routing Note (Optional)
                        </label>
                        <textarea
                            value={note}
                            onChange={(e) => setNote(e.target.value)}
                            placeholder="Add any specific instructions for the receiving institution..."
                            className="w-full bg-neutral-50 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg p-3 text-sm text-neutral-900 dark:text-white outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 resize-none h-24"
                        />
                    </div>
                </div>

                {/* Footer */}
                <div className="px-6 py-4 border-t border-neutral-200 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-800/30 flex justify-end gap-3">
                    <button 
                        onClick={onClose}
                        className="px-5 py-2 text-sm font-bold text-neutral-600 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-white transition-colors"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleConfirm}
                        disabled={!selectedOrgId || loading}
                        className="px-6 py-2 rounded-lg text-sm font-bold bg-blue-600 hover:bg-blue-500 text-white transition-all shadow-lg shadow-blue-600/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                        Confirm Routing
                    </button>
                </div>
            </div>
        </div>
    )
}
