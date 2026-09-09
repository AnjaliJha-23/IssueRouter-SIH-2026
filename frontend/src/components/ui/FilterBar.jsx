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
    w-full h-[36px] pl-3 pr-8 text-[12.5px] appearance-none
    bg-neutral-50 dark:bg-neutral-800/90
    border border-neutral-200 dark:border-neutral-700 rounded-lg outline-none
    text-neutral-700 dark:text-neutral-200 font-medium
    focus:border-blue-500 focus:ring-1 focus:ring-blue-500/20 focus:bg-white dark:focus:bg-neutral-900
    transition-all cursor-pointer
  `

    return (
        <div className="bg-white dark:bg-neutral-900/80 backdrop-blur-md border border-neutral-200/80 dark:border-neutral-800 rounded-xl p-4 shadow-sm space-y-3">

            {/* ── Filter inputs row ──────────────────── */}
            <div className="flex flex-wrap gap-3 items-end">

                {/* Search */}
                <div className="flex flex-col gap-1.5 flex-1 min-w-[200px]">
                    <span className="text-[11px] font-semibold uppercase tracking-wider text-neutral-400 dark:text-neutral-500">
                        Search Challenges
                    </span>
                    <div className="relative">
                        <Search
                            size={14}
                            className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400 dark:text-neutral-500 pointer-events-none"
                        />
                        <input
                            type="text"
                            value={search || ''}
                            onChange={(e) => set('search', e.target.value)}
                            placeholder="Search by problem, location, or ID..."
                            className="
                                w-full h-[36px] pl-9 pr-3 text-[12.5px]
                                bg-neutral-50 dark:bg-neutral-800/90
                                border border-neutral-200 dark:border-neutral-700 rounded-lg outline-none
                                text-neutral-800 dark:text-neutral-200
                                placeholder:text-neutral-400 dark:placeholder:text-neutral-500
                                focus:border-blue-500 focus:ring-1 focus:ring-blue-500/20 focus:bg-white dark:focus:bg-neutral-900
                                transition-all
                            "
                        />
                    </div>
                </div>

                {/* Domain */}
                <div className="flex flex-col gap-1.5 min-w-[150px]">
                    <span className="text-[11px] font-semibold uppercase tracking-wider text-neutral-400 dark:text-neutral-500">
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
                <div className="flex flex-col gap-1.5 min-w-[150px]">
                    <span className="text-[11px] font-semibold uppercase tracking-wider text-neutral-400 dark:text-neutral-500">
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
                <div className="flex flex-col gap-1.5 min-w-[140px]">
                    <span className="text-[11px] font-semibold uppercase tracking-wider text-neutral-400 dark:text-neutral-500">
                        Priority Level
                    </span>
                    <SelectWrapper>
                        <select
                            value={priority || ''}
                            onChange={(e) => set('priority', e.target.value)}
                            className={baseSelect}
                        >
                            <option value="">All Priorities</option>
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
                            h-[36px] px-3.5 text-[12px] font-semibold self-end flex-shrink-0
                            border border-neutral-200 dark:border-neutral-700 rounded-lg
                            text-neutral-600 dark:text-neutral-300
                            hover:bg-neutral-100 dark:hover:bg-neutral-800
                            transition-colors
                        "
                    >
                        Clear all
                    </button>
                )}
            </div>

            {/* ── Active filter chips ────────────────── */}
            {activeChips.length > 0 && (
                <div className="flex flex-wrap gap-2 pt-1 border-t border-neutral-100 dark:border-neutral-800">
                    <span className="text-[11px] font-medium text-neutral-400 dark:text-neutral-500 self-center">
                        Active Filters:
                    </span>
                    {activeChips.map(({ label, key }) => (
                        <span
                            key={key}
                            className="inline-flex items-center gap-1.5 text-[11px] font-semibold bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 pl-2.5 pr-1.5 py-1 rounded-md border border-blue-200/60 dark:border-blue-900/40 shadow-2xs"
                        >
                            {label}
                            <button
                                onClick={() => set(key, '')}
                                className="hover:text-blue-950 dark:hover:text-white transition-colors"
                            >
                                <X size={12} />
                            </button>
                        </span>
                    ))}
                </div>
            )}
        </div>
    )
}