import { useState, useEffect, useMemo } from 'react'
import { X, Building2, Target, CheckCircle2, AlertCircle, Clock, Search, Plus } from 'lucide-react'

export default function RoutingModal({ challenge, isOpen, onClose, onConfirm }) {
    const [matches, setMatches] = useState([])
    const [allUniversities, setAllUniversities] = useState([])
    const [selectedOrgIds, setSelectedOrgIds] = useState(new Set())
    
    const [loadingMatches, setLoadingMatches] = useState(false)
    const [loadingAll, setLoadingAll] = useState(false)
    
    const [note, setNote] = useState("")
    const [deadlineOption, setDeadlineOption] = useState("7") // days
    const [customDate, setCustomDate] = useState("")
    const [searchQuery, setSearchQuery] = useState("")

    useEffect(() => {
        if (isOpen && challenge) {
            fetchMatches()
            fetchAllUniversities()
            setSelectedOrgIds(new Set())
            setNote("")
            setDeadlineOption("7")
            setCustomDate("")
            setSearchQuery("")
        }
    }, [isOpen, challenge])

    const fetchMatches = async () => {
        setLoadingMatches(true)
        try {
            const res = await fetch(`http://localhost:8000/api/matches/generate/${challenge.id}`, { method: 'POST' })
            if (res.ok) {
                const data = await res.json()
                setMatches(data)
                // Auto-select top matches (e.g. top 3)
                const topIds = new Set(data.slice(0, 3).map(m => m.org_id))
                setSelectedOrgIds(topIds)
            }
        } catch (e) {
            console.error("Failed to generate matches", e)
        } finally {
            setLoadingMatches(false)
        }
    }

    const fetchAllUniversities = async () => {
        setLoadingAll(true)
        try {
            const res = await fetch(`http://localhost:8000/api/universities/?status=ACTIVE`)
            if (res.ok) {
                setAllUniversities(await res.json())
            }
        } catch (e) {
            console.error(e)
        } finally {
            setLoadingAll(false)
        }
    }

    const handleConfirm = () => {
        if (selectedOrgIds.size > 0) {
            let finalDeadline = null
            if (deadlineOption === "custom") {
                if (!customDate) return // Prevent invalid date
                finalDeadline = new Date(customDate).toISOString()
            } else {
                const days = parseInt(deadlineOption)
                const date = new Date()
                date.setDate(date.getDate() + days)
                date.setHours(23, 59, 59, 999)
                finalDeadline = date.toISOString()
            }
            
            onConfirm(challenge.id, Array.from(selectedOrgIds), finalDeadline, note)
        }
    }

    const toggleSelection = (id) => {
        setSelectedOrgIds(prev => {
            const next = new Set(prev)
            if (next.has(id)) next.delete(id)
            else next.add(id)
            return next
        })
    }

    // Identify which universities to show in search results (excluding already matched ones)
    const matchIds = new Set(matches.map(m => m.org_id))
    const searchResults = useMemo(() => {
        if (!searchQuery.trim()) return []
        const term = searchQuery.toLowerCase()
        return allUniversities.filter(u => 
            !matchIds.has(u.id) && 
            (u.name.toLowerCase().includes(term) || (u.district && u.district.toLowerCase().includes(term)))
        )
    }, [allUniversities, matchIds, searchQuery])

    if (!isOpen || !challenge) return null

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
            <div className="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity" onClick={onClose} />
            
            <div className="bg-white dark:bg-neutral-900 rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden relative z-[61] animate-fade-in-up max-h-[90vh] flex flex-col">
                
                {/* Header */}
                <div className="px-6 py-4 border-b border-neutral-200 dark:border-neutral-800 flex items-center justify-between bg-neutral-50/50 dark:bg-neutral-800/30 flex-shrink-0">
                    <div>
                        <h2 className="text-lg font-bold text-neutral-900 dark:text-white flex items-center gap-2">
                            <Target className="text-blue-600 dark:text-blue-400" size={20} />
                            Route Challenge
                        </h2>
                        <p className="text-xs text-neutral-500 mt-0.5">{challenge.title} • {challenge.location}</p>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-neutral-200 dark:hover:bg-neutral-800 rounded-full transition-colors">
                        <X size={20} className="text-neutral-500" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto space-y-6 flex-1">
                    
                    {/* Deadline Section */}
                    <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800/50 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                        <div>
                            <h3 className="text-sm font-bold text-blue-900 dark:text-blue-200 flex items-center gap-1.5">
                                <Clock size={16} /> Response Deadline
                            </h3>
                            <p className="text-[11px] text-blue-700 dark:text-blue-400 mt-0.5">
                                Selected universities must respond before this deadline.
                            </p>
                        </div>
                        <div className="flex gap-2">
                            <select 
                                value={deadlineOption} 
                                onChange={(e) => setDeadlineOption(e.target.value)}
                                className="bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 text-sm rounded-lg px-3 py-1.5 outline-none font-semibold text-neutral-700 dark:text-neutral-200"
                            >
                                <option value="3">3 Days</option>
                                <option value="7">7 Days</option>
                                <option value="14">14 Days</option>
                                <option value="custom">Custom Date...</option>
                            </select>
                            {deadlineOption === "custom" && (
                                <input 
                                    type="date" 
                                    value={customDate}
                                    onChange={(e) => setCustomDate(e.target.value)}
                                    className="bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 text-sm rounded-lg px-3 py-1.5 outline-none font-semibold text-neutral-700 dark:text-neutral-200"
                                />
                            )}
                        </div>
                    </div>

                    {/* Universities List */}
                    <div>
                        <h3 className="text-sm font-bold text-neutral-900 dark:text-white mb-3 flex justify-between items-end">
                            Recommended Partners
                            {loadingMatches && <span className="text-xs text-blue-500 font-medium animate-pulse">Analyzing profiles...</span>}
                        </h3>
                        
                        <div className="space-y-3">
                            {!loadingMatches && matches.length === 0 && (
                                <div className="text-center py-6 bg-neutral-50 dark:bg-neutral-800/50 rounded-xl border border-dashed border-neutral-200 dark:border-neutral-700">
                                    <AlertCircle className="w-8 h-8 text-neutral-400 mx-auto mb-2" />
                                    <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400">No strong automatic matches found.</p>
                                    <p className="text-xs text-neutral-500 mt-1">Browse the university directory below to select institutions manually.</p>
                                </div>
                            )}

                            {matches.map(match => (
                                <label 
                                    key={match.org_id}
                                    className={`
                                        flex items-start p-4 rounded-xl border-2 cursor-pointer transition-all
                                        ${selectedOrgIds.has(match.org_id)
                                            ? 'border-blue-600 bg-blue-50/50 dark:bg-blue-900/10' 
                                            : 'border-neutral-200 dark:border-neutral-700 hover:border-blue-300 dark:hover:border-blue-700'
                                        }
                                    `}
                                >
                                    <div className="pt-0.5 mr-3">
                                        <input 
                                            type="checkbox" 
                                            className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-600"
                                            checked={selectedOrgIds.has(match.org_id)}
                                            onChange={() => toggleSelection(match.org_id)}
                                        />
                                    </div>
                                    <div className="flex-1">
                                        <div className="flex justify-between items-start mb-1">
                                            <p className="text-sm font-bold text-neutral-900 dark:text-white leading-tight">
                                                {match.organization?.name || "Partner Institution"}
                                            </p>
                                            <span className="text-sm font-bold text-blue-700 dark:text-blue-400">
                                                {match.match_score}%
                                            </span>
                                        </div>
                                        <p className="text-xs text-neutral-600 dark:text-neutral-400 flex items-center gap-1.5">
                                            <CheckCircle2 size={12} className="text-emerald-500 flex-shrink-0" />
                                            {match.match_reason}
                                        </p>
                                    </div>
                                </label>
                            ))}
                        </div>
                    </div>

                    {/* Manual Search */}
                    <div>
                        <h3 className="text-sm font-bold text-neutral-900 dark:text-white mb-3">Add from Directory</h3>
                        <div className="relative">
                            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder="Search university by name or location..."
                                className="w-full h-[40px] pl-9 pr-3 text-[13px] bg-neutral-50 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg outline-none text-neutral-700 dark:text-neutral-200 focus:border-blue-400 transition-colors"
                            />
                        </div>
                        {searchResults.length > 0 && (
                            <div className="mt-2 border border-neutral-200 dark:border-neutral-700 rounded-lg overflow-hidden divide-y divide-neutral-100 dark:divide-neutral-800">
                                {searchResults.slice(0, 4).map(uni => (
                                    <div key={uni.id} className="flex justify-between items-center p-3 bg-white dark:bg-neutral-900">
                                        <div>
                                            <p className="text-sm font-semibold text-neutral-800 dark:text-neutral-200">{uni.name}</p>
                                            <p className="text-[11px] text-neutral-500">{uni.location}</p>
                                        </div>
                                        <button 
                                            onClick={() => {
                                                toggleSelection(uni.id)
                                                setSearchQuery("") // clear search after add
                                            }}
                                            disabled={selectedOrgIds.has(uni.id)}
                                            className="px-3 py-1.5 text-xs font-semibold rounded-md flex items-center gap-1 bg-neutral-100 hover:bg-neutral-200 dark:bg-neutral-800 dark:hover:bg-neutral-700 text-neutral-700 dark:text-neutral-300 disabled:opacity-50"
                                        >
                                            <Plus size={12} /> {selectedOrgIds.has(uni.id) ? 'Added' : 'Add'}
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                        {/* Display manually selected universities that are not in the matches array */}
                        {Array.from(selectedOrgIds).filter(id => !matchIds.has(id)).map(id => {
                            const uni = allUniversities.find(u => u.id === id)
                            if (!uni) return null
                            return (
                                <div key={id} className="mt-3 flex items-start p-4 rounded-xl border-2 border-blue-600 bg-blue-50/50 dark:bg-blue-900/10 cursor-pointer">
                                    <div className="pt-0.5 mr-3">
                                        <input 
                                            type="checkbox" 
                                            className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-600"
                                            checked={true}
                                            onChange={() => toggleSelection(id)}
                                        />
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm font-bold text-neutral-900 dark:text-white leading-tight">
                                            {uni.name}
                                        </p>
                                        <p className="text-xs text-neutral-500 mt-0.5">Manually added • {uni.location}</p>
                                    </div>
                                </div>
                            )
                        })}
                    </div>

                    {/* Routing Note */}
                    <div>
                        <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-2 uppercase tracking-wider">
                            Routing Note (Optional)
                        </label>
                        <textarea
                            value={note}
                            onChange={(e) => setNote(e.target.value)}
                            placeholder="Add any specific instructions for the receiving institutions..."
                            className="w-full bg-neutral-50 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg p-3 text-sm text-neutral-900 dark:text-white outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 resize-none h-20"
                        />
                    </div>
                </div>

                {/* Footer */}
                <div className="px-6 py-4 border-t border-neutral-200 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-800/30 flex justify-between items-center flex-shrink-0">
                    <div className="text-sm font-semibold text-neutral-600 dark:text-neutral-400">
                        {selectedOrgIds.size} {selectedOrgIds.size === 1 ? 'University' : 'Universities'} Selected
                    </div>
                    <div className="flex gap-3">
                        <button 
                            onClick={onClose}
                            className="px-5 py-2 text-sm font-bold text-neutral-600 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-white transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={handleConfirm}
                            disabled={selectedOrgIds.size === 0 || loadingMatches || (deadlineOption === 'custom' && !customDate)}
                            className="px-6 py-2 rounded-lg text-sm font-bold bg-blue-600 hover:bg-blue-500 text-white transition-all shadow-lg shadow-blue-600/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                        >
                            Confirm & Route
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}
