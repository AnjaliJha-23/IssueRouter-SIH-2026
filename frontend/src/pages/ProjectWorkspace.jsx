import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { FolderGit2, CheckCircle2, Circle, ArrowLeft } from 'lucide-react'

export default function ProjectWorkspace() {
  const { id } = useParams()
  const { user } = useAuth()
  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProject()
  }, [id])

  const fetchProject = async () => {
    try {
      const res = await fetch(`/api/projects/${id}`).catch(() => fetch(`http://localhost:8000/api/projects/${id}`))
      if (res && res.ok) setProject(await res.json())
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="p-10 text-center">Loading Project...</div>
  if (!project) return <div className="p-10 text-center text-red-500">Project not found</div>

  let milestones = []
  try {
    if (project.milestones_json) {
        milestones = typeof project.milestones_json === 'string' ? JSON.parse(project.milestones_json) : project.milestones_json
    }
  } catch (e) {
    console.error("Error parsing milestones", e)
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Link to={user?.role === 'Gov' ? '/dashboard/gov' : user?.role === 'Citizen' ? '/dashboard/citizen' : '/dashboard/org'} className="p-2 hover:bg-neutral-200 dark:hover:bg-neutral-800 rounded-full transition-colors">
          <ArrowLeft className="w-5 h-5 text-neutral-600 dark:text-neutral-300" />
        </Link>
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent flex items-center gap-2">
            <FolderGit2 className="text-blue-600" /> Project Workspace
          </h2>
          <p className="text-sm text-neutral-500 mt-1">ID: {project.id}</p>
        </div>
      </div>

      <div className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 p-6 shadow-sm">
        <div className="mb-6 pb-6 border-b border-neutral-200 dark:border-neutral-700 flex justify-between items-start">
           <div>
             <h3 className="text-lg font-bold text-neutral-900 dark:text-white mb-1">Status: {project.status.toUpperCase()}</h3>
             <p className="text-sm text-neutral-500">Challenge ID: {project.challenge_id}</p>
           </div>
           <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
             Submit Deliverable
           </button>
        </div>

        <h4 className="text-sm font-bold text-neutral-900 dark:text-white mb-4">Project Milestones</h4>
        <div className="space-y-4">
          {milestones.length === 0 && <p className="text-sm text-neutral-500">No milestones defined yet.</p>}
          {milestones.map((m, idx) => (
            <div key={idx} className="flex items-center justify-between p-4 bg-neutral-50 dark:bg-neutral-800/50 border border-neutral-200 dark:border-neutral-700 rounded-lg">
              <div className="flex items-center gap-3">
                {m.status === 'completed' ? (
                  <CheckCircle2 className="w-5 h-5 text-green-500" />
                ) : (
                  <Circle className="w-5 h-5 text-neutral-400" />
                )}
                <span className={`text-sm font-medium ${m.status === 'completed' ? 'text-neutral-900 dark:text-white line-through opacity-70' : 'text-neutral-900 dark:text-white'}`}>
                  {m.title}
                </span>
              </div>
              <span className={`text-[10px] uppercase font-bold px-2 py-1 rounded ${
                m.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
              }`}>
                {m.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
