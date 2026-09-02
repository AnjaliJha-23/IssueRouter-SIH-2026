import { Search, X } from 'lucide-react'
import { clusters } from '../../data/Clusters'
import { useMemo } from 'react'

// Derive unique locations, departments and types from the data itself
const LOCATIONS = [...new Set(clusters.map((c) => c.location))].sort()
const DEPARTMENTS = [...new Set(clusters.map((c) => c.department))].sort()
const TYPES = [...new Set(clusters.map((c) => c.problem.split('—')[0].trim()))].sort()


function SelectWrapper({ children }) {
    return (
        <div className="relative">
            {children}
            <svg
                viewBox="0 0 12 12"
                fill="none"
                className="w-3 h-3 absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
            >
                <path d="M2 4L6 8L10 4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
            </svg>
        </div>
    )
}

export default function FilterBar({ filters, onChange }) {
    const { search, type, location, department } = filters

    const activeChips = useMemo(() => {
        const chips = []
        if (search) chips.push({ label: `"${search}"`, key: 'search' })
        if (type) chips.push({ label: type, key: 'type' })
        if (location) chips.push({ label: location, key: 'location' })
        if (department) chips.push({ label: department, key: 'department' })
        return chips
    }, [search, type, location, department])

    const set = (key, value) => onChange({ ...filters, [key]: value })

    const reset = () =>
        onChange({ search: '', type: '', location: '', department: '' })

    const baseSelect = `
    w-full h-[34px] pl-2.5 pr-7 text-[12px] appearance-none
    bg-gray-100 dark:bg-gray-700
    border border-transparent rounded-lg outline-none
    text-gray-700 dark:text-gray-200
    focus:border-indigo-400 focus:bg-white dark:focus:bg-gray-900
    transition-colors cursor-pointer
  `

    return (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-3.5 space-y-3">

            {/* ── Filter inputs row ──────────────────── */}
            <div className="flex flex-wrap gap-3 items-end">

                {/* Search */}
                <div className="flex flex-col gap-1 flex-1 min-w-[180px]">
                    <span className="text-[10px] uppercase tracking-wider text-gray-400 dark:text-gray-500">
                        Search cluster
                    </span>
                    <div className="relative">
                        <Search
                            size={13}
                            className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500 pointer-events-none"
                        />
                        <input
                            type="text"
                            value={search}
                            onChange={(e) => set('search', e.target.value)}
                            placeholder="Problem, location, cluster ID..."
                            className="
                w-full h-[34px] pl-8 pr-3 text-[12px]
                bg-gray-100 dark:bg-gray-700
                border border-transparent rounded-lg outline-none
                text-gray-700 dark:text-gray-200
                placeholder:text-gray-400 dark:placeholder:text-gray-500
                focus:border-indigo-400 focus:bg-white dark:focus:bg-gray-900
                transition-colors
              "
                        />
                    </div>
                </div>

                {/* Complaint type */}
                <div className="flex flex-col gap-1 min-w-[140px]">
                    <span className="text-[10px] uppercase tracking-wider text-gray-400 dark:text-gray-500">
                        Complaint Type
                    </span>
                    <SelectWrapper>
                        <select
                            value={type}
                            onChange={(e) => set('type', e.target.value)}
                            className={baseSelect}
                        >
                            <option value="">All types</option>
                            {TYPES.map((t) => (
                                <option key={t} value={t}>{t}</option>
                            ))}
                        </select>
                    </SelectWrapper>
                </div>

                {/* Location */}
                <div className="flex flex-col gap-1 min-w-[140px]">
                    <span className="text-[10px] uppercase tracking-wider text-gray-400 dark:text-gray-500">
                        Location
                    </span>
                    <SelectWrapper>
                        <select
                            value={location}
                            onChange={(e) => set('location', e.target.value)}
                            className={baseSelect}
                        >
                            <option value="">All locations</option>
                            {LOCATIONS.map((loc) => (
                                <option key={loc} value={loc}>{loc}</option>
                            ))}
                        </select>
                    </SelectWrapper>
                </div>

                {/* Department */}
                <div className="flex flex-col gap-1 min-w-[120px]">
                    <span className="text-[10px] uppercase tracking-wider text-gray-400 dark:text-gray-500">
                        Department
                    </span>
                    <SelectWrapper>
                        <select
                            value={department}
                            onChange={(e) => set('department', e.target.value)}
                            className={baseSelect}
                        >
                            <option value="">All departments</option>
                            {DEPARTMENTS.map((dept) => (
                                <option key={dept} value={dept}>{dept}</option>
                            ))}
                        </select>
                    </SelectWrapper>
                </div>

                {/* Clear all */}
                {activeChips.length > 0 && (
                    <button
                        onClick={reset}
                        className="
              h-[34px] px-3.5 text-[12px] self-end flex-shrink-0
              border border-gray-200 dark:border-gray-600 rounded-lg
              text-gray-500 dark:text-gray-400
              hover:bg-gray-100 dark:hover:bg-gray-700
              transition-colors
            "
                    >
                        Clear all
                    </button>
                )}
            </div>

            {/* ── Active filter chips ────────────────── */}
            {activeChips.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                    {activeChips.map(({ label, key }) => (
                        <span
                            key={key}
                            className="inline-flex items-center gap-1.5 text-[11px] bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 pl-2.5 pr-1.5 py-1 rounded-full"
                        >
                            {label}
                            <button
                                onClick={() => set(key, '')}
                                className="hover:text-indigo-900 dark:hover:text-indigo-100 transition-colors"
                            >
                                <X size={11} />
                            </button>
                        </span>
                    ))}
                </div>
            )}
        </div>
    )
}