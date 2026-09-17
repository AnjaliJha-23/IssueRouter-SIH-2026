import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute({ allowedRoles }) {
  const { user, token } = useAuth()

  if (!token) {
    return <Navigate to="/login" replace />
  }

  // If allowedRoles is defined and user role is not permitted, block access
  if (allowedRoles && user?.role && !allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />
  }

  return <Outlet />
}
