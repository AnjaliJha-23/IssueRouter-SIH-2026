import { createContext, useContext, useState, useEffect } from 'react'

const ThemeContext = createContext(null)

export function ThemeProvider({ children }) {
    // Read saved preference from localStorage on first load
    const [darkMode, setDarkMode] = useState(() => {
        return localStorage.getItem('theme') === 'dark'
    })

    // Persist preference + sync the `dark` class on <html> for Tailwind
    useEffect(() => {
        localStorage.setItem('theme', darkMode ? 'dark' : 'light')
        document.documentElement.classList.toggle('dark', darkMode)
    }, [darkMode])

    const toggleDarkMode = () => setDarkMode((prev) => !prev)

    return (
        <ThemeContext.Provider value={{ darkMode, toggleDarkMode }}>
            {children}
        </ThemeContext.Provider>
    )
}

// Custom hook — use this anywhere instead of prop drilling
export function useTheme() {
    const ctx = useContext(ThemeContext)
    if (!ctx) throw new Error('useTheme must be used inside <ThemeProvider>')
    return ctx
}