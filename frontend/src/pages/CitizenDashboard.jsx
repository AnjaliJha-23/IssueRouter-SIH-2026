import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { CheckCircle2, MapPin, Send } from 'lucide-react'

export default function CitizenDashboard() {
  const { user } = useAuth()
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [location, setLocation] = useState('')
  const [challenges, setChallenges] = useState([])
  const [submitting, setSubmitting] = useState(false)
  const [msg, setMsg] = useState('')

  useEffect(() => {
    fetchChallenges()
  }, [])

  const fetchChallenges = async () => {
    try {
      const res = await fetch('/api/challenges/').catch(() => fetch('http://localhost:8000/api/challenges/'))
      if (res && res.ok) {
        const data = await res.json()
        setChallenges(Array.isArray(data) ? data : [])
      }
    } catch (e) {
      console.error(e)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setMsg('')
    try {
      const res = await fetch('/api/challenges/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title,
          description,
          location,
          lat: 23.3441, // Defaulting for MVP
          lng: 85.3096
        })
      }).catch(() => fetch('http://localhost:8000/api/challenges/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title,
          description,
          location,
          lat: 23.3441,
          lng: 85.3096
        })
      }))
      if (res && res.ok) {
        setMsg('Challenge submitted successfully! The Smart Router is analyzing it.')
        setTitle('')
        setDescription('')
        setLocation('')
        fetchChallenges()
      } else {
        setMsg('Failed to submit challenge.')
      }
    } catch (err) {
      setMsg('Error submitting challenge.')
    }
    setSubmitting(false)
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex flex-col">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
          Citizen Dashboard
        </h2>
        <p className="text-sm text-neutral-500 mt-1">
          Welcome {user?.name}. Submit local problems and track their impact.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Submit Form */}
        <div className="bg-white dark:bg-neutral-800 p-6 rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-sm">
          <h3 className="text-lg font-semibold mb-4 text-neutral-900 dark:text-white flex items-center gap-2">
            <Send className="w-5 h-5 text-blue-500" /> Report a New Challenge
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-neutral-500 dark:text-neutral-400 mb-1">Title</label>
              <input
                required
                type="text"
                value={title}
                onChange={e => setTitle(e.target.value)}
                placeholder="e.g. Broken Water Pipe in Ward 12"
                className="w-full px-3 py-2 text-sm border rounded-lg bg-transparent border-neutral-300 dark:border-neutral-600 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-neutral-500 dark:text-neutral-400 mb-1">Description (Be descriptive for AI categorization)</label>
              <textarea
                required
                rows={4}
                value={description}
                onChange={e => setDescription(e.target.value)}
                placeholder="Describe the issue in detail..."
                className="w-full px-3 py-2 text-sm border rounded-lg bg-transparent border-neutral-300 dark:border-neutral-600 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-neutral-500 dark:text-neutral-400 mb-1">Location</label>
              <input
                required
                type="text"
                value={location}
                onChange={e => setLocation(e.target.value)}
                placeholder="e.g. Ranchi, Main Road"
                className="w-full px-3 py-2 text-sm border rounded-lg bg-transparent border-neutral-300 dark:border-neutral-600 dark:text-white"
              />
            </div>
            
            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm py-2 px-4 rounded-lg transition-colors"
            >
              {submitting ? 'Submitting...' : 'Submit Challenge'}
            </button>
            {msg && <p className="text-xs text-green-600 dark:text-green-400 mt-2">{msg}</p>}
          </form>
        </div>

        {/* Live Challenges list */}
        <div className="bg-white dark:bg-neutral-800 p-6 rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-sm overflow-y-auto max-h-[500px]">
          <h3 className="text-lg font-semibold mb-4 text-neutral-900 dark:text-white flex items-center gap-2">
            <MapPin className="w-5 h-5 text-purple-500" /> Recent Community Challenges
          </h3>
          <div className="space-y-4">
            {challenges.length === 0 && <p className="text-sm text-neutral-500">No challenges found.</p>}
            {challenges.map(c => (
              <div key={c.id} className="p-4 border border-neutral-100 dark:border-neutral-700 rounded-lg bg-neutral-50 dark:bg-neutral-800/50">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="text-sm font-semibold text-neutral-900 dark:text-white">{c.title}</h4>
                  <span className={`text-[10px] px-2 py-1 rounded-full font-medium ${
                    c.status === 'verified' ? 'bg-green-100 text-green-800' :
                    c.status === 'matched' ? 'bg-blue-100 text-blue-800' :
                    c.status === 'in_project' ? 'bg-purple-100 text-purple-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {c.status.toUpperCase()}
                  </span>
                </div>
                <p className="text-xs text-neutral-600 dark:text-neutral-400 line-clamp-2 mb-2">{c.description}</p>
                <div className="flex items-center gap-3 text-[10px] text-neutral-500 font-medium">
                  <span className="flex items-center gap-1"><MapPin className="w-3 h-3"/> {c.location}</span>
                  {c.domain && <span className="bg-neutral-200 dark:bg-neutral-700 px-1.5 py-0.5 rounded text-neutral-700 dark:text-neutral-300">{c.domain}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
