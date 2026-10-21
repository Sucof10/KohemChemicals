import { useAuth } from '../../auth/useAuth'
import { listAuditLogs } from '../../api/services/audit.service'
import { listMaterials } from '../../api/services/materials.service'
import { listOrders } from '../../api/services/orders.service'
import { EmptyState } from '../../components/feedback/EmptyState'
import { ErrorState } from '../../components/feedback/ErrorState'
import { LoadingScreen } from '../../components/feedback/LoadingScreen'
import { Badge } from '../../components/ui/Badge'
import { Card, CardHeader } from '../../components/ui/Card'
import { Icon, type IconName } from '../../components/ui/Icon'
import { LinkButton } from '../../components/ui/LinkButton'
import { PageHeader } from '../../components/ui/PageHeader'
import { StatusBadge } from '../../components/ui/StatusBadge'
import { useApiData } from '../../hooks/useApiData'
import type { AuditLog, Order, RawMaterial, UserRole } from '../../types/api'
import { formatCurrency, formatDateTime } from '../../utils/format'
import { FINAL_ORDER_STATUSES } from '../../types/api'
import { ROLE_LABELS } from '../../utils/labels'
import { can, isStaff } from '../../utils/permissions'

interface DashboardData {
  materials: RawMaterial[]
  orders: Order[]
  logs: AuditLog[]
}

const roleDescriptions: Record<UserRole, string> = {
  admin:
    'Controla inventario, pedidos, usuarios a través de la API y revisa la trazabilidad del sistema.',
  analista:
    'Gestiona el inventario y acompaña los pedidos registrados por los clientes.',
  cliente:
    'Consulta materias primas, registra pedidos y solicita asesoría cuando la necesites.',
}

function MetricCard({
  icon,
  label,
  value,
  detail,
}: {
  icon: IconName
  label: string
  value: string | number
  detail: string
}) {
  return (
    <Card className="p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-slate-500">{label}</p>
          <p className="mt-2 text-3xl font-semibold tracking-tight text-slate-900">
            {value}
          </p>
        </div>
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-50 text-teal-700">
          <Icon name={icon} className="h-5 w-5" />
        </span>
      </div>
      <p className="mt-3 text-xs text-slate-500">{detail}</p>
    </Card>
  )
}

export function DashboardPage() {
  const { session } = useAuth()
  const role = session?.role ?? 'cliente'

  const { data, isLoading, error, reload } = useApiData<DashboardData>(
    async () => {
      const [materials, orders, logs] = await Promise.all([
        listMaterials({ limit: 100 }),
        listOrders({ limit: 100 }),
        can(role, 'audit:view')
          ? listAuditLogs(100)
          : Promise.resolve<AuditLog[]>([]),
      ])
      return { materials, orders, logs }
    },
    [role],
  )

  if (isLoading) {
    return <LoadingScreen message="Cargando panel…" />
  }

  if (error || !data) {
    return (
      <ErrorState
        message={error ?? 'No se pudo cargar el panel.'}
        onRetry={reload}
      />
    )
  }

  const inProgress = data.orders.filter(
    (order) => !FINAL_ORDER_STATUSES.includes(order.status),
  ).length
  const delivered = data.orders.filter(
    (order) => order.status === 'entregado',
  ).length
  const activeMaterials = data.materials.filter(
    (material) => material.is_active,
  ).length
  const recentOrders = data.orders.slice(0, 5)

  return (
    <div className="space-y-6">
      <PageHeader
        title={`Hola, ${session?.username}`}
        description={roleDescriptions[role]}
        actions={
          <>
            <Badge className="bg-teal-50 text-teal-700 ring-teal-200">
              Rol: {ROLE_LABELS[role]}
            </Badge>
            {can(role, 'orders:create') ? (
              <LinkButton to="/orders/new">
                <Icon name="plus" className="h-4 w-4" />
                Nuevo pedido
              </LinkButton>
            ) : null}
            {can(role, 'materials:create') ? (
              <LinkButton to="/materials/new">
                <Icon name="plus" className="h-4 w-4" />
                Nuevo material
              </LinkButton>
            ) : null}
          </>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          icon="materials"
          label="Materiales"
          value={data.materials.length}
          detail={`${activeMaterials} activos en el catálogo`}
        />
        <MetricCard
          icon="orders"
          label="Pedidos"
          value={data.orders.length}
          detail={isStaff(role) ? 'Visibles para tu rol' : 'Registrados por ti'}
        />
        <MetricCard
          icon="dashboard"
          label="En curso"
          value={inProgress}
          detail="Pedidos no entregados ni cancelados"
        />
        <MetricCard
          icon="check"
          label="Entregados"
          value={delivered}
          detail="Pedidos con estado final entregado"
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader
            title="Pedidos recientes"
            description="Últimos pedidos devueltos por la API."
            action={
              <LinkButton to="/orders" variant="secondary" className="h-9">
                Ver todos
              </LinkButton>
            }
          />
          {recentOrders.length === 0 ? (
            <div className="p-5">
              <EmptyState
                title="Aún no hay pedidos"
                description={
                  can(role, 'orders:create')
                    ? 'Registra tu primer pedido desde el catálogo de materiales.'
                    : 'Los pedidos aparecerán aquí cuando los clientes los registren.'
                }
                action={
                  can(role, 'orders:create') ? (
                    <LinkButton to="/orders/new">Crear pedido</LinkButton>
                  ) : undefined
                }
              />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    <th className="px-5 py-3 font-medium">Pedido</th>
                    {isStaff(role) ? (
                      <th className="px-5 py-3 font-medium">Cliente</th>
                    ) : null}
                    <th className="px-5 py-3 font-medium">Estado</th>
                    <th className="px-5 py-3 font-medium">Total</th>
                    <th className="px-5 py-3 font-medium">Fecha</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 bg-white">
                  {recentOrders.map((order) => (
                    <tr key={order.id}>
                      <td className="px-5 py-3 font-medium text-slate-900">
                        #{order.id}
                      </td>
                      {isStaff(role) ? (
                        <td className="px-5 py-3 text-slate-600">
                          {order.customer_id}
                        </td>
                      ) : null}
                      <td className="px-5 py-3">
                        <StatusBadge status={order.status} />
                      </td>
                      <td className="px-5 py-3 text-slate-700">
                        {formatCurrency(order.total)}
                      </td>
                      <td className="px-5 py-3 text-slate-500">
                        {formatDateTime(order.created_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        <div className="space-y-6">
          <Card className="p-5">
            <h2 className="text-base font-semibold text-slate-900">
              Accesos rápidos
            </h2>
            <div className="mt-4 space-y-2">
              <LinkButton
                to="/materials"
                variant="secondary"
                className="w-full justify-start"
              >
                <Icon name="materials" className="h-4 w-4" />
                Consultar materiales
              </LinkButton>
              <LinkButton
                to="/orders"
                variant="secondary"
                className="w-full justify-start"
              >
                <Icon name="orders" className="h-4 w-4" />
                {isStaff(role) ? 'Revisar pedidos' : 'Mis pedidos'}
              </LinkButton>
              <LinkButton
                to="/ai"
                variant="secondary"
                className="w-full justify-start"
              >
                <Icon name="ai" className="h-4 w-4" />
                Asesoría IA
              </LinkButton>
              {can(role, 'audit:view') ? (
                <LinkButton
                  to="/audit-logs"
                  variant="secondary"
                  className="w-full justify-start"
                >
                  <Icon name="audit" className="h-4 w-4" />
                  Logs de auditoría
                </LinkButton>
              ) : null}
            </div>
          </Card>

          {isStaff(role) ? (
            <Card className="p-5">
              <div className="flex items-center gap-3">
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-slate-600">
                  <Icon name="audit" className="h-5 w-5" />
                </span>
                <div>
                  <p className="text-sm font-medium text-slate-500">
                    Eventos de auditoría
                  </p>
                  <p className="text-2xl font-semibold text-slate-900">
                    {data.logs.length}
                  </p>
                </div>
              </div>
              <p className="mt-3 text-xs text-slate-500">
                Registros recientes devueltos por la API. La vista es de solo
                lectura.
              </p>
            </Card>
          ) : null}

          <p className="px-1 text-xs leading-relaxed text-slate-500">
            Las métricas se calculan sobre los hasta 100 registros más recientes
            que expone la API. No reemplazan reportes del servidor.
          </p>
        </div>
      </div>
    </div>
  )
}
