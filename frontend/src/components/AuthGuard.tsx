import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

interface Props {
  children: React.ReactElement
  requireAdmin?: boolean
}

export function AuthGuard({ children, requireAdmin = false }: Props) {
  const { user } = useAuth()
  const location = useLocation()

  if (!user) {
    // Save the attempted URL so we can redirect after login
    return <Navigate to="/login" state={{ from: location.pathname }} replace />
  }

  if (requireAdmin && user.role !== 'admin') {
    // Non-admin trying to access admin page - send to their dashboard
    return <Navigate to="/contributor" replace />
  }

  return children
}

