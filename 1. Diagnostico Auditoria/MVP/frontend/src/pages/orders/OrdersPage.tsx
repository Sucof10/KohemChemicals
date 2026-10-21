import { useState } from 'react'
import { useLocation } from 'react-router-dom'
import { listOrders } from '../../api/services/orders.service'
import { useAuth } from '../../auth/useAuth'
import { Alert } from '../../components/feedback/Alert'
import { EmptyState } from '../../components/feedback/EmptyState'
import { ErrorState } from '../../components/feedback/ErrorState'
import { LoadingScreen } from '../../components/feedback/LoadingScreen'
import { Card } from '../../components/ui/Card'
import { Icon } from '../../components/ui/Icon'
import { inputClass, selectClass } from '../../components/ui/formStyles'
import { LinkButton } from '../../components/ui/LinkButton'
import { PageHeader } from '../../components/ui/PageHeader'
import { StatusBadge } from '../../components/ui/StatusBadge'
import { useApiData } from '../../hooks/useApiData'
import { ORDER_STATUSES, type OrderStatus } from '../../types/api'
import { formatCurrency, formatDateTime } from '../../utils/format'
import { ORDER_STATUS_LABELS } from '../../utils/labels'
import { can, isStaff } from '../../utils/permissions'

interface LocationState {
  message?: string
}

type StatusFilter = 'todos' | OrderStatus

export function OrdersPage() {
  const { session } = useAuth()
  const role = session?.role ?? null
  const location = useLocation()
  const state = location.state as LocationState | null
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('todos')
  const [search, setSearch] = useState('')

  const { data, isLoading, error, reload } = useApiData(
    () => listOrders({ limit: 100 }),
    [],
  )

  const orders = data ?? []
  const term = search.trim().toLowerCase()
  const filtered = orders.filter((order) => {
    const matchesStatus =
      statusFilter === 'todos' || order.status === statusFilter
    const matchesSearch =
      term.length === 0 ||
      String(order.id).includes(term) ||
      (isStaff(role) && String(order.customer_id).includes(term))
    return matchesStatus && matchesSearch
  })

  if (isLoading) {
    return <LoadingScreen message="Cargando pedidos…" />
  }

  if (error) {
    return <ErrorState message={error} onRetry={reload} />
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={isStaff(role) ? 'Pedidos' : 'Mis pedidos'}
        description={
          isStaff(role)
            ? 'Pedidos registrados por los clientes. Puedes actualizar su estado según las reglas del sistema.'
            : 'Historial de tus pedidos. El total mostrado es el calculado por el servidor.'
        }
        actions={
          can(role, 'orders:create') ? (
            <LinkButton to="/orders/new">
              <Icon name="plus" className="h-4 w-4" />
              Nuevo pedido
            </LinkButton>
          ) : undefined
        }
      />

      {state?.message ? <Alert tone="success">{state.message}</Alert> : null}

      <Card>
        <div className="flex flex-wrap items-center gap-3 border-b border-slate-200 p-4">
          <div className="relative w-full max-w-xs">
            <Icon
              name="search"
              className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
            />
            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder={
                isStaff(role) ? 'Buscar por pedido o cliente' : 'Buscar pedido'
              }
              aria-label="Buscar pedidos"
              className={`${inputClass} pl-9`}
            />
          </div>
          <select
            value={statusFilter}
            onChange={(event) =>
              setStatusFilter(event.target.value as StatusFilter)
            }
            aria-label="Filtrar por estado"
            className={`${selectClass} max-w-xs`}
          >
            <option value="todos">Todos los estados</option>
            {ORDER_STATUSES.map((status) => (
              <option key={status} value={status}>
                {ORDER_STATUS_LABELS[status]}
              </option>
            ))}
          </select>
          <p className="ml-auto text-sm text-slate-500">
            {filtered.length} de {orders.length} pedidos
          </p>
        </div>

        {orders.length === 0 ? (
          <div className="p-5">
            <EmptyState
              title="Aún no hay pedidos"
              description={
                can(role, 'orders:create')
                  ? 'Selecciona materias primas disponibles y registra tu primer pedido.'
                  : 'Los pedidos de los clientes aparecerán en esta vista.'
              }
              action={
                can(role, 'orders:create') ? (
                  <LinkButton to="/orders/new">Crear pedido</LinkButton>
                ) : undefined
              }
            />
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-5">
            <EmptyState
              title="Sin resultados"
              description="Ajusta el estado o el término de búsqueda."
            />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-5 py-3 font-medium">Pedido</th>
                  {isStaff(role) ? (
                    <th className="px-5 py-3 font-medium">Cliente ID</th>
                  ) : null}
                  <th className="px-5 py-3 font-medium">Estado</th>
                  <th className="px-5 py-3 font-medium">Ítems</th>
                  <th className="px-5 py-3 font-medium">Total</th>
                  <th className="px-5 py-3 font-medium">Creado</th>
                  <th className="px-5 py-3 text-right font-medium">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {filtered.map((order) => (
                  <tr key={order.id}>
                    <td className="px-5 py-4 font-medium text-slate-900">
                      #{order.id}
                    </td>
                    {isStaff(role) ? (
                      <td className="px-5 py-4 text-slate-600">
                        {order.customer_id}
                      </td>
                    ) : null}
                    <td className="px-5 py-4">
                      <StatusBadge status={order.status} />
                    </td>
                    <td className="px-5 py-4 text-slate-600">
                      {order.items.length}
                    </td>
                    <td className="px-5 py-4 font-medium text-slate-900">
                      {formatCurrency(order.total)}
                    </td>
                    <td className="px-5 py-4 text-slate-500">
                      {formatDateTime(order.created_at)}
                    </td>
                    <td className="px-5 py-4 text-right">
                      <LinkButton
                        to={`/orders/${order.id}`}
                        variant="secondary"
                        className="h-9"
                      >
                        Ver detalle
                      </LinkButton>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      <p className="text-xs text-slate-500">
        La API devuelve hasta 100 pedidos por consulta. No existe un total
        paginado en el backend.
      </p>
    </div>
  )
}
