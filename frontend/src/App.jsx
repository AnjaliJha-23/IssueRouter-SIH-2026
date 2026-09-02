import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import { IssueProvider } from './context/IssueContext'
import { AuthProvider } from './context/AuthContext'
import Layout from './components/layout/Layout'
import GovDashboard from './pages/GovDashboard'
import OrgDashboard from './pages/OrgDashboard'
import CitizenDashboard from './pages/CitizenDashboard'
import Analytics from './pages/Analytics'
import Maps from './pages/Maps'
import Settings from './pages/Settings'
import Progress from './pages/Progress'
import Login from './pages/Login'
import ProtectedRoute from './components/ProtectedRoute'
import ProjectWorkspace from './pages/ProjectWorkspace'

export default function App() {
  return (
    <ThemeProvider>
      <IssueProvider>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              {/* Public Routes */}
              <Route path="/login" element={<Login />} />
              
              {/* Protected Routes inside Layout */}
              <Route path="/" element={<ProtectedRoute />}>
                <Route element={<Layout />}>
                  {/* Default redirect (could be improved to redirect based on role) */}
                  <Route index element={<Navigate to="/dashboard/gov" replace />} />
                  
                  <Route path="dashboard/gov" element={<GovDashboard />} />
                  <Route path="dashboard/org" element={<OrgDashboard />} />
                  <Route path="dashboard/citizen" element={<CitizenDashboard />} />
                  
                  <Route path="project/:id" element={<ProjectWorkspace />} />

                  <Route path="analytics" element={<Analytics />} />
                  <Route path="maps" element={<Maps />} />
                  <Route path="progress" element={<Progress />} />
                  <Route path="settings" element={<Settings />} />
                </Route>
              </Route>
              
              <Route path="/unauthorized" element={<div className="p-10 text-center text-red-500 text-xl font-bold">Unauthorized Access</div>} />
              <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </IssueProvider>
    </ThemeProvider>
  )
}