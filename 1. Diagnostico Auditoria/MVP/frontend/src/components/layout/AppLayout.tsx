import { Suspense, useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { LoadingScreen } from '../feedback/LoadingScreen'
import { useAuth } from '../../auth/useAuth'
import { APP_NAME } from '../../config/env'
import { can } from '../../utils/permissions'
import { ROLE_LABELS } from '../../utils/labels'
import { cn } from '../../utils/cn'
import { Icon, type IconName } from '../ui/Icon'
import { Button } from '../ui/Button'

interface NavItem {
  to: string
  label: string
  icon: IconName
  end?: boolean
}

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  const { session, logout } = useAuth()
  const navigate = useNavigate()
  const role = session?.role ?? null

  const items: NavItem[] = [
    { to: '/', label: 'Panel', icon: 'dashboard', end: true },
    { to: '/materials', label: 'Materiales', icon: 'materials' },
    { to: '/orders', label: 'Pedidos', icon: 'orders' },
    { to: '/ai', label: 'Asesoría IA', icon: 'ai' },
    ...(can(role, 'audit:view')
      ? [{ to: '/audit-logs', label: 'Auditoría', icon: 'audit' as const }]
      : []),
    { to: '/session', label: 'Mi sesión', icon: 'user' },
  ]

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-3 px-5 py-5">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-700 text-lg font-bold text-white">
          K
        </div>
        <div>
          <p className="text-sm font-semibold text-slate-900">{APP_NAME}</p>
          <p className="text-xs text-slate-500">Gestión de pedidos</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-2" aria-label="Navegación principal">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            onClick={onNavigate}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition',
                isActive
                  ? 'bg-teal-50 text-teal-800'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
              )
            }
          >
            <Icon name={item.icon} className="h-5 w-5" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-slate-200 p-3">
        <div className="flex items-center gap-3 rounded-lg px-2 py-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-200 text-sm font-semibold uppercase text-slate-700">
            {session?.username.slice(0, 1) ?? '?'}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-slate-900">
              {session?.username}
            </p>
            <p className="text-xs text-slate-500">
              {role ? ROLE_LABELS[role] : 'Sin sesión'}
            </p>
          </div>
        </div>
        <Button
          variant="ghost"
          className="mt-1 w-full justify-start"
          onClick={handleLogout}
        >
          <Icon name="logout" className="h-5 w-5" />
          Cerrar sesión
        </Button>
      </div>
    </div>
  )
}

export function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <div className="min-h-screen bg-slate-50 lg:flex">
      <aside className="hidden w-72 shrink-0 border-r border-slate-200 bg-white lg:block">
        <div className="sticky top-0 h-screen">
          <SidebarContent />
        </div>
      </aside>

      {mobileOpen ? (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            type="button"
            aria-label="Cerrar menú"
            className="absolute inset-0 bg-slate-900/40"
            onClick={() => setMobileOpen(false)}
          />
          <aside className="relative h-full w-72 max-w-[85vw] bg-white shadow-xl">
            <button
              type="button"
              aria-label="Cerrar menú"
              className="absolute right-3 top-3 rounded-lg p-2 text-slate-500 hover:bg-slate-100"
              onClick={() => setMobileOpen(false)}
            >
              <Icon name="close" className="h-5 w-5" />
            </button>
            <SidebarContent onNavigate={() => setMobileOpen(false)} />
          </aside>
        </div>
      ) : null}

      <div className="min-w-0 flex-1">
        <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-slate-200 bg-white/95 px-4 backdrop-blur lg:hidden">
          <button
            type="button"
            aria-label="Abrir menú"
            className="rounded-lg p-2 text-slate-600 hover:bg-slate-100"
            onClick={() => setMobileOpen(true)}
          >
            <Icon name="menu" className="h-5 w-5" />
          </button>
          <span className="text-sm font-semibold text-slate-900">{APP_NAME}</span>
        </header>

        <main className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
          <Suspense fallback={<LoadingScreen message="Cargando módulo…" />}>
            <Outlet />
          </Suspense>
        </main>
      </div>
    </div>
  )
}
