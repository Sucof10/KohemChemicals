import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { LoadingScreen } from '../components/feedback/LoadingScreen'
import type { UserRole } from '../types/api'
import { useAuth } from './useAuth'

export function ProtectedRoute({
  allowedRoles,
}: {
  allowedRoles?: readonly UserRole[]
}) {
  const { session, isReady } = useAuth()
  const location = useLocation()

  if (!isReady) {
    return <LoadingScreen message="Verificando sesión…" />
  }

  if (!session) {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: `${location.pathname}${location.search}` }}
      />
    )
  }

  if (allowedRoles && !allowedRoles.includes(session.role)) {
    return <Navigate to="/forbidden" replace />
  }

  return <Outlet />
}

export function PublicOnlyRoute() {
  const { session, isReady } = useAuth()

  if (!isReady) {
    return <LoadingScreen message="Verificando sesión…" />
  }

  if (session) {
    return <Navigate to="/" replace />
  }

  return <Outlet />
}
