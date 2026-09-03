import { Search, X } from 'lucide-react'
import { useMemo } from 'react'
import { JHARKHAND_DISTRICTS, DOMAINS, PRIORITIES } from '../../data/geography'

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
    const { search, domain, district, priority } = filters

    const activeChips = useMemo(() => {
        const chips = []
        if (search) chips.push({ label: `"${search}"`, key: 'search' })
        if (domain) chips.push({ label: domain, key: 'domain' })
        if (district) chips.push({ label: district, key: 'district' })
        if (priority) {
            const priorityLabel = PRIORITIES.find(p => p.value === priority)?.label || priority;
            chips.push({ label: priorityLabel, key: 'priority' });
        }
        return chips
    }, [search, domain, district, priority])

    const set = (key, value) => onChange({ ...filters, [key]: value })

    const reset = () =>
        onChange({ search: '', domain: '', district: '', priority: '' })

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
                        Search challenge
                    </span>
                    <div className="relative">
                        <Search
                            size={13}
                            className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500 pointer-events-none"
                        />
                        <input
                            type="text"
                            value={search || ''}
                            onChange={(e) => set('search', e.target.value)}
                            placeholder="Problem, location, challenge ID..."
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

                {/* Domain */}
                <div className="flex flex-col gap-1 min-w-[140px]">
                    <span className="text-[10px] uppercase tracking-wider text-gray-400 dark:text-gray-500">
                        Domain
                    </span>
                    <SelectWrapper>
                        <select
                            value={domain || ''}
                            onChange={(e) => set('domain', e.target.value)}
                            className={baseSelect}
                        >
                            <option value="">All Domains</option>
                            {DOMAINS.map((d) => (
                                <option key={d} value={d}>{d}</option>
                            ))}
                        </select>
                    </SelectWrapper>
                </div>

                {/* District */}
                <div className="flex flex-col gap-1 min-w-[140px]">
                    <span className="text-[10px] uppercase tracking-wider text-gray-400 dark:text-gray-500">
                        District
                    </span>
                    <SelectWrapper>
                        <select
                            value={district || ''}
                            onChange={(e) => set('district', e.target.value)}
                            className={baseSelect}
                        >
                            <option value="">Jharkhand (All)</option>
                            {JHARKHAND_DISTRICTS.map((loc) => (
                                <option key={loc} value={loc}>{loc}</option>
                            ))}
                        </select>
                    </SelectWrapper>
                </div>

                {/* Priority */}
                <div className="flex flex-col gap-1 min-w-[120px]">
                    <span className="text-[10px] uppercase tracking-wider text-gray-400 dark:text-gray-500">
                        Priority
                    </span>
                    <SelectWrapper>
                        <select
                            value={priority || ''}
                            onChange={(e) => set('priority', e.target.value)}
                            className={baseSelect}
                        >
                            <option value="">All priorities</option>
                            {PRIORITIES.map((p) => (
                                <option key={p.value} value={p.value}>{p.label}</option>
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