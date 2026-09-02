import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { Building, Target, CheckCircle, ArrowRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function OrgDashboard() {
  const { user } = useAuth()
  const [challenges, setChallenges] = useState([])
  const [activeProjects, setActiveProjects] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    fetchRoutedChallenges()
    fetchActiveProjects()
  }, [])

  const fetchRoutedChallenges = async () => {
    try {
      // Mock: Getting all verified challenges and generating matches
      const res = await fetch('http://localhost:8000/api/challenges/?verified=true')
      if (res.ok) {
        const verified = await res.json()
        const myMatches = []
        for (const c of verified) {
          const mRes = await fetch(`http://localhost:8000/api/matches/generate/${c.id}`, { method: 'POST' })
          if (mRes.ok) {
            const matches = await mRes.json()
            const myMatch = matches.find(m => m.org_id === user?.org_id && m.status === 'suggested')
            if (myMatch) {
              myMatches.push({ challenge: c, match: myMatch })
            }
          }
        }
        setChallenges(myMatches)
      }
    } catch (e) { console.error(e) }
  }

  const fetchActiveProjects = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/projects/')
      if (res.ok) {
        setActiveProjects(await res.json())
      }
    } catch (e) { console.error(e) }
  }

  const handleAccept = async (matchId) => {
    try {
      const res = await fetch(`http://localhost:8000/api/matches/${matchId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'accepted' })
      })
      if (res.ok) {
        fetchRoutedChallenges()
        fetchActiveProjects()
      }
    } catch (e) { console.error(e) }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between sm:items-end">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent flex items-center gap-2">
            <Building className="text-emerald-600" /> Organization Portal
          </h2>
          <p className="text-sm text-neutral-500 mt-1">
            {user?.organization?.name} • View Smart Matches and Collaboration Opportunities.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Inbox: Smart Matches */}
        <div className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-sm overflow-hidden flex flex-col h-[500px]">
          <div className="px-6 py-4 border-b border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-800/50 flex-shrink-0">
            <h3 className="text-sm font-bold text-neutral-900 dark:text-white flex items-center gap-2">
              <Target className="w-4 h-4 text-purple-500"/> Smart Router Matches
            </h3>
          </div>
          <div className="divide-y divide-neutral-200 dark:divide-neutral-700 overflow-y-auto flex-1">
            {challenges.length === 0 && (
              <div className="p-6 text-center text-sm text-neutral-500">No new matches right now.</div>
            )}
            {challenges.map(({ challenge: c, match: m }) => (
              <div key={c.id} className="p-6 hover:bg-neutral-50 dark:hover:bg-neutral-800/80 transition-colors">
                <div className="flex justify-between items-start">
                  <h4 className="text-sm font-bold text-neutral-900 dark:text-white">{c.title}</h4>
                  <span className="bg-indigo-100 text-indigo-800 text-[10px] font-bold px-2 py-0.5 rounded">
                    Match Score: {m.match_score}%
                  </span>
                </div>
                <p className="text-xs text-neutral-600 dark:text-neutral-400 mt-2 line-clamp-3">{c.description}</p>
                <div className="mt-3 p-2 bg-purple-50 dark:bg-purple-900/10 border border-purple-100 dark:border-purple-800/30 rounded text-[11px] text-purple-800 dark:text-purple-300">
                  <span className="font-bold">Why you were matched:</span> {m.match_reason}
                </div>
                <div className="mt-4 flex gap-2">
                  <button 
                    onClick={() => handleAccept(m.id)}
                    className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold py-2 px-4 rounded transition-colors"
                  >
                    Accept & Form Team
                  </button>
                  <button className="px-4 py-2 bg-neutral-200 dark:bg-neutral-700 hover:bg-neutral-300 dark:hover:bg-neutral-600 text-neutral-800 dark:text-neutral-200 text-xs font-bold rounded transition-colors">
                    Decline
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Active Projects */}
        <div className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-sm overflow-hidden flex flex-col h-[500px]">
          <div className="px-6 py-4 border-b border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-800/50 flex-shrink-0">
            <h3 className="text-sm font-bold text-neutral-900 dark:text-white flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-500"/> Active Projects
            </h3>
          </div>
          <div className="divide-y divide-neutral-200 dark:divide-neutral-700 overflow-y-auto flex-1">
            {activeProjects.length === 0 && (
              <div className="p-6 text-center text-sm text-neutral-500">No active projects.</div>
            )}
            {activeProjects.map(p => (
              <div key={p.id} className="p-6 hover:bg-neutral-50 dark:hover:bg-neutral-800/80 transition-colors flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-neutral-900 dark:text-white">Project ID: {p.id.split('-')[0]}</h4>
                  <div className="flex gap-2 mt-2">
                    <span className="bg-green-100 text-green-800 text-[10px] font-bold px-2 py-0.5 rounded">
                      Status: {p.status.toUpperCase()}
                    </span>
                  </div>
                </div>
                <button 
                  onClick={() => navigate(`/project/${p.id}`)}
                  className="p-2 bg-blue-50 dark:bg-blue-900/20 text-blue-600 hover:bg-blue-100 dark:hover:bg-blue-900/40 rounded-full transition-colors"
                >
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  )
}
