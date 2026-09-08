import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { 
  FolderGit2, 
  CheckCircle2, 
  Circle, 
  ArrowLeft, 
  Sparkles, 
  Send, 
  Save, 
  Building2, 
  MapPin, 
  Tag, 
  Layers, 
  ShieldCheck, 
  AlertCircle, 
  DollarSign, 
  Clock, 
  Award, 
  Users, 
  FileText,
  Check,
  Edit3
} from 'lucide-react'

const TRL_OPTIONS = [
  { value: 'TRL-4 (Lab Prototype)', label: 'TRL-4 (Lab Prototype)' },
  { value: 'TRL-5 (Component Validated)', label: 'TRL-5 (Component Validated)' },
  { value: 'TRL-6 (Field Pilot Ready)', label: 'TRL-6 (Field Pilot Ready)' },
  { value: 'TRL-7 (Production Ready)', label: 'TRL-7 (Production Ready)' },
]

export default function ProjectWorkspace() {
  const { id } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  
  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [toast, setToast] = useState(null)

  // Proposal Form State
  const [formData, setFormData] = useState({
    solution_title: '',
    problem_understanding: '',
    proposed_solution: '',
    approach_methodology: '',
    trl: 'TRL-6 (Field Pilot Ready)',
    budget_required: '₹8,50,000',
    budget_num: 850000,
    impact_metrics: '',
    timeline: '4 Months',
    resources_needed: '',
    faculty_lead: '',
    contact_email: '',
    team_members: '',
    evidence_research: '',
  })

  useEffect(() => {
    fetchProject()
  }, [id])

  const showToast = (message, type = 'success') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 4000)
  }

  const fetchProject = async () => {
    setLoading(true)
    try {
      const res = await fetch(`/api/projects/${id}`).catch(() => fetch(`http://localhost:8000/api/projects/${id}`))
      if (res && res.ok) {
        const data = await res.json()
        setProject(data)

        // Pre-fill form if existing proposal exists
        if (data.proposal) {
          setFormData({
            solution_title: data.proposal.title || '',
            problem_understanding: data.proposal.problem_understanding || '',
            proposed_solution: data.proposal.proposed_solution || '',
            approach_methodology: data.proposal.approach_methodology || '',
            trl: data.proposal.trl || 'TRL-6 (Field Pilot Ready)',
            budget_required: data.proposal.budget_required || '₹8,50,000',
            budget_num: data.proposal.budget_num || 850000,
            impact_metrics: data.proposal.impact_metrics || '',
            timeline: data.proposal.timeline || '4 Months',
            resources_needed: data.proposal.resources_needed || '',
            faculty_lead: data.proposal.faculty_lead || '',
            contact_email: data.proposal.contact_email || '',
            team_members: data.proposal.team_members || '',
            evidence_research: data.proposal.evidence_research || '',
          })
          setIsEditing(false)
        } else {
          // Prepopulate sensible defaults based on challenge context
          const c = data.challenge
          const uniName = user?.organization?.name || 'University Research Team'
          setFormData(prev => ({
            ...prev,
            solution_title: c ? `${c.domain || 'Tech'} Intervention: ${c.title.split('-')[0].trim()}` : '',
            problem_understanding: c ? `Detailed root cause analysis for ${c.title} in ${c.location || 'Jharkhand'}. Existing infrastructure lacks automated monitoring.` : '',
            faculty_lead: user?.name ? `${user.name} (Research Lead)` : 'Dr. Lead Investigator',
            contact_email: user?.email || 'lead.research@university.ac.in',
            impact_metrics: `Directly mitigates public impact for residents across ${c?.location || 'the target zone'}.`,
            resources_needed: 'Access to field site, local civic authority coordination, IoT testing sensors.',
            timeline: '4 Months'
          }))
          setIsEditing(true)
        }
      }
    } catch (e) {
      console.error('Error fetching project:', e)
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmitProposal = async (isDraft = false) => {
    if (!formData.solution_title.trim() || !formData.proposed_solution.trim()) {
      showToast('Please provide at least a Solution Title and Solution Description.', 'error')
      return
    }

    setSubmitting(true)
    try {
      const payload = {
        ...formData,
        is_draft: isDraft
      }

      const res = await fetch(`/api/projects/${id}/proposal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      }).catch(() => fetch(`http://localhost:8000/api/projects/${id}/proposal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      }))

      if (res && res.ok) {
        showToast(
          isDraft ? 'Proposal saved as draft!' : 'Solution Proposal successfully submitted to Industry Portal!', 
          'success'
        )
        await fetchProject()
        setIsEditing(false)
      } else {
        showToast('Failed to submit proposal. Please check inputs.', 'error')
      }
    } catch (e) {
      console.error('Error submitting proposal:', e)
      showToast('Error communicating with backend.', 'error')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto py-16 text-center space-y-3">
        <div className="w-10 h-10 border-3 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm font-semibold text-neutral-600 dark:text-neutral-400">Loading Project Workspace...</p>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="max-w-4xl mx-auto py-16 text-center">
        <p className="text-base font-bold text-red-500">Project not found or unavailable.</p>
        <Link to="/dashboard/org" className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-blue-600 hover:underline">
          <ArrowLeft className="w-4 h-4" /> Return to Organization Portal
        </Link>
      </div>
    )
  }

  const c = project.challenge
  const p = project.proposal
  const isSubmitted = Boolean(p && p.status === 'submitted')

  let milestones = []
  try {
    if (project.milestones_json) {
      milestones = typeof project.milestones_json === 'string' ? JSON.parse(project.milestones_json) : project.milestones_json
    }
  } catch (e) {
    console.error('Error parsing milestones', e)
  }

  return (
    <div className="max-w-5xl mx-auto space-y-7 pb-16">
      
      {/* ── Toast Notification ───────────────── */}
      {toast && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-3 bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 px-5 py-3.5 rounded-xl shadow-2xl border border-neutral-700 animate-fade-in-up">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 dark:text-emerald-600 flex-shrink-0" />
          <p className="text-sm font-semibold">{toast.message}</p>
        </div>
      )}

      {/* ── Header Breadcrumbs & Status ───────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link 
            to={user?.role === 'Gov' ? '/dashboard/gov' : user?.role === 'Citizen' ? '/dashboard/citizen' : '/dashboard/org'} 
            className="p-2.5 hover:bg-neutral-200 dark:hover:bg-neutral-800 rounded-xl transition-colors text-neutral-600 dark:text-neutral-300"
            title="Back to Dashboard"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400 bg-clip-text text-transparent flex items-center gap-2">
                <FolderGit2 className="text-blue-600 dark:text-blue-400" /> Solution Workspace
              </h2>
              <span className="font-mono text-xs bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 px-2 py-0.5 rounded font-bold">
                {project.id.split('-')[0].toUpperCase()}
              </span>
            </div>
            <p className="text-xs text-neutral-500 mt-0.5">
              Assigned to: <span className="font-semibold text-neutral-700 dark:text-neutral-300">{user?.organization?.name || project.organization?.name || 'RIMS Ranchi'}</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          {isSubmitted ? (
            <span className="bg-emerald-100 dark:bg-emerald-900/40 text-emerald-800 dark:text-emerald-300 text-xs font-bold px-3 py-1.5 rounded-lg border border-emerald-300/40 flex items-center gap-1.5 shadow-sm">
              <Sparkles className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              Live in Industry Portal
            </span>
          ) : (
            <span className="bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300 text-xs font-bold px-3 py-1.5 rounded-lg border border-blue-300/40 flex items-center gap-1.5">
              <Clock className="w-4 h-4" />
              Proposal Formulation In-Progress
            </span>
          )}
        </div>
      </div>

      {/* ══════════════════════════════════════════════════
          SECTION 1 — READ-ONLY CHALLENGE DETAILS
          ══════════════════════════════════════════════════ */}
      <div className="bg-white dark:bg-neutral-800 rounded-2xl border border-neutral-200 dark:border-neutral-700 p-6 shadow-sm space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-neutral-100 dark:border-neutral-700/60">
          <div className="flex items-center gap-2">
            <span className="text-[11px] uppercase font-bold tracking-wider text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 px-2.5 py-0.5 rounded">
              Government Civic Challenge
            </span>
            <span className="text-xs text-neutral-400">•</span>
            <span className="font-mono text-xs text-neutral-500 font-semibold">{project.challenge_id}</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-xs font-extrabold px-2.5 py-0.5 rounded-full border border-red-200/50">
              Priority Score: {c?.priority_score || 85}
            </span>
            <span className="bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 text-xs font-bold px-2.5 py-0.5 rounded-full border border-emerald-200 flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              Verified by Gov
            </span>
          </div>
        </div>

        {/* Challenge Title & Badges */}
        <div>
          <h3 className="text-lg font-extrabold text-neutral-900 dark:text-white leading-snug">
            {c?.title || 'Civic Problem Description'}
          </h3>
          <div className="flex flex-wrap items-center gap-3 mt-2 text-xs text-neutral-600 dark:text-neutral-400">
            <span className="inline-flex items-center gap-1 font-medium bg-neutral-100 dark:bg-neutral-700/60 px-2 py-0.5 rounded">
              <Tag className="w-3 h-3 text-neutral-400" />
              {c?.domain || 'HealthTech'}
            </span>
            <span className="inline-flex items-center gap-1 font-medium bg-neutral-100 dark:bg-neutral-700/60 px-2 py-0.5 rounded">
              <Building2 className="w-3 h-3 text-neutral-400" />
              {c?.department || 'Public Administration'}
            </span>
            <span className="inline-flex items-center gap-1 font-medium bg-neutral-100 dark:bg-neutral-700/60 px-2 py-0.5 rounded">
              <MapPin className="w-3 h-3 text-neutral-400" />
              {c?.location || 'Jharkhand'}
            </span>
            <span className="text-neutral-400">
              • {c?.complaint_count || 120} citizen reports logged
            </span>
          </div>
        </div>

        {/* Problem Description */}
        <div className="bg-neutral-50 dark:bg-neutral-900/50 rounded-xl p-4 border border-neutral-100 dark:border-neutral-800 text-xs text-neutral-700 dark:text-neutral-300 leading-relaxed">
          <p className="font-semibold text-neutral-900 dark:text-white mb-1">Official Problem Statement:</p>
          {c?.description || 'High priority municipal challenge requiring research-backed technological intervention.'}
        </div>
      </div>

      {/* ══════════════════════════════════════════════════
          SECTION 2 — UNIVERSITY SOLUTION PROPOSAL
          ══════════════════════════════════════════════════ */}
      <div className="bg-white dark:bg-neutral-800 rounded-2xl border border-neutral-200 dark:border-neutral-700 shadow-sm overflow-hidden">
        
        {/* Section Header */}
        <div className="px-6 py-4 border-b border-neutral-200 dark:border-neutral-700 bg-neutral-50/70 dark:bg-neutral-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-bold text-neutral-900 dark:text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              University Solution Proposal & Industry Routing
            </h3>
            <p className="text-xs text-neutral-500 mt-0.5">
              Submit your academic team's proposed technology solution for CSR grant allocation and industry partnership.
            </p>
          </div>

          {isSubmitted && !isEditing && (
            <button
              onClick={() => setIsEditing(true)}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-neutral-100 hover:bg-neutral-200 dark:bg-neutral-700 dark:hover:bg-neutral-600 text-neutral-700 dark:text-neutral-200 text-xs font-bold rounded-lg transition-colors cursor-pointer self-start sm:self-auto"
            >
              <Edit3 className="w-3.5 h-3.5" />
              Edit Proposal
            </button>
          )}
        </div>

        {/* ── CASE A: PROPOSAL SUBMITTED (READ-ONLY VIEW) ── */}
        {isSubmitted && !isEditing ? (
          <div className="p-6 space-y-6">
            
            {/* Live Status Banner */}
            <div className="bg-gradient-to-r from-emerald-50 via-teal-50 to-white dark:from-emerald-950/30 dark:via-teal-950/20 dark:to-neutral-800 border border-emerald-200 dark:border-emerald-800/50 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center flex-shrink-0 shadow-sm shadow-emerald-600/30">
                  <Check className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-emerald-900 dark:text-emerald-200">
                    Proposal Active & Visible in Industry Dashboard
                  </h4>
                  <p className="text-xs text-emerald-700 dark:text-emerald-400 mt-0.5">
                    CSR committees and industry partners (e.g. Tata Steel CSR) can now evaluate, fund, and offer co-pilot partnerships.
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className="bg-emerald-100 dark:bg-emerald-900 text-emerald-800 dark:text-emerald-200 text-xs font-bold px-3 py-1 rounded-full">
                  {p.funding_status || 'Open for Funding'}
                </span>
                <span className="bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs font-bold px-3 py-1 rounded-full">
                  {p.collaboration_status || 'Seeking Partner'}
                </span>
              </div>
            </div>

            {/* Submitted Proposal Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-neutral-50 dark:bg-neutral-900/40 rounded-xl border border-neutral-100 dark:border-neutral-800">
                <span className="text-[10.5px] font-bold text-neutral-400 uppercase tracking-wider">Required Budget</span>
                <p className="text-lg font-extrabold text-neutral-900 dark:text-white mt-0.5">{p.budget_required}</p>
                <span className="text-[11px] text-neutral-500">CSR Grant Target</span>
              </div>
              <div className="p-4 bg-neutral-50 dark:bg-neutral-900/40 rounded-xl border border-neutral-100 dark:border-neutral-800">
                <span className="text-[10.5px] font-bold text-neutral-400 uppercase tracking-wider">Readiness Level</span>
                <p className="text-lg font-extrabold text-emerald-600 dark:text-emerald-400 mt-0.5">{p.trl}</p>
                <span className="text-[11px] text-neutral-500">Deployment Staging</span>
              </div>
              <div className="p-4 bg-neutral-50 dark:bg-neutral-900/40 rounded-xl border border-neutral-100 dark:border-neutral-800">
                <span className="text-[10.5px] font-bold text-neutral-400 uppercase tracking-wider">Timeline</span>
                <p className="text-lg font-extrabold text-blue-600 dark:text-blue-400 mt-0.5">{p.timeline || '4 Months'}</p>
                <span className="text-[11px] text-neutral-500">Pilot Completion</span>
              </div>
            </div>

            {/* Proposal Details Content */}
            <div className="space-y-4 text-xs">
              <div>
                <h5 className="font-bold text-sm text-neutral-900 dark:text-white">{p.title}</h5>
                <p className="text-neutral-600 dark:text-neutral-400 mt-1 leading-relaxed">{p.proposed_solution}</p>
              </div>

              {p.problem_understanding && (
                <div className="p-3.5 bg-neutral-50 dark:bg-neutral-900/40 rounded-xl">
                  <span className="font-bold text-neutral-700 dark:text-neutral-300 block mb-1">Problem Understanding:</span>
                  <p className="text-neutral-600 dark:text-neutral-400 leading-relaxed">{p.problem_understanding}</p>
                </div>
              )}

              {p.approach_methodology && (
                <div className="p-3.5 bg-neutral-50 dark:bg-neutral-900/40 rounded-xl">
                  <span className="font-bold text-neutral-700 dark:text-neutral-300 block mb-1">Proposed Approach & Technology:</span>
                  <p className="text-neutral-600 dark:text-neutral-400 leading-relaxed">{p.approach_methodology}</p>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-3.5 bg-neutral-50 dark:bg-neutral-900/40 rounded-xl">
                  <span className="font-bold text-neutral-700 dark:text-neutral-300 block mb-1">Faculty Lead & Contact:</span>
                  <p className="text-neutral-700 dark:text-neutral-300 font-semibold">{p.faculty_lead || 'Lead Researcher'}</p>
                  <p className="text-neutral-500 mt-0.5">{p.contact_email || 'Email provided to partners'}</p>
                </div>
                <div className="p-3.5 bg-neutral-50 dark:bg-neutral-900/40 rounded-xl">
                  <span className="font-bold text-neutral-700 dark:text-neutral-300 block mb-1">Expected Impact Metrics:</span>
                  <p className="text-neutral-600 dark:text-neutral-400 leading-relaxed">{p.impact_metrics || 'Quantified civic benefit.'}</p>
                </div>
              </div>
            </div>

            <div className="pt-2 flex justify-between items-center border-t border-neutral-100 dark:border-neutral-700/60 text-xs text-neutral-500">
              <span>Submitted: {new Date(p.created_at).toLocaleDateString()}</span>
              <Link to="/dashboard/industry" className="font-bold text-emerald-600 hover:text-emerald-700 flex items-center gap-1">
                View in Industry Portal →
              </Link>
            </div>
          </div>
        ) : (
          /* ── CASE B: FORM INPUT (NOT SUBMITTED OR EDITING) ── */
          <form onSubmit={(e) => { e.preventDefault(); handleSubmitProposal(false); }} className="p-6 space-y-6">
            
            {/* Subsection 1: Solution Overview */}
            <div className="space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-neutral-400 dark:text-neutral-500 flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5" /> 1. Solution Overview
              </h4>

              <div>
                <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1.5">
                  Solution Title <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.solution_title}
                  onChange={(e) => handleInputChange('solution_title', e.target.value)}
                  placeholder="e.g. IoT Solar Telemedicine Kiosk with Edge Diagnostic Sync"
                  className="w-full h-10 px-3.5 text-xs bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-lg outline-none focus:border-blue-500 text-neutral-800 dark:text-white transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1.5">
                  Problem Understanding & Root Cause
                </label>
                <textarea
                  rows={2}
                  value={formData.problem_understanding}
                  onChange={(e) => handleInputChange('problem_understanding', e.target.value)}
                  placeholder="Briefly explain your team's technical diagnosis of why this civic issue exists and previous interventions failed..."
                  className="w-full p-3 text-xs bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-lg outline-none focus:border-blue-500 text-neutral-800 dark:text-white resize-none transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1.5">
                  Proposed Solution Description <span className="text-red-500">*</span>
                </label>
                <textarea
                  rows={3}
                  required
                  value={formData.proposed_solution}
                  onChange={(e) => handleInputChange('proposed_solution', e.target.value)}
                  placeholder="Describe your technological, engineering, or scientific solution in clear, actionable detail..."
                  className="w-full p-3 text-xs bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-lg outline-none focus:border-blue-500 text-neutral-800 dark:text-white resize-none transition-colors"
                />
              </div>
            </div>

            {/* Subsection 2: Technical Approach & Readiness */}
            <div className="space-y-4 pt-4 border-t border-neutral-100 dark:border-neutral-700/60">
              <h4 className="text-xs font-bold uppercase tracking-wider text-neutral-400 dark:text-neutral-500 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5" /> 2. Technical Approach & Readiness
              </h4>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1.5">
                    Technology Readiness Level (TRL)
                  </label>
                  <select
                    value={formData.trl}
                    onChange={(e) => handleInputChange('trl', e.target.value)}
                    className="w-full h-10 px-3 text-xs bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-lg outline-none focus:border-blue-500 text-neutral-800 dark:text-white cursor-pointer"
                  >
                    {TRL_OPTIONS.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1.5">
                    Estimated Implementation Timeline
                  </label>
                  <input
                    type="text"
                    value={formData.timeline}
                    onChange={(e) => handleInputChange('timeline', e.target.value)}
                    placeholder="e.g. 4 Months (Pilot in 60 days)"
                    className="w-full h-10 px-3.5 text-xs bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-lg outline-none focus:border-blue-500 text-neutral-800 dark:text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1.5">
                  Methodology & Technology Stack
                </label>
                <textarea
                  rows={2}
                  value={formData.approach_methodology}
                  onChange={(e) => handleInputChange('approach_methodology', e.target.value)}
                  placeholder="Hardware/software stack, sensors, cloud components, standard operating procedures..."
                  className="w-full p-3 text-xs bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-lg outline-none focus:border-blue-500 text-neutral-800 dark:text-white resize-none"
                />
              </div>
            </div>

            {/* Subsection 3: Impact & Budget */}
            <div className="space-y-4 pt-4 border-t border-neutral-100 dark:border-neutral-700/60">
              <h4 className="text-xs font-bold uppercase tracking-wider text-neutral-400 dark:text-neutral-500 flex items-center gap-1.5">
                <DollarSign className="w-3.5 h-3.5" /> 3. Budget & Impact Metrics
              </h4>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1.5">
                    Estimated Budget Required (INR) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.budget_required}
                    onChange={(e) => handleInputChange('budget_required', e.target.value)}
                    placeholder="e.g. ₹8,50,000"
                    className="w-full h-10 px-3.5 text-xs bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-lg outline-none focus:border-blue-500 text-neutral-800 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1.5">
                    Quantified Impact Metrics
                  </label>
                  <input
                    type="text"
                    value={formData.impact_metrics}
                    onChange={(e) => handleInputChange('impact_metrics', e.target.value)}
                    placeholder="e.g. Covers 40,000 villagers across 12 hamlets with 24/7 tele-triage."
                    className="w-full h-10 px-3.5 text-xs bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-lg outline-none focus:border-blue-500 text-neutral-800 dark:text-white"
                  />
                </div>
              </div>
            </div>

            {/* Subsection 4: Team & Resources */}
            <div className="space-y-4 pt-4 border-t border-neutral-100 dark:border-neutral-700/60">
              <h4 className="text-xs font-bold uppercase tracking-wider text-neutral-400 dark:text-neutral-500 flex items-center gap-1.5">
                <Users className="w-3.5 h-3.5" /> 4. Faculty Lead & Team Capacity
              </h4>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1.5">
                    Faculty Lead & Designation
                  </label>
                  <input
                    type="text"
                    value={formData.faculty_lead}
                    onChange={(e) => handleInputChange('faculty_lead', e.target.value)}
                    placeholder="e.g. Dr. S. K. Sharma (Biomedical Engineering)"
                    className="w-full h-10 px-3.5 text-xs bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-lg outline-none focus:border-blue-500 text-neutral-800 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1.5">
                    Contact Email
                  </label>
                  <input
                    type="email"
                    value={formData.contact_email}
                    onChange={(e) => handleInputChange('contact_email', e.target.value)}
                    placeholder="e.g. sharma.biomed@rims.ac.in"
                    className="w-full h-10 px-3.5 text-xs bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-lg outline-none focus:border-blue-500 text-neutral-800 dark:text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-neutral-700 dark:text-neutral-300 mb-1.5">
                  Required Resources & Industry Pilot Needs
                </label>
                <input
                  type="text"
                  value={formData.resources_needed}
                  onChange={(e) => handleInputChange('resources_needed', e.target.value)}
                  placeholder="e.g. PHC facility access, solar battery grant, cellular testing SIMs"
                  className="w-full h-10 px-3.5 text-xs bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-lg outline-none focus:border-blue-500 text-neutral-800 dark:text-white"
                />
              </div>
            </div>

            {/* Actions Bar */}
            <div className="pt-4 border-t border-neutral-100 dark:border-neutral-700/60 flex flex-col sm:flex-row justify-between items-center gap-3">
              <p className="text-[11.5px] text-neutral-500">
                Submitting this proposal makes it immediately visible to verified Industry CSR partners.
              </p>

              <div className="flex items-center gap-3 w-full sm:w-auto">
                <button
                  type="button"
                  onClick={() => handleSubmitProposal(true)}
                  disabled={submitting}
                  className="flex-1 sm:flex-none px-4 py-2.5 bg-neutral-100 hover:bg-neutral-200 dark:bg-neutral-700 dark:hover:bg-neutral-600 text-neutral-800 dark:text-neutral-200 text-xs font-bold rounded-xl transition-colors flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-50"
                >
                  <Save className="w-3.5 h-3.5" />
                  Save Draft
                </button>

                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 sm:flex-none px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white text-xs font-bold rounded-xl transition-all shadow-lg shadow-emerald-600/20 flex items-center justify-center gap-2 cursor-pointer"
                >
                  <Send className="w-3.5 h-3.5" />
                  {submitting ? 'Submitting to Industry...' : 'Submit Proposal to Industry'}
                </button>
              </div>
            </div>

          </form>
        )}

      </div>

      {/* ══════════════════════════════════════════════════
          PROJECT MILESTONES (COLLAPSIBLE / SUMMARY)
          ══════════════════════════════════════════════════ */}
      <div className="bg-white dark:bg-neutral-800 rounded-2xl border border-neutral-200 dark:border-neutral-700 p-6 shadow-sm space-y-4">
        <h4 className="text-sm font-bold text-neutral-900 dark:text-white flex items-center gap-2">
          <Layers className="w-4 h-4 text-blue-600" />
          Project Delivery Pipeline
        </h4>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {milestones.map((m, idx) => {
            const isDone = m.status === 'completed'
            const isInProg = m.status === 'in_progress'

            return (
              <div 
                key={idx} 
                className={`p-3.5 rounded-xl border flex flex-col justify-between gap-2 ${
                  isDone 
                    ? 'bg-emerald-50/50 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800/40' 
                    : isInProg
                    ? 'bg-blue-50/50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800/40'
                    : 'bg-neutral-50 dark:bg-neutral-900/30 border-neutral-200 dark:border-neutral-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold text-neutral-400 uppercase">Phase {idx + 1}</span>
                  {isDone ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  ) : isInProg ? (
                    <Circle className="w-4 h-4 text-blue-500 fill-blue-500/20" />
                  ) : (
                    <Circle className="w-4 h-4 text-neutral-300 dark:text-neutral-600" />
                  )}
                </div>

                <p className="text-xs font-bold text-neutral-800 dark:text-neutral-200 leading-snug">
                  {m.title}
                </p>

                <span className={`text-[9.5px] uppercase font-extrabold px-2 py-0.5 rounded self-start ${
                  isDone 
                    ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-300' 
                    : isInProg
                    ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/60 dark:text-blue-300'
                    : 'bg-neutral-200 text-neutral-700 dark:bg-neutral-700 dark:text-neutral-400'
                }`}>
                  {m.status.replace('_', ' ')}
                </span>
              </div>
            )
          })}
        </div>
      </div>

    </div>
  )
}

