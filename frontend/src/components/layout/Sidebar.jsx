import { NavLink, useNavigate } from 'react-router-dom'
import IssueRouterLogo from '../../assets/issuerouter-logo.svg'
import { useAuth } from '../../context/AuthContext'
import {
    LayoutDashboard,
    BarChart2,
    Map,
    Settings,
    Bell,
    User,
    LogOut,
    Sun,
    Moon,
    X,
    ChevronRight,
    TrendingUp,
    GraduationCap,
    Shield,
} from 'lucide-react'

// Role-aware navigation definitions
const ROLE_NAVIGATION = {
    Citizen: {
        main: [
            { label: 'Dashboard', path: '/dashboard/citizen', icon: LayoutDashboard },
            { label: 'My Progress', path: '/progress', icon: TrendingUp },
        ],
        account: [
            { label: 'Profile', path: '/profile', icon: User },
            { label: 'Notifications', path: '/notifications', icon: Bell, dot: false },
            { label: 'Settings', path: '/settings', icon: Settings },
        ]
    },
    Gov: {
        main: [
            { label: 'Dashboard', path: '/dashboard/gov', icon: LayoutDashboard },
            { label: 'Analytics', path: '/analytics', icon: BarChart2, badge: 'New' },
            { label: 'Maps', path: '/maps', icon: Map },
            { label: 'Progress', path: '/progress', icon: TrendingUp },
            { label: 'Universities', path: '/universities', icon: GraduationCap },
        ],
        account: [
            { label: 'Profile', path: '/profile', icon: User },
            { label: 'Notifications', path: '/notifications', icon: Bell, dot: true },
            { label: 'Settings', path: '/settings', icon: Settings },
        ]
    },
    University: {
        main: [
            { label: 'University Portal', path: '/dashboard/org', icon: LayoutDashboard },
            { label: 'Progress Tracker', path: '/progress', icon: TrendingUp },
            { label: 'Directory', path: '/universities', icon: GraduationCap },
        ],
        account: [
            { label: 'Profile', path: '/profile', icon: User },
            { label: 'Notifications', path: '/notifications', icon: Bell, dot: false },
            { label: 'Settings', path: '/settings', icon: Settings },
        ]
    },
    Industry: {
        main: [
            { label: 'CSR Portal', path: '/dashboard/industry', icon: LayoutDashboard },
            { label: 'Project Progress', path: '/progress', icon: TrendingUp },
        ],
        account: [
            { label: 'Profile', path: '/profile', icon: User },
            { label: 'Notifications', path: '/notifications', icon: Bell, dot: false },
            { label: 'Settings', path: '/settings', icon: Settings },
        ]
    }
}

export default function Sidebar({ darkMode, toggleDarkMode, isOpen, onClose }) {
    const { user, logout } = useAuth()
    const navigate = useNavigate()

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    const currentNav = ROLE_NAVIGATION[user?.role] || ROLE_NAVIGATION.Citizen
    const mainNav = currentNav.main
    const accountNav = currentNav.account

    const initials = user?.name
        ? user.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
        : (user?.role ? user.role.slice(0, 2).toUpperCase() : 'U')

    return (
        <>
            {/* Mobile overlay — clicking it closes the sidebar */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/40 z-20 lg:hidden"
                    onClick={onClose}
                />
            )}

            {/* Sidebar panel */}
            <aside
                className={`
          fixed top-0 left-0 h-full z-30 w-60 flex flex-col
          bg-[#0a0f1c]/95 backdrop-blur-3xl border-r border-white/5 shadow-[4px_0_24px_rgba(0,0,0,0.4)] text-white
          transition-transform duration-300 ease-in-out
          lg:static lg:translate-x-0 lg:z-auto
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
            >
                {/* ── Logo ─────────────────────────────────── */}
                <div className="flex items-center justify-between px-4 py-5 border-b border-white/10">
                    <div className="flex flex-col items-center flex-1">
                        <img src={IssueRouterLogo} alt="IssueRouter Logo" className="h-12 w-auto object-contain rounded-lg" />
                        <span className="mt-1.5 text-[10px] font-medium tracking-[0.24em] text-white/45 text-center">
                            {user?.role === 'Citizen' ? 'Citizen Portal' : 'Innovation Portal'}
                        </span>
                    </div>

                    {/* Close button — visible on mobile only */}
                    <button
                        onClick={onClose}
                        className="lg:hidden p-1 rounded-md text-white/50 hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
                        aria-label="Close menu"
                    >
                        <X size={16} />
                    </button>
                </div>

                {/* ── Navigation ───────────────────────────── */}
                <nav className="flex-1 px-2.5 py-3 overflow-y-auto space-y-0.5">
                    <p className="px-2 pb-1 pt-2 text-[10px] uppercase tracking-widest text-white/40 font-semibold">
                        Main
                    </p>

                    {mainNav.map(({ label, path, icon: Icon, badge }) => (
                        <NavLink
                            key={path}
                            to={path}
                            onClick={onClose}
                            className={({ isActive }) =>
                                `flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-[13px] transition-colors
                ${isActive
                                    ? 'bg-white/20 text-white font-medium shadow-xs'
                                    : 'text-white/65 hover:bg-white/10 hover:text-white'
                                }`
                            }
                        >
                            <Icon size={16} className="flex-shrink-0" />
                            <span className="flex-1">{label}</span>
                            {badge && (
                                <span className="text-[10px] bg-indigo-200 text-indigo-800 font-medium px-1.5 py-0.5 rounded-full">
                                    {badge}
                                </span>
                            )}
                        </NavLink>
                    ))}

                    <p className="px-2 pb-1 pt-4 text-[10px] uppercase tracking-widest text-white/40 font-semibold">
                        Account
                    </p>

                    {accountNav.map(({ label, path, icon: Icon, dot }) => (
                        <NavLink
                            key={path}
                            to={path}
                            onClick={onClose}
                            className={({ isActive }) =>
                                `flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-[13px] transition-colors
                ${isActive
                                    ? 'bg-white/20 text-white font-medium shadow-xs'
                                    : 'text-white/65 hover:bg-white/10 hover:text-white'
                                }`
                            }
                        >
                            <Icon size={16} className="flex-shrink-0" />
                            <span className="flex-1">{label}</span>
                            {dot && <span className="w-1.5 h-1.5 rounded-full bg-rose-400 flex-shrink-0 animate-pulse" />}
                        </NavLink>
                    ))}
                </nav>

                {/* ── Bottom section ───────────────────────── */}
                <div className="px-2.5 py-3 border-t border-white/10 space-y-1">

                    {/* Dark / Light mode toggle */}
                    <button
                        onClick={toggleDarkMode}
                        className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-[13px] text-white/65 hover:bg-white/10 hover:text-white transition-colors cursor-pointer"
                    >
                        {darkMode ? <Sun size={16} /> : <Moon size={16} />}
                        <span className="flex-1 text-left">
                            {darkMode ? 'Light mode' : 'Dark mode'}
                        </span>
                        {/* Pill indicator */}
                        <div
                            className={`w-8 h-[18px] rounded-full relative transition-colors duration-200 ${darkMode ? 'bg-emerald-400' : 'bg-white/20'
                                }`}
                        >
                            <div
                                className={`w-3 h-3 bg-white rounded-full absolute top-[3px] transition-all duration-200 ${darkMode ? 'left-[17px]' : 'left-[3px]'
                                    }`}
                            />
                        </div>
                    </button>

                    {/* User profile row */}
                    <NavLink
                        to="/profile"
                        onClick={onClose}
                        className="flex items-center gap-2.5 px-2.5 py-2 rounded-lg hover:bg-white/10 cursor-pointer transition-colors"
                    >
                        <div className="w-7 h-7 rounded-full bg-indigo-500 border-2 border-white/25 flex items-center justify-center text-[11px] font-medium flex-shrink-0">
                            {initials}
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-[12px] font-medium text-white truncate">{user?.name || 'User'}</p>
                            <p className="text-[10px] text-white/45 flex items-center gap-1">
                                {user?.role === 'Citizen' && <Shield size={10} className="text-purple-400" />}
                                {user?.role || 'Guest'}
                            </p>
                        </div>
                        <ChevronRight size={13} className="text-white/30 flex-shrink-0" />
                    </NavLink>

                    {/* Logout */}
                    <button onClick={handleLogout} className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-[13px] text-red-300 hover:bg-red-500/15 transition-colors cursor-pointer">
                        <LogOut size={15} />
                        Logout
                    </button>
                </div>
            </aside>
        </>
    )
}
