import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { authFetch } from '../api/client'
import { 
  Building, 
  CheckCircle2, 
  ArrowRight, 
  Clock, 
  Calendar, 
  Users, 
  AlertCircle, 
  FolderGit2, 
  FileText, 
  Sparkles,
  MapPin,
  Tag
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function OrgDashboard() {
  const { user } = useAuth()
  const [assignments, setAssignments] = useState([])
  const [activeProjects, setActiveProjects] = useState([])
  const [loadingAssignments, setLoadingAssignments] = useState(true)
  const [loadingProjects, setLoadingProjects] = useState(true)
  const [processingId, setProcessingId] = useState(null)
  const navigate = useNavigate()

  // Default to org-univ-1 for Dr. Sharma if user.org_id is null in dev
  const currentOrgId = user?.org_id || 'org-univ-1'

  useEffect(() => {
    fetchAssignments()
    fetchActiveProjects()
  }, [currentOrgId])

  const fetchAssignments = async () => {
    setLoadingAssignments(true)
    try {
      const res = await authFetch(`/api/challenges/assignments?org_id=${currentOrgId}`)
      if (res && res.ok) {
        const data = await res.json()
        setAssignments(Array.isArray(data) ? data : [])
      }
    } catch (e) {
      console.error('Error fetching university assignments:', e)
    } finally {
      setLoadingAssignments(false)
    }
  }

  const fetchActiveProjects = async () => {
    setLoadingProjects(true)
    try {
      const res = await authFetch(`/api/projects/?org_id=${currentOrgId}`)
      if (res && res.ok) {
        const data = await res.json()
        setActiveProjects(Array.isArray(data) ? data : [])
      }
    } catch (e) {
      console.error('Error fetching university projects:', e)
    } finally {
      setLoadingProjects(false)
    }
  }

  const handleAccept = async (assignmentId) => {
    setProcessingId(assignmentId)
    try {
      const res = await authFetch(`/api/challenges/invitations/${assignmentId}/accept`, {
        method: 'POST'
      })

      if (res && res.ok) {
        await Promise.all([fetchAssignments(), fetchActiveProjects()])
      }
    } catch (e) {
      console.error('Error accepting assignment:', e)
    } finally {
      setProcessingId(null)
    }
  }

  const handleDecline = async (assignmentId) => {
    setProcessingId(assignmentId)
    try {
      const res = await authFetch(`/api/challenges/invitations/${assignmentId}/decline`, {
        method: 'POST'
      })

      if (res && res.ok) {
        await fetchAssignments()
      }
    } catch (e) {
      console.error('Error declining assignment:', e)
    } finally {
      setProcessingId(null)
    }
  }

  const pendingAssignments = assignments.filter(a => a.status === 'pending')

  return (
    <div className="space-y-6">
      {/* ── Page Header ───────────────────────── */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-end gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 dark:from-emerald-400 dark:to-teal-400 bg-clip-text text-transparent flex items-center gap-2">
              <Building className="text-emerald-600 dark:text-emerald-400" /> University Innovation Portal
            </h2>
            <span className="bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-300 text-[11px] font-bold px-2.5 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800">
              Academic Hub
            </span>
          </div>
          <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
            {user?.organization?.name || 'RIMS Ranchi'} • Review Government Challenge Assignments & Formulate Solution Proposals.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs font-semibold text-neutral-500 bg-neutral-100 dark:bg-neutral-800 px-3 py-1.5 rounded-lg">
          <span>Active Role:</span>
          <span className="text-emerald-600 dark:text-emerald-400 font-bold">{user?.name || 'University Lead'}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* ── Left Column: Assigned Civic Challenges ───────────────── */}
        <div className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-sm overflow-hidden flex flex-col min-h-[580px]">
          <div className="px-6 py-4 border-b border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-800/60 flex justify-between items-center flex-shrink-0">
            <h3 className="text-sm font-bold text-neutral-900 dark:text-white flex items-center gap-2">
              <Calendar className="w-4 h-4 text-blue-600 dark:text-blue-400"/> Assigned Civic Challenges
            </h3>
            <span className="text-xs bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300 font-bold px-2 py-0.5 rounded-full">
              {pendingAssignments.length} Pending Review
            </span>
          </div>

          <div className="divide-y divide-neutral-200 dark:divide-neutral-700 overflow-y-auto flex-1">
            {loadingAssignments ? (
              <div className="p-8 text-center text-sm text-neutral-500">Loading assignments...</div>
            ) : pendingAssignments.length === 0 ? (
              <div className="p-12 text-center flex flex-col items-center justify-center">
                <CheckCircle2 className="w-10 h-10 text-emerald-500 mb-2 opacity-80" />
                <p className="text-sm font-semibold text-neutral-800 dark:text-neutral-200">No pending assignments</p>
                <p className="text-xs text-neutral-500 mt-1 max-w-xs">
                  All assigned government challenges have been processed. New assignments from the State Government will appear here.
                </p>
              </div>
            ) : (
              pendingAssignments.map((assignment) => {
                const c = assignment.challenge
                const deadlineDate = new Date(assignment.deadline)
                const isUrgent = (deadlineDate - new Date()) / (1000 * 3600 * 24) <= 3
                const isBusy = processingId === assignment.assignment_id

                return (
                  <div key={assignment.assignment_id} className="p-5 hover:bg-neutral-50 dark:hover:bg-neutral-800/80 transition-colors space-y-3">
                    
                    {/* Top Badges */}
                    <div className="flex justify-between items-start gap-2">
                      <div className="flex flex-wrap items-center gap-1.5">
                        <span className="bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-[10.5px] font-extrabold px-2 py-0.5 rounded-full border border-red-200/50">
                          Priority {c?.priority_score || 85}
                        </span>
                        <span className="inline-flex items-center gap-1 bg-neutral-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300 text-[10.5px] font-semibold px-2 py-0.5 rounded">
                          <Tag className="w-3 h-3 text-neutral-500" />
                          {c?.domain || 'HealthTech'}
                        </span>
                      </div>

                      <div className={`flex items-center gap-1 text-[11px] font-semibold px-2.5 py-0.5 rounded-full border ${
                        isUrgent 
                          ? 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300' 
                          : 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300'
                      }`}>
                        <Clock className="w-3 h-3" />
                        Due {deadlineDate.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                      </div>
                    </div>

                    {/* Challenge Title */}
                    <h4 className="text-sm font-bold text-neutral-900 dark:text-white leading-snug">
                      {c?.title}
                    </h4>

                    {/* Description */}
                    <p className="text-xs text-neutral-600 dark:text-neutral-400 line-clamp-2 leading-relaxed">
                      {c?.description}
                    </p>

                    {/* Location & Department Info */}
                    <div className="flex items-center gap-3 text-[11px] text-neutral-500">
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3 h-3 text-neutral-400" />
                        {c?.location || 'Jharkhand'}
                      </span>
                      <span>•</span>
                      <span>{c?.department || 'Public Administration'}</span>
                    </div>

                    {/* Government Routing Directives Box */}
                    <div className="p-3 bg-blue-50/70 dark:bg-blue-950/20 border border-blue-100 dark:border-blue-900/40 rounded-lg space-y-1.5">
                      <div className="flex items-center justify-between text-[11px] font-bold text-blue-900 dark:text-blue-300">
                        <span className="flex items-center gap-1.5">
                          <AlertCircle className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
                          Government Routing Directive
                        </span>
                        <span className="flex items-center gap-1 font-semibold text-blue-700 dark:text-blue-400 text-[10.5px]">
                          <Users className="w-3 h-3" />
                          {assignment.total_assigned_universities} {assignment.total_assigned_universities === 1 ? 'University Selected' : 'Universities Selected'}
                        </span>
                      </div>
                      <p className="text-xs text-blue-950 dark:text-blue-200 font-medium">
                        {assignment.government_note || 'Assigned to your institution based on domain research capacity. Please prepare an actionable technological intervention.'}
                      </p>
                    </div>

                    {/* Actions */}
                    <div className="pt-1 flex gap-2">
                      <button 
                        onClick={() => handleAccept(assignment.assignment_id)}
                        disabled={isBusy}
                        className="flex-1 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white text-xs font-bold py-2.5 px-4 rounded-lg transition-colors flex items-center justify-center gap-1.5 shadow-sm cursor-pointer"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        {isBusy ? 'Processing...' : 'Accept Challenge & Start Project'}
                      </button>
                      <button 
                        onClick={() => handleDecline(assignment.assignment_id)}
                        disabled={isBusy}
                        className="px-4 py-2.5 bg-neutral-100 hover:bg-neutral-200 dark:bg-neutral-700 dark:hover:bg-neutral-600 text-neutral-700 dark:text-neutral-300 text-xs font-semibold rounded-lg transition-colors cursor-pointer"
                      >
                        Decline
                      </button>
                    </div>

                  </div>
                )
              })
            )}
          </div>
        </div>

        {/* ── Right Column: Active Projects ───────────────────────── */}
        <div className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-sm overflow-hidden flex flex-col min-h-[580px]">
          <div className="px-6 py-4 border-b border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-800/60 flex justify-between items-center flex-shrink-0">
            <h3 className="text-sm font-bold text-neutral-900 dark:text-white flex items-center gap-2">
              <FolderGit2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400"/> Active University Projects
            </h3>
            <span className="text-xs bg-emerald-100 dark:bg-emerald-900/40 text-emerald-800 dark:text-emerald-300 font-bold px-2 py-0.5 rounded-full">
              {activeProjects.length} Projects
            </span>
          </div>

          <div className="divide-y divide-neutral-200 dark:divide-neutral-700 overflow-y-auto flex-1">
            {loadingProjects ? (
              <div className="p-8 text-center text-sm text-neutral-500">Loading active projects...</div>
            ) : activeProjects.length === 0 ? (
              <div className="p-12 text-center flex flex-col items-center justify-center">
                <FolderGit2 className="w-10 h-10 text-neutral-400 mb-2 opacity-60" />
                <p className="text-sm font-semibold text-neutral-800 dark:text-neutral-200">No active projects yet</p>
                <p className="text-xs text-neutral-500 mt-1 max-w-xs">
                  When you accept an assigned challenge from the Government, a project is initialized here with its Solution Workspace.
                </p>
              </div>
            ) : (
              activeProjects.map((p) => {
                const challengeTitle = p.challenge?.title || `Civic Challenge: ${p.challenge_id}`
                const hasProposal = Boolean(p.proposal && p.proposal.status === 'submitted')
                const isDraft = Boolean(p.proposal && p.proposal.status === 'draft')

                return (
                  <div key={p.id} className="p-5 hover:bg-neutral-50 dark:hover:bg-neutral-800/80 transition-colors space-y-3">
                    <div className="flex justify-between items-start gap-2">
                      <span className="font-mono text-[10.5px] font-bold bg-neutral-100 dark:bg-neutral-700 text-neutral-600 dark:text-neutral-300 px-2 py-0.5 rounded">
                        {p.id.split('-')[0].toUpperCase()}
                      </span>

                      <div className="flex items-center gap-1.5">
                        {/* Proposal State Tag */}
                        {hasProposal ? (
                          <span className="bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 text-[10px] font-bold px-2.5 py-0.5 rounded-full flex items-center gap-1">
                            <Sparkles className="w-3 h-3 text-emerald-500" /> Proposal Live in Industry
                          </span>
                        ) : isDraft ? (
                          <span className="bg-amber-50 text-amber-700 border border-amber-200 text-[10px] font-bold px-2.5 py-0.5 rounded-full">
                            Draft Saved
                          </span>
                        ) : (
                          <span className="bg-blue-50 text-blue-700 border border-blue-200 text-[10px] font-bold px-2.5 py-0.5 rounded-full">
                            Proposal Needed
                          </span>
                        )}

                        <span className="bg-neutral-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300 text-[10px] font-bold px-2 py-0.5 rounded uppercase">
                          {p.status}
                        </span>
                      </div>
                    </div>

                    {/* Challenge & Project Info */}
                    <div>
                      <h4 className="text-sm font-bold text-neutral-900 dark:text-white leading-snug">
                        {challengeTitle}
                      </h4>
                      {p.challenge?.location && (
                        <p className="text-[11px] text-neutral-500 flex items-center gap-1 mt-1">
                          <MapPin className="w-3 h-3 text-neutral-400" />
                          {p.challenge.location} • {p.challenge.domain || 'HealthTech'}
                        </p>
                      )}
                    </div>

                    {/* Proposal Solution Summary if submitted */}
                    {p.proposal && (
                      <div className="p-3 bg-neutral-50 dark:bg-neutral-900/60 border border-neutral-200 dark:border-neutral-700/60 rounded-lg">
                        <p className="text-xs font-bold text-neutral-800 dark:text-neutral-200">
                          {p.proposal.title}
                        </p>
                        <p className="text-[11px] text-neutral-500 mt-0.5 line-clamp-1">
                          {p.proposal.proposed_solution}
                        </p>
                      </div>
                    )}

                    {/* Open Workspace Action */}
                    <div className="pt-1 flex items-center justify-between">
                      <div className="text-[11px] text-neutral-500 flex items-center gap-1">
                        <Building className="w-3 h-3 text-neutral-400" />
                        {user?.organization?.name || 'Assigned University'}
                      </div>

                      <button 
                        onClick={() => navigate(`/project/${p.id}`)}
                        className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-50 hover:bg-blue-100 dark:bg-blue-900/20 dark:hover:bg-blue-900/40 text-blue-700 dark:text-blue-300 text-xs font-bold rounded-lg transition-colors cursor-pointer"
                      >
                        <FileText className="w-3.5 h-3.5" />
                        Open Workspace
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </div>

                  </div>
                )
              })
            )}
          </div>
        </div>

      </div>
    </div>
  )
}

