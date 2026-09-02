import { useState, useRef, useEffect } from 'react'
import { useLocation, Link } from 'react-router-dom'
import { Search, User, Settings, LogOut, ChevronDown, Home } from 'lucide-react'

// Map each path to a readable label
const PAGE_LABELS = {
    '/dashboard': 'Dashboard',
    '/analytics': 'Analytics',
    '/maps': 'Maps',
    '/settings': 'Settings',
    '/profile': 'Profile',
    '/notifications': 'Notifications',
}

export default function Topbar({ onMenuClick }) {
    const { pathname } = useLocation()
    const [dropdownOpen, setDropdownOpen] = useState(false)
    const [searchValue, setSearchValue] = useState('')
    const dropdownRef = useRef(null)

    const pageLabel = PAGE_LABELS[pathname] ?? 'Page'

    // Close dropdown when clicking outside
    useEffect(() => {
        function handleClickOutside(e) {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
                setDropdownOpen(false)
            }
        }
        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    return (
        <header className="
      sticky top-0 z-10 h-14 px-5
      flex items-center gap-4
      bg-white dark:bg-gray-800
      border-b border-gray-200 dark:border-gray-700
    ">

            {/* ── Hamburger — mobile only ──────────────── */}
            <button
                onClick={onMenuClick}
                className="lg:hidden p-1.5 rounded-md text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex-shrink-0"
            >
                <svg viewBox="0 0 20 20" fill="none" className="w-5 h-5">
                    <path d="M3 5H17M3 10H17M3 15H17" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                </svg>
            </button>

            {/* ── Breadcrumb ───────────────────────────── */}
            <nav className="flex items-center gap-1.5 text-sm flex-shrink-0">
                <Link
                    to="/dashboard"
                    className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                >
                    <Home size={14} />
                </Link>
                <span className="text-gray-300 dark:text-gray-600">›</span>
                <span className="font-medium text-gray-700 dark:text-gray-200">
                    {pageLabel}
                </span>
            </nav>

            {/* ── Search bar ───────────────────────────── */}
            <div className="relative flex-1 max-w-xs ml-4">
                <Search
                    size={13}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500 pointer-events-none"
                />
                <input
                    type="text"
                    value={searchValue}
                    onChange={(e) => setSearchValue(e.target.value)}
                    placeholder="Search anything..."
                    className="
            w-full h-[34px] pl-8 pr-3 text-[13px]
            bg-gray-100 dark:bg-gray-700
            border border-transparent
            rounded-lg outline-none
            text-gray-700 dark:text-gray-200
            placeholder:text-gray-400 dark:placeholder:text-gray-500
            focus:bg-white dark:focus:bg-gray-900
            focus:border-indigo-400
            transition-colors
          "
                />
            </div>

            {/* ── Right side ───────────────────────────── */}
            <div className="ml-auto relative" ref={dropdownRef}>

                {/* Avatar button */}
                <button
                    onClick={() => setDropdownOpen((o) => !o)}
                    className="
            flex items-center gap-2 px-2.5 py-1.5 rounded-lg
            hover:bg-gray-100 dark:hover:bg-gray-700
            transition-colors
          "
                >
                    {/* Avatar circle */}
                    <div className="w-7 h-7 rounded-full bg-indigo-500 flex items-center justify-center text-[11px] font-medium text-white flex-shrink-0">
                        AK
                    </div>

                    {/* Name + role — hidden on small screens */}
                    <div className="hidden sm:block text-left leading-tight">
                        <p className="text-[12px] font-medium text-gray-800 dark:text-gray-100">
                            Arjun Kumar
                        </p>
                        <p className="text-[10px] text-gray-400 dark:text-gray-500">
                            Super Admin
                        </p>
                    </div>

                    <ChevronDown
                        size={14}
                        className={`text-gray-400 transition-transform duration-200 ${dropdownOpen ? 'rotate-180' : ''}`}
                    />
                </button>

                {/* ── Dropdown menu ────────────────────── */}
                {dropdownOpen && (
                    <div className="
            absolute right-0 top-[calc(100%+6px)] w-48
            bg-white dark:bg-gray-800
            border border-gray-200 dark:border-gray-700
            rounded-xl shadow-lg
            overflow-hidden z-50
          ">
                        {/* User info header */}
                        <div className="px-3.5 py-3 border-b border-gray-100 dark:border-gray-700">
                            <p className="text-[13px] font-medium text-gray-800 dark:text-gray-100">
                                Arjun Kumar
                            </p>
                            <p className="text-[11px] text-gray-400 dark:text-gray-500 mt-0.5">
                                arjun@adminkit.io
                            </p>
                        </div>

                        {/* Menu items */}
                        <div className="py-1">
                            <Link
                                to="/profile"
                                onClick={() => setDropdownOpen(false)}
                                className="flex items-center gap-2.5 px-3.5 py-2 text-[13px] text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                            >
                                <User size={14} />
                                Profile
                            </Link>
                            <Link
                                to="/settings"
                                onClick={() => setDropdownOpen(false)}
                                className="flex items-center gap-2.5 px-3.5 py-2 text-[13px] text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                            >
                                <Settings size={14} />
                                Settings
                            </Link>
                        </div>

                        <div className="border-t border-gray-100 dark:border-gray-700 py-1">
                            <button
                                onClick={() => {
                                    setDropdownOpen(false)
                                    // wire up your logout logic here
                                }}
                                className="w-full flex items-center gap-2.5 px-3.5 py-2 text-[13px] text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
                            >
                                <LogOut size={14} />
                                Logout
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </header>
    )
}