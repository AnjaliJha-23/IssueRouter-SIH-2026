import React, { useState, useEffect } from 'react'
import { User, LayoutDashboard, Palette, CheckCircle2, Loader2 } from 'lucide-react'

const DEFAULT_SETTINGS = {
  // Profile info
  name: 'Rajesh Kumar',
  email: 'rajesh.k@gov.in',
  designation: 'Chief Nodal Officer',
  department: 'MCD',
  
  // Dashboard display preferences
  hashtag: '#DelhiComplaints',
  city: 'New Delhi',
  refreshInterval: '5',
  
  // Appearance
  theme: 'system',
  language: 'en'
}

const DEPARTMENTS = ['PWD', 'MCD', 'DJB', 'BSES', 'NDMC', 'Traffic Police', 'Delhi Police', 'DDA', 'DMRC', 'DTC']
const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'Hindi (हिंदी)' },
]
const INTERVALS = [
  { value: '1', label: '1 minute' },
  { value: '5', label: '5 minutes' },
  { value: '15', label: '15 minutes' },
  { value: '30', label: '30 minutes' },
  { value: 'never', label: 'Manual refresh' },
]
const THEMES = [
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
  { value: 'system', label: 'System Default' },
]

export default function Settings() {
  const [settings, setSettings] = useState(() => {
    const saved = localStorage.getItem('issueRouter_settings')
    return saved ? JSON.parse(saved) : DEFAULT_SETTINGS
  })
  const [saveStatus, setSaveStatus] = useState('saved') // 'saved', 'saving'

  // Auto-save effect
  useEffect(() => {
    if (saveStatus === 'saving') {
      const timer = setTimeout(() => {
        localStorage.setItem('issueRouter_settings', JSON.stringify(settings))
        setSaveStatus('saved')
      }, 600)
      return () => clearTimeout(timer)
    }
  }, [settings, saveStatus])

  const handleChange = (e) => {
    const { name, value } = e.target
    setSettings(prev => ({ ...prev, [name]: value }))
    setSaveStatus('saving')
  }

  const InputField = ({ label, name, type = 'text', placeholder }) => (
    <div className="flex flex-col gap-1.5">
      <label className="text-[11px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
        {label}
      </label>
      <input
        type={type}
        name={name}
        value={settings[name]}
        onChange={handleChange}
        placeholder={placeholder}
        className="
          w-full px-3 py-2 text-[13px] rounded-xl outline-none transition-all
          bg-gray-50 dark:bg-gray-900/50 
          border border-gray-200 dark:border-gray-700
          text-gray-800 dark:text-gray-100
          focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500
          placeholder:text-gray-400 dark:placeholder:text-gray-600
        "
      />
    </div>
  )

  const SelectField = ({ label, name, options }) => (
    <div className="flex flex-col gap-1.5">
      <label className="text-[11px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
        {label}
      </label>
      <div className="relative">
        <select
          name={name}
          value={settings[name]}
          onChange={handleChange}
          className="
            w-full px-3 py-2 pr-8 text-[13px] rounded-xl outline-none transition-all appearance-none
            bg-gray-50 dark:bg-gray-900/50 
            border border-gray-200 dark:border-gray-700
            text-gray-800 dark:text-gray-100
            focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 cursor-pointer
          "
        >
          {options.map(opt => (
            <option key={opt.value || opt} value={opt.value || opt}>
              {opt.label || opt}
            </option>
          ))}
        </select>
        <svg viewBox="0 0 12 12" fill="none" className="w-3 h-3 absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none">
            <path d="M2 4L6 8L10 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>
    </div>
  )

  const Section = ({ title, icon: Icon, children }) => (
    <div className="glass-panel p-6 animate-fade-in-up">
      <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-100 dark:border-gray-700/50">
        <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-900/30 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
          <Icon size={18} />
        </div>
        <h3 className="text-lg font-bold text-gray-800 dark:text-gray-100">{title}</h3>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {children}
      </div>
    </div>
  )

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12">
      
      {/* ── Header ───────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-2">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400 bg-clip-text text-transparent">
            Settings
          </h2>
          <p className="text-[13px] font-medium text-gray-500 dark:text-gray-400 mt-1">
            Manage your personal profile and dashboard preferences.
          </p>
        </div>
        
        {/* Auto-save indicator */}
        <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 shadow-sm self-start sm:self-auto">
          {saveStatus === 'saving' ? (
            <>
              <Loader2 size={14} className="text-indigo-500 animate-spin" />
              <span className="text-[12px] font-medium text-gray-600 dark:text-gray-300">Saving changes...</span>
            </>
          ) : (
            <>
              <CheckCircle2 size={14} className="text-emerald-500" />
              <span className="text-[12px] font-medium text-gray-600 dark:text-gray-300">All changes saved</span>
            </>
          )}
        </div>
      </div>

      <div className="space-y-6">
        {/* Profile Info Section */}
        <Section title="Profile Information" icon={User}>
          <InputField label="Full Name" name="name" placeholder="John Doe" />
          <InputField label="Email Address" name="email" type="email" placeholder="john@example.com" />
          <InputField label="Designation" name="designation" placeholder="e.g. Nodal Officer" />
          <SelectField label="Department" name="department" options={DEPARTMENTS} />
        </Section>

        {/* Dashboard Preferences Section */}
        <Section title="Dashboard Display Preferences" icon={LayoutDashboard}>
          <InputField label="Tracked Hashtag" name="hashtag" placeholder="#YourCityComplaints" />
          <InputField label="City / Region" name="city" placeholder="e.g. Delhi" />
          <SelectField label="Auto-Refresh Interval" name="refreshInterval" options={INTERVALS} />
        </Section>

        {/* Appearance Section */}
        <Section title="Appearance" icon={Palette}>
          <SelectField label="Theme Preference" name="theme" options={THEMES} />
          <SelectField label="Language" name="language" options={LANGUAGES} />
        </Section>
      </div>

    </div>
  )
}