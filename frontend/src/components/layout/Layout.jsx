import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Topbar from './Topbar'
import { useTheme } from '../../context/ThemeContext'

export default function Layout() {
    const [sidebarOpen, setSidebarOpen] = useState(false)
    const { darkMode, toggleDarkMode } = useTheme()

    return (
        <div className="flex h-screen overflow-hidden">

            <Sidebar
                darkMode={darkMode}
                toggleDarkMode={toggleDarkMode}
                isOpen={sidebarOpen}
                onClose={() => setSidebarOpen(false)}
            />

            <div className="flex flex-col flex-1 min-w-0 overflow-hidden">

                {/* Topbar — shown on all screen sizes.
            On mobile it also receives the open handler for the hamburger. */}
                <Topbar onMenuClick={() => setSidebarOpen(true)} />

                {/* Page content */}
                <main className="flex-1 overflow-y-auto p-6">
                    <Outlet />
                </main>
            </div>
        </div>
    )
}