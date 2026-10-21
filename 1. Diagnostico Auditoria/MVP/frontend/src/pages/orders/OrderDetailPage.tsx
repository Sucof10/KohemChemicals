import { useMemo, useState } from 'react'
import { useLocation, useParams } from 'react-router-dom'
import { getErrorMessage } from '../../api/errors'
import { listMaterials } from '../../api/services/materials.service'
import { getOrder, updateOrderStatus } from '../../api/services/orders.service'
import { useAuth } from '../../auth/useAuth'
import { Alert } from '../../components/feedback/Alert'
import { ErrorState } from '../../components/feedback/ErrorState'
import { LoadingScreen } from '../../components/feedback/LoadingScreen'
import { Button } from '../../components/ui/Button'
import { Card, CardHeader } from '../../components/ui/Card'
import { ConfirmDialog } from '../../components/ui/ConfirmDialog'
import { selectClass } from '../../components/ui/formStyles'
import { Icon } from '../../components/ui/Icon'
import { LinkButton } from '../../components/ui/LinkButton'
import { PageHeader } from '../../components/ui/PageHeader'
import { StatusBadge } from '../../components/ui/StatusBadge'
import { useApiData } from '../../hooks/useApiData'
import {
  FINAL_ORDER_STATUSES,
  ORDER_STATUSES,
  type Order,
  type OrderStatus,
  type RawMaterial,
} from '../../types/api'
import {
  formatCurrency,
  formatDateTime,
  formatQuantity,
} from '../../utils/format'
import { ORDER_STATUS_LABELS } from '../../utils/labels'
import { can, isStaff } from '../../utils/permissions'

interface OrderDetailData {
  order: Order
  materials: RawMaterial[]
}

interface LocationState {
  message?: string
}

export function OrderDetailPage() {
  const { id } = useParams<{ id: string }>()
  const orderId = Number(id)
  const { session } = useAuth()
  const role = session?.role ?? null
  const location = useLocation()
  const locationState = location.state as LocationState | null
  const [successMessage, setSuccessMessage] = useState<string | null>(
    locationState?.message ?? null,
  )
  const [actionError, setActionError] = useState<string | null>(null)
  const [statusChoice, setStatusChoice] = useState<OrderStatus | null>(null)
  const [pendingStatus, setPendingStatus] = useState<OrderStatus | null>(null)
  const [isUpdating, setIsUpdating] = useState(false)

  const { data, isLoading, error, reload } = useApiData<OrderDetailData>(
    async () => {
      if (!Number.isFinite(orderId)) {
        throw new Error('Identificador de pedido inválido.')
      }
      const [order, materials] = await Promise.all([
        getOrder(orderId),
        listMaterials({ limit: 100 }),
      ])
      return { order, materials }
    },
    [orderId],
  )

  const materialsById = useMemo(() => {
    const map = new Map<number, RawMaterial>()
    for (const material of data?.materials ?? []) {
      map.set(material.id, material)
    }
    return map
  }, [data])

  if (isLoading) {
    return <LoadingScreen message="Cargando pedido…" />
  }

  if (error || !data) {
    return (
      <ErrorState
        message={error ?? 'No se pudo cargar el pedido.'}
        onRetry={reload}
      />
    )
  }

  const { order } = data
  const isFinal = FINAL_ORDER_STATUSES.includes(order.status)
  const staff = isStaff(role)
  const selectedStatus = statusChoice ?? order.status

  const applyStatus = async (status: OrderStatus) => {
    if (status === order.status) return
    setActionError(null)
    setIsUpdating(true)
    try {
      await updateOrderStatus(order.id, status)
      setSuccessMessage(
        `El pedido #${order.id} cambió a estado "${ORDER_STATUS_LABELS[status]}".`,
      )
      setStatusChoice(null)
      await reload()
    } catch (requestError) {
      setActionError(getErrorMessage(requestError))
    } finally {
      setIsUpdating(false)
    }
  }

  const requestStatusChange = (status: OrderStatus) => {
    if (status === 'cancelado' && order.status !== 'cancelado') {
      setPendingStatus(status)
      return
    }
    void applyStatus(status)
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={`Pedido #${order.id}`}
        description={`Creado el ${formatDateTime(order.created_at)} · Actualizado el ${formatDateTime(order.updated_at)}`}
        actions={
          <LinkButton to="/orders" variant="secondary">
            <Icon name="arrow-left" className="h-4 w-4" />
            Volver a pedidos
          </LinkButton>
        }
      />

      {successMessage ? <Alert tone="success">{successMessage}</Alert> : null}
      {actionError ? <Alert tone="error">{actionError}</Alert> : null}

      <div className="grid gap-6 xl:grid-cols-3">
        <div className="space-y-6 xl:col-span-2">
          <Card>
            <CardHeader
              title="Materias primas del pedido"
              description="Precios y subtotales calculados por el servidor al registrar el pedido."
            />
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    <th className="px-5 py-3 font-medium">Material</th>
                    <th className="px-5 py-3 font-medium">Cantidad</th>
                    <th className="px-5 py-3 font-medium">Precio unitario</th>
                    <th className="px-5 py-3 text-right font-medium">Subtotal</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 bg-white">
                  {order.items.map((item) => {
                    const material = materialsById.get(item.raw_material_id)
                    return (
                      <tr key={item.id}>
                        <td className="px-5 py-4">
                          <p className="font-medium text-slate-900">
                            {material?.name ??
                              `Materia prima #${item.raw_material_id}`}
                          </p>
                          <p className="text-xs text-slate-500">
                            ID de material: {item.raw_material_id}
                          </p>
                        </td>
                        <td className="px-5 py-4 text-slate-700">
                          {formatQuantity(item.quantity)}
                          {material ? ` ${material.unit}` : ''}
                        </td>
                        <td className="px-5 py-4 text-slate-700">
                          {formatCurrency(item.unit_price)}
                        </td>
                        <td className="px-5 py-4 text-right font-medium text-slate-900">
                          {formatCurrency(item.subtotal)}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </Card>

          {order.notes ? (
            <Card className="p-5">
              <h2 className="text-base font-semibold text-slate-900">Notas</h2>
              <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-slate-600">
                {order.notes}
              </p>
            </Card>
          ) : null}
        </div>

        <div className="space-y-6">
          <Card className="p-5">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-semibold text-slate-900">Resumen</h2>
              <StatusBadge status={order.status} />
            </div>
            <dl className="mt-4 space-y-3 text-sm">
              <div className="flex justify-between gap-3">
                <dt className="text-slate-500">Total</dt>
                <dd className="text-lg font-semibold text-slate-900">
                  {formatCurrency(order.total)}
                </dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-slate-500">Líneas</dt>
                <dd className="text-slate-700">{order.items.length}</dd>
              </div>
              {staff ? (
                <div className="flex justify-between gap-3">
                  <dt className="text-slate-500">Cliente ID</dt>
                  <dd className="text-slate-700">{order.customer_id}</dd>
                </div>
              ) : null}
              <div className="flex justify-between gap-3">
                <dt className="text-slate-500">Última actualización</dt>
                <dd className="text-right text-slate-700">
                  {formatDateTime(order.updated_at)}
                </dd>
              </div>
            </dl>
            {staff ? (
              <p className="mt-4 text-xs leading-relaxed text-slate-500">
                La API no expone el nombre del cliente, solo su identificador.
              </p>
            ) : null}
          </Card>

          {!isFinal ? (
            <Card className="p-5">
              <h2 className="text-base font-semibold text-slate-900">
                Acciones
              </h2>
              {can(role, 'orders:update-status') ? (
                <div className="mt-4 space-y-3">
                  <label
                    htmlFor="order-status"
                    className="block text-sm font-medium text-slate-700"
                  >
                    Cambiar estado
                  </label>
                  <select
                    id="order-status"
                    value={selectedStatus}
                    onChange={(event) =>
                      setStatusChoice(event.target.value as OrderStatus)
                    }
                    className={selectClass}
                    disabled={isUpdating}
                  >
                    {ORDER_STATUSES.map((status) => (
                      <option key={status} value={status}>
                        {ORDER_STATUS_LABELS[status]}
                      </option>
                    ))}
                  </select>
                  <Button
                    className="w-full"
                    onClick={() => requestStatusChange(selectedStatus)}
                    disabled={
                      selectedStatus === order.status || isUpdating
                    }
                    isLoading={isUpdating}
                  >
                    Actualizar estado
                  </Button>
                  <p className="text-xs leading-relaxed text-slate-500">
                    El servidor permite cualquier cambio mientras el pedido no
                    esté entregado ni cancelado. Si pasa a cancelado, el stock
                    se devuelve.
                  </p>
                </div>
              ) : (
                <div className="mt-4">
                  <Button
                    variant="danger"
                    className="w-full"
                    onClick={() => requestStatusChange('cancelado')}
                    isLoading={isUpdating}
                  >
                    Cancelar pedido
                  </Button>
                  <p className="mt-3 text-xs leading-relaxed text-slate-500">
                    Al cancelar, el stock reservado se devuelve al inventario.
                  </p>
                </div>
              )}
            </Card>
          ) : (
            <Alert tone="info">
              Este pedido está en un estado final y no admite más cambios.
            </Alert>
          )}
        </div>
      </div>

      <ConfirmDialog
        open={pendingStatus !== null}
        title="Cancelar pedido"
        description="El pedido pasará a estado cancelado y el stock reservado se devolverá al inventario. Esta acción no se puede deshacer."
        confirmLabel="Sí, cancelar pedido"
        cancelLabel="Volver"
        isConfirming={isUpdating}
        onConfirm={() => {
          if (pendingStatus) {
            void applyStatus(pendingStatus)
          }
          setPendingStatus(null)
        }}
        onCancel={() => setPendingStatus(null)}
      />
    </div>
  )
}
