import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import { IssueProvider } from './context/IssueContext'
import { AuthProvider, useAuth } from './context/AuthContext'
import Layout from './components/layout/Layout'
import GovDashboard from './pages/GovDashboard'
import OrgDashboard from './pages/OrgDashboard'
import IndustryDashboard from './pages/IndustryDashboard'
import CitizenDashboard from './pages/CitizenDashboard'
import Analytics from './pages/Analytics'
import Maps from './pages/Maps'
import Settings from './pages/Settings'
import Progress from './pages/Progress'
import LandingPage from './pages/LandingPage'
import Login from './pages/Login'
import Profile from './pages/Profile'
import Notifications from './pages/Notifications'
import Unauthorized from './pages/Unauthorized'
import ProtectedRoute from './components/ProtectedRoute'
import ProjectWorkspace from './pages/ProjectWorkspace'
import Universities from './pages/Universities'
import ErrorBoundary from './components/ErrorBoundary'

// Smart role-based dashboard router
function RoleDashboardRedirect() {
  const { user } = useAuth()
  if (user?.role === 'Citizen') return <Navigate to="/dashboard/citizen" replace />
  if (user?.role === 'University') return <Navigate to="/dashboard/org" replace />
  if (user?.role === 'Industry') return <Navigate to="/dashboard/industry" replace />
  return <Navigate to="/dashboard/gov" replace />
}

export default function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <IssueProvider>
          <AuthProvider>
            <BrowserRouter>
              <Routes>
                {/* ── Public Routes ── */}
                <Route path="/" element={<LandingPage />} />
                <Route path="/login" element={<Login />} />
                <Route path="/unauthorized" element={<Unauthorized />} />

                {/* ── Protected Shell inside Layout ── */}
                <Route element={<ProtectedRoute />}>
                  <Route element={<Layout />}>
                    {/* Default Dashboard Redirection */}
                    <Route path="dashboard" element={<RoleDashboardRedirect />} />

                    {/* ── 1. Citizen Routes ── */}
                    <Route element={<ProtectedRoute allowedRoles={['Citizen', 'Gov']} />}>
                      <Route path="dashboard/citizen" element={<CitizenDashboard />} />
                    </Route>

                    {/* ── 2. Government Only Routes ── */}
                    <Route element={<ProtectedRoute allowedRoles={['Gov']} />}>
                      <Route path="dashboard/gov" element={<GovDashboard />} />
                      <Route path="analytics" element={<Analytics />} />
                      <Route path="maps" element={<Maps />} />
                      <Route path="universities" element={<Universities />} />
                    </Route>

                    {/* ── 3. University Routes ── */}
                    <Route element={<ProtectedRoute allowedRoles={['University', 'Gov']} />}>
                      <Route path="dashboard/org" element={<OrgDashboard />} />
                      <Route path="project/:id" element={<ProjectWorkspace />} />
                    </Route>

                    {/* ── 4. Industry Routes ── */}
                    <Route element={<ProtectedRoute allowedRoles={['Industry', 'Gov']} />}>
                      <Route path="dashboard/industry" element={<IndustryDashboard />} />
                    </Route>

                    {/* ── 5. Shared Authenticated Routes ── */}
                    <Route element={<ProtectedRoute allowedRoles={['Citizen', 'Gov', 'University', 'Industry']} />}>
                      <Route path="progress" element={<Progress />} />
                      <Route path="profile" element={<Profile />} />
                      <Route path="notifications" element={<Notifications />} />
                      <Route path="settings" element={<Settings />} />
                    </Route>
                  </Route>
                </Route>

                {/* Fallback */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </BrowserRouter>
          </AuthProvider>
        </IssueProvider>
      </ThemeProvider>
    </ErrorBoundary>
  )
}