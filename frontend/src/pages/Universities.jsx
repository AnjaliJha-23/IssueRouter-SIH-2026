import { useState, useEffect, useMemo } from 'react'
import { GraduationCap, MapPin, CheckCircle2, XCircle, Search, Filter, Plus, X, Building2, Activity, Pencil } from 'lucide-react'
import { authFetch } from '../api/client'

export default function Universities() {
    const [universities, setUniversities] = useState([])
    const [loading, setLoading] = useState(true)

    const [search, setSearch] = useState('')
    const [statusFilter, setStatusFilter] = useState('all')
    const [districtFilter, setDistrictFilter] = useState('all')
    const [domainFilter, setDomainFilter] = useState('all')

    const [selectedUni, setSelectedUni] = useState(null)
    const [isAdding, setIsAdding] = useState(false)
    const [isEditing, setIsEditing] = useState(false)

    // Form state
    const [formData, setFormData] = useState({
        name: '', location: '', district: '', research_domains: '', research_specializations: '', research_output: '', status: 'ACTIVE'
    })

    useEffect(() => {
        fetchUniversities()
    }, [])

    const fetchUniversities = async () => {
        setLoading(true)
        try {
            const res = await authFetch('/api/universities/')
            if (res.ok) setUniversities(await res.json())
        } catch (e) {
            console.error("Failed to fetch universities", e)
        } finally {
            setLoading(false)
        }
    }

    const filtered = useMemo(() => {
        return universities.filter(u => {
            const term = search.toLowerCase()
            const matchSearch = !search || 
                u.name.toLowerCase().includes(term) || 
                (u.location && u.location.toLowerCase().includes(term)) || 
                (u.research_domains && u.research_domains.toLowerCase().includes(term))
                
            const matchStatus = statusFilter === 'all' || u.status === statusFilter
            const matchDistrict = districtFilter === 'all' || u.district === districtFilter
            const matchDomain = domainFilter === 'all' || (u.research_domains && u.research_domains.includes(domainFilter))

            return matchSearch && matchStatus && matchDistrict && matchDomain
        })
    }, [universities, search, statusFilter, districtFilter, domainFilter])

    const districts = useMemo(() => {
        const d = new Set()
        universities.forEach(u => { if (u.district) d.add(u.district) })
        return Array.from(d).sort()
    }, [universities])

    const domains = useMemo(() => {
        const d = new Set()
        universities.forEach(u => {
            if (u.research_domains) {
                u.research_domains.split(',').forEach(item => d.add(item.trim()))
            }
        })
        return Array.from(d).sort()
    }, [universities])

    const counts = {
        total: universities.length,
        active: universities.filter(u => u.status === 'ACTIVE').length,
    }

    const handleSave = async () => {
        try {
            const url = isEditing 
                ? `/api/universities/${selectedUni.id}` 
                : '/api/universities/';
            const method = isEditing ? 'PUT' : 'POST';

            const res = await authFetch(url, {
                method,
                body: JSON.stringify(formData)
            })

            if (res.ok) {
                fetchUniversities()
                setIsAdding(false)
                setIsEditing(false)
                setSelectedUni(null)
            }
        } catch (e) {
            console.error("Failed to save", e)
        }
    }

    const handleToggleStatus = async (uni) => {
        const newStatus = uni.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE'
        try {
            const res = await authFetch(`/api/universities/${uni.id}/status?status=${newStatus}`, { method: 'PATCH' })
            if (res.ok) {
                const updated = await res.json()
                setUniversities(universities.map(u => u.id === updated.id ? updated : u))
                if (selectedUni?.id === updated.id) setSelectedUni(updated)
            }
        } catch(e) {
            console.error(e)
        }
    }

    const openEdit = (uni) => {
        setFormData({
            name: uni.name, location: uni.location || '', district: uni.district || '',
            research_domains: uni.research_domains || '', research_specializations: uni.research_specializations || '',
            research_output: uni.research_output || '', status: uni.status || 'ACTIVE'
        })
        setIsEditing(true)
    }

    return (
        <div className="space-y-5 relative">
            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-2">
                <div>
                    <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400 bg-clip-text text-transparent">
                        Jharkhand University Network
                    </h2>
                    <p className="text-[13px] font-medium text-gray-500 dark:text-gray-400 mt-1 max-w-2xl">
                        Manage universities participating in the societal innovation ecosystem and view their research capabilities, routing activity and active collaborations.
                    </p>
                </div>
                <button 
                    onClick={() => {
                        setFormData({name: '', location: '', district: '', research_domains: '', research_specializations: '', research_output: '', status: 'ACTIVE'})
                        setIsAdding(true)
                    }}
                    className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
                >
                    <Plus size={16} /> Add University
                </button>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="glass-panel p-4 flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-blue-50 dark:bg-blue-900/30">
                        <GraduationCap className="text-blue-600 dark:text-blue-400" size={20} />
                    </div>
                    <div>
                        <p className="text-[10px] uppercase tracking-wide text-gray-400 font-semibold mb-0.5">Total Universities</p>
                        <p className="text-2xl font-bold text-gray-800 dark:text-gray-100">{counts.total}</p>
                    </div>
                </div>
                <div className="glass-panel p-4 flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-emerald-50 dark:bg-emerald-900/30">
                        <CheckCircle2 className="text-emerald-600 dark:text-emerald-400" size={20} />
                    </div>
                    <div>
                        <p className="text-[10px] uppercase tracking-wide text-gray-400 font-semibold mb-0.5">Active Universities</p>
                        <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{counts.active}</p>
                    </div>
                </div>
                <div className="glass-panel p-4 flex items-center gap-3 opacity-60">
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-amber-50 dark:bg-amber-900/30">
                        <Activity className="text-amber-600 dark:text-amber-400" size={20} />
                    </div>
                    <div>
                        <p className="text-[10px] uppercase tracking-wide text-gray-400 font-semibold mb-0.5">Currently Receiving</p>
                        <p className="text-2xl font-bold text-amber-600 dark:text-amber-400">0</p>
                    </div>
                </div>
                <div className="glass-panel p-4 flex items-center gap-3 opacity-60">
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-purple-50 dark:bg-purple-900/30">
                        <Building2 className="text-purple-600 dark:text-purple-400" size={20} />
                    </div>
                    <div>
                        <p className="text-[10px] uppercase tracking-wide text-gray-400 font-semibold mb-0.5">Active Projects</p>
                        <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">0</p>
                    </div>
                </div>
            </div>

            <div className="glass-panel p-3.5 flex flex-wrap gap-3 items-center">
                <div className="relative flex-1 min-w-[200px]">
                    <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                        type="text"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search universities, locations, domains..."
                        className="w-full h-[36px] pl-9 pr-3 text-[13px] bg-gray-100 dark:bg-gray-700/50 border border-transparent rounded-lg outline-none text-gray-700 dark:text-gray-200 focus:border-blue-400 focus:bg-white dark:focus:bg-gray-800 transition-colors"
                    />
                </div>
                <div className="flex gap-2">
                    <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="h-[36px] px-3 text-[12px] bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg outline-none text-gray-700 dark:text-gray-200 cursor-pointer">
                        <option value="all">All Status</option>
                        <option value="ACTIVE">Active</option>
                        <option value="INACTIVE">Inactive</option>
                    </select>
                    <select value={districtFilter} onChange={(e) => setDistrictFilter(e.target.value)} className="h-[36px] px-3 text-[12px] bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg outline-none text-gray-700 dark:text-gray-200 cursor-pointer max-w-[150px] truncate">
                        <option value="all">All Districts</option>
                        {districts.map(d => <option key={d} value={d}>{d}</option>)}
                    </select>
                    <select value={domainFilter} onChange={(e) => setDomainFilter(e.target.value)} className="h-[36px] px-3 text-[12px] bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg outline-none text-gray-700 dark:text-gray-200 cursor-pointer max-w-[150px] truncate">
                        <option value="all">All Domains</option>
                        {domains.map(d => <option key={d} value={d}>{d}</option>)}
                    </select>
                </div>
            </div>

            <div className="glass-panel overflow-hidden">
                {loading ? (
                    <div className="p-8 text-center text-gray-500">Loading universities...</div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-gray-50 dark:bg-gray-800/50 border-b border-gray-100 dark:border-gray-700">
                                    <th className="px-5 py-3 text-[10px] font-bold uppercase tracking-wider text-gray-500">University</th>
                                    <th className="px-5 py-3 text-[10px] font-bold uppercase tracking-wider text-gray-500">Location</th>
                                    <th className="px-5 py-3 text-[10px] font-bold uppercase tracking-wider text-gray-500">Status</th>
                                    <th className="px-5 py-3 text-[10px] font-bold uppercase tracking-wider text-gray-500 hidden md:table-cell">Research Domains</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                                {filtered.map(uni => (
                                    <tr 
                                        key={uni.id} 
                                        onClick={() => setSelectedUni(uni)}
                                        className="hover:bg-gray-50 dark:hover:bg-gray-700/30 cursor-pointer transition-colors"
                                    >
                                        <td className="px-5 py-3 text-[13px] font-semibold text-gray-800 dark:text-gray-200">
                                            {uni.name}
                                        </td>
                                        <td className="px-5 py-3 text-[12px] text-gray-600 dark:text-gray-400">
                                            <div className="flex items-center gap-1.5">
                                                <MapPin size={12} className="text-gray-400" />
                                                {uni.location}
                                            </div>
                                        </td>
                                        <td className="px-5 py-3">
                                            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold ${uni.status === 'ACTIVE' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'}`}>
                                                {uni.status === 'ACTIVE' ? <CheckCircle2 size={10} /> : <XCircle size={10} />}
                                                {uni.status === 'ACTIVE' ? 'Active' : 'Inactive'}
                                            </span>
                                        </td>
                                        <td className="px-5 py-3 text-[12px] text-gray-500 truncate max-w-[300px] hidden md:table-cell">
                                            {uni.research_domains}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {filtered.length === 0 && (
                            <div className="p-8 text-center text-gray-500 text-sm">No universities match the filters.</div>
                        )}
                    </div>
                )}
            </div>

            {/* View Detail Drawer */}
            {selectedUni && !isEditing && (
                <div className="fixed inset-y-0 right-0 w-full sm:w-[450px] bg-white dark:bg-neutral-900 shadow-2xl z-50 border-l border-neutral-200 dark:border-neutral-800 flex flex-col transform transition-transform duration-300">
                    <div className="px-6 py-5 border-b border-neutral-100 dark:border-neutral-800 flex justify-between items-start bg-neutral-50 dark:bg-neutral-900/50">
                        <div>
                            <h3 className="text-lg font-bold text-neutral-900 dark:text-white leading-tight pr-4">{selectedUni.name}</h3>
                            <div className="flex items-center gap-3 mt-2">
                                <span className="flex items-center gap-1 text-xs text-neutral-500">
                                    <MapPin size={12} /> {selectedUni.location}, {selectedUni.district}
                                </span>
                                <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold ${selectedUni.status === 'ACTIVE' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-neutral-100 text-neutral-600 dark:bg-neutral-800 dark:text-neutral-400'}`}>
                                    {selectedUni.status === 'ACTIVE' ? '● Active' : '○ Inactive'}
                                </span>
                            </div>
                        </div>
                        <button onClick={() => setSelectedUni(null)} className="p-1.5 hover:bg-neutral-200 dark:hover:bg-neutral-800 rounded-lg text-neutral-500">
                            <X size={18} />
                        </button>
                    </div>

                    <div className="flex-1 overflow-y-auto p-6 space-y-6">
                        <div>
                            <h4 className="text-xs font-bold uppercase tracking-wider text-neutral-400 mb-2">Research Domains</h4>
                            <div className="flex flex-wrap gap-2">
                                {selectedUni.research_domains?.split(',').map(d => d.trim()).filter(Boolean).map(d => (
                                    <span key={d} className="px-2.5 py-1 rounded-md bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 text-xs font-semibold border border-blue-100 dark:border-blue-800/50">{d}</span>
                                ))}
                            </div>
                        </div>

                        <div>
                            <h4 className="text-xs font-bold uppercase tracking-wider text-neutral-400 mb-2">Research Output</h4>
                            <p className="text-sm text-neutral-700 dark:text-neutral-300 leading-relaxed bg-neutral-50 dark:bg-neutral-800/50 p-3 rounded-lg border border-neutral-100 dark:border-neutral-800">
                                {selectedUni.research_output || "Not specified."}
                            </p>
                        </div>

                        <div>
                            <h4 className="text-xs font-bold uppercase tracking-wider text-neutral-400 mb-2">Platform Activity</h4>
                            <div className="grid grid-cols-2 gap-3">
                                <div className="p-3 bg-neutral-50 dark:bg-neutral-800/50 rounded-lg border border-neutral-100 dark:border-neutral-800">
                                    <p className="text-xs text-neutral-500 mb-1">Challenges Received</p>
                                    <p className="text-lg font-bold text-neutral-800 dark:text-neutral-200">0</p>
                                </div>
                                <div className="p-3 bg-neutral-50 dark:bg-neutral-800/50 rounded-lg border border-neutral-100 dark:border-neutral-800">
                                    <p className="text-xs text-neutral-500 mb-1">Active Projects</p>
                                    <p className="text-lg font-bold text-neutral-800 dark:text-neutral-200">0</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="p-4 border-t border-neutral-100 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-900/50 flex gap-2">
                        <button 
                            onClick={() => openEdit(selectedUni)}
                            className="flex-1 flex justify-center items-center gap-2 px-4 py-2 bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg text-sm font-semibold hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors text-neutral-700 dark:text-neutral-200"
                        >
                            <Pencil size={14} /> Edit Details
                        </button>
                        <button 
                            onClick={() => handleToggleStatus(selectedUni)}
                            className={`flex-1 flex justify-center items-center gap-2 px-4 py-2 border rounded-lg text-sm font-semibold transition-colors ${selectedUni.status === 'ACTIVE' ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-900/50 text-red-600 dark:text-red-400 hover:bg-red-100' : 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-900/50 text-emerald-600 dark:text-emerald-400 hover:bg-emerald-100'}`}
                        >
                            {selectedUni.status === 'ACTIVE' ? 'Deactivate' : 'Activate'}
                        </button>
                    </div>
                </div>
            )}

            {/* Add / Edit Modal */}
            {(isAdding || isEditing) && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
                    <div className="bg-white dark:bg-neutral-900 rounded-2xl w-full max-w-lg shadow-xl overflow-hidden animate-fade-in-up">
                        <div className="px-6 py-4 border-b border-neutral-100 dark:border-neutral-800 flex justify-between items-center bg-neutral-50 dark:bg-neutral-900/50">
                            <h3 className="text-lg font-bold text-neutral-900 dark:text-white">
                                {isEditing ? 'Edit University' : 'Add University'}
                            </h3>
                            <button onClick={() => { setIsAdding(false); setIsEditing(false) }} className="p-1.5 hover:bg-neutral-200 dark:hover:bg-neutral-800 rounded-lg text-neutral-500">
                                <X size={18} />
                            </button>
                        </div>
                        <div className="p-6 space-y-4">
                            <div>
                                <label className="block text-xs font-bold text-neutral-600 dark:text-neutral-400 mb-1">University Name *</label>
                                <input required value={formData.name} onChange={e=>setFormData({...formData, name: e.target.value})} className="w-full px-3 py-2 bg-neutral-50 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg text-sm outline-none focus:border-blue-500" />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-xs font-bold text-neutral-600 dark:text-neutral-400 mb-1">Location *</label>
                                    <input required value={formData.location} onChange={e=>setFormData({...formData, location: e.target.value})} className="w-full px-3 py-2 bg-neutral-50 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg text-sm outline-none focus:border-blue-500" />
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-neutral-600 dark:text-neutral-400 mb-1">District *</label>
                                    <input required value={formData.district} onChange={e=>setFormData({...formData, district: e.target.value})} className="w-full px-3 py-2 bg-neutral-50 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg text-sm outline-none focus:border-blue-500" />
                                </div>
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-neutral-600 dark:text-neutral-400 mb-1">Research Domains (comma separated)</label>
                                <input value={formData.research_domains} onChange={e=>setFormData({...formData, research_domains: e.target.value})} className="w-full px-3 py-2 bg-neutral-50 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg text-sm outline-none focus:border-blue-500" placeholder="e.g. HealthTech, BioTech" />
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-neutral-600 dark:text-neutral-400 mb-1">Research Output</label>
                                <textarea value={formData.research_output} onChange={e=>setFormData({...formData, research_output: e.target.value})} className="w-full px-3 py-2 bg-neutral-50 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg text-sm outline-none focus:border-blue-500 h-20 resize-none" placeholder="Description of output..." />
                            </div>
                            {isAdding && (
                                <div>
                                    <label className="block text-xs font-bold text-neutral-600 dark:text-neutral-400 mb-1">Status</label>
                                    <select value={formData.status} onChange={e=>setFormData({...formData, status: e.target.value})} className="w-full px-3 py-2 bg-neutral-50 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg text-sm outline-none focus:border-blue-500">
                                        <option value="ACTIVE">ACTIVE</option>
                                        <option value="INACTIVE">INACTIVE</option>
                                    </select>
                                </div>
                            )}
                        </div>
                        <div className="px-6 py-4 border-t border-neutral-100 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-900/50 flex justify-end gap-3">
                            <button onClick={() => { setIsAdding(false); setIsEditing(false) }} className="px-4 py-2 text-sm font-semibold text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white transition-colors">Cancel</button>
                            <button onClick={handleSave} disabled={!formData.name || !formData.location} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-semibold transition-colors disabled:opacity-50">
                                Save University
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Selected overlay */}
            {selectedUni && !isEditing && (
                <div className="fixed inset-0 bg-black/20 z-40" onClick={() => setSelectedUni(null)} />
            )}
        </div>
    )
}
