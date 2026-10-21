import { lazy, Suspense } from 'react'
import { Route, Routes } from 'react-router-dom'
import { ProtectedRoute, PublicOnlyRoute } from './auth/guards'
import { LoadingScreen } from './components/feedback/LoadingScreen'
import { AppLayout } from './components/layout/AppLayout'

const LoginPage = lazy(() =>
  import('./pages/auth/LoginPage').then((module) => ({
    default: module.LoginPage,
  })),
)
const RegisterPage = lazy(() =>
  import('./pages/auth/RegisterPage').then((module) => ({
    default: module.RegisterPage,
  })),
)
const DashboardPage = lazy(() =>
  import('./pages/dashboard/DashboardPage').then((module) => ({
    default: module.DashboardPage,
  })),
)
const MaterialsPage = lazy(() =>
  import('./pages/materials/MaterialsPage').then((module) => ({
    default: module.MaterialsPage,
  })),
)
const MaterialFormPage = lazy(() =>
  import('./pages/materials/MaterialFormPage').then((module) => ({
    default: module.MaterialFormPage,
  })),
)
const OrdersPage = lazy(() =>
  import('./pages/orders/OrdersPage').then((module) => ({
    default: module.OrdersPage,
  })),
)
const NewOrderPage = lazy(() =>
  import('./pages/orders/NewOrderPage').then((module) => ({
    default: module.NewOrderPage,
  })),
)
const OrderDetailPage = lazy(() =>
  import('./pages/orders/OrderDetailPage').then((module) => ({
    default: module.OrderDetailPage,
  })),
)
const AIChatPage = lazy(() =>
  import('./pages/ai/AIChatPage').then((module) => ({
    default: module.AIChatPage,
  })),
)
const AuditLogsPage = lazy(() =>
  import('./pages/audit/AuditLogsPage').then((module) => ({
    default: module.AuditLogsPage,
  })),
)
const SessionPage = lazy(() =>
  import('./pages/session/SessionPage').then((module) => ({
    default: module.SessionPage,
  })),
)
const ForbiddenPage = lazy(() =>
  import('./pages/errors/ForbiddenPage').then((module) => ({
    default: module.ForbiddenPage,
  })),
)
const NotFoundPage = lazy(() =>
  import('./pages/errors/NotFoundPage').then((module) => ({
    default: module.NotFoundPage,
  })),
)

export default function App() {
  return (
    <Suspense fallback={<LoadingScreen message="Cargando módulo…" />}>
      <Routes>
        <Route element={<PublicOnlyRoute />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Route>

        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route index element={<DashboardPage />} />
            <Route path="materials" element={<MaterialsPage />} />
            <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
              <Route path="materials/new" element={<MaterialFormPage />} />
            </Route>
            <Route
              element={<ProtectedRoute allowedRoles={['admin', 'analista']} />}
            >
              <Route path="materials/:id/edit" element={<MaterialFormPage />} />
            </Route>
            <Route path="orders" element={<OrdersPage />} />
            <Route element={<ProtectedRoute allowedRoles={['cliente']} />}>
              <Route path="orders/new" element={<NewOrderPage />} />
            </Route>
            <Route path="orders/:id" element={<OrderDetailPage />} />
            <Route path="ai" element={<AIChatPage />} />
            <Route
              element={<ProtectedRoute allowedRoles={['admin', 'analista']} />}
            >
              <Route path="audit-logs" element={<AuditLogsPage />} />
            </Route>
            <Route path="session" element={<SessionPage />} />
            <Route path="forbidden" element={<ForbiddenPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Route>
      </Routes>
    </Suspense>
  )
}
