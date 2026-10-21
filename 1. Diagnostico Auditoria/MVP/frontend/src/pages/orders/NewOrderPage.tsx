import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getErrorMessage } from '../../api/errors'
import { listMaterials } from '../../api/services/materials.service'
import { createOrder } from '../../api/services/orders.service'
import { Alert } from '../../components/feedback/Alert'
import { EmptyState } from '../../components/feedback/EmptyState'
import { ErrorState } from '../../components/feedback/ErrorState'
import { LoadingScreen } from '../../components/feedback/LoadingScreen'
import { Button } from '../../components/ui/Button'
import { Card, CardHeader } from '../../components/ui/Card'
import { FormField } from '../../components/ui/FormField'
import {
  inputClass,
  selectClass,
  textareaClass,
} from '../../components/ui/formStyles'
import { Icon } from '../../components/ui/Icon'
import { LinkButton } from '../../components/ui/LinkButton'
import { PageHeader } from '../../components/ui/PageHeader'
import { useApiData } from '../../hooks/useApiData'
import { orderFormSchema } from '../../schemas/order.schema'
import type { RawMaterial } from '../../types/api'
import { formatCurrency, formatQuantity } from '../../utils/format'

interface CartItem {
  raw_material_id: number
  quantity: number
}

export function NewOrderPage() {
  const navigate = useNavigate()
  const [cart, setCart] = useState<CartItem[]>([])
  const [selectedMaterialId, setSelectedMaterialId] = useState('')
  const [quantity, setQuantity] = useState('1')
  const [notes, setNotes] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const { data, isLoading, error, reload } = useApiData(
    () => listMaterials({ limit: 100 }),
    [],
  )

  const materials = data ?? []
  const activeMaterials = materials.filter(
    (material) => material.is_active,
  )

  const materialsById = useMemo(() => {
    const map = new Map<number, RawMaterial>()
    for (const material of data ?? []) {
      map.set(material.id, material)
    }
    return map
  }, [data])

  const estimatedTotal = cart.reduce((total, item) => {
    const material = materialsById.get(item.raw_material_id)
    return total + (material ? material.price * item.quantity : 0)
  }, 0)

  const addToCart = () => {
    setFormError(null)
    const materialId = Number(selectedMaterialId)
    const requested = Number(quantity)

    if (!Number.isFinite(materialId) || materialId <= 0) {
      setFormError('Selecciona una materia prima.')
      return
    }
    const material = materialsById.get(materialId)
    if (!material || !material.is_active) {
      setFormError('La materia prima seleccionada no está disponible.')
      return
    }
    if (!Number.isFinite(requested) || requested <= 0) {
      setFormError('La cantidad debe ser mayor que cero.')
      return
    }
    if (cart.some((item) => item.raw_material_id === materialId)) {
      setFormError(
        'Esa materia prima ya está en el pedido. Ajusta su cantidad en la lista.',
      )
      return
    }
    if (requested > material.stock) {
      setFormError(
        `Stock insuficiente para "${material.name}". Disponible: ${formatQuantity(material.stock)} ${material.unit}.`,
      )
      return
    }

    setCart((current) => [
      ...current,
      { raw_material_id: materialId, quantity: requested },
    ])
    setSelectedMaterialId('')
    setQuantity('1')
  }

  const updateQuantity = (materialId: number, value: number) => {
    setCart((current) =>
      current.map((item) =>
        item.raw_material_id === materialId
          ? { ...item, quantity: value }
          : item,
      ),
    )
  }

  const removeFromCart = (materialId: number) => {
    setCart((current) =>
      current.filter((item) => item.raw_material_id !== materialId),
    )
  }

  const submitOrder = async () => {
    setFormError(null)

    const parsed = orderFormSchema.safeParse({
      items: cart,
      notes: notes.trim() || undefined,
    })
    if (!parsed.success) {
      setFormError(parsed.error.issues[0]?.message ?? 'Revisa el pedido.')
      return
    }

    for (const item of parsed.data.items) {
      const material = materialsById.get(item.raw_material_id)
      if (!material || !material.is_active) {
        setFormError('Una de las materias primas ya no está disponible.')
        return
      }
      if (item.quantity > material.stock) {
        setFormError(
          `Stock insuficiente para "${material.name}". Disponible: ${formatQuantity(material.stock)} ${material.unit}.`,
        )
        return
      }
    }

    setIsSubmitting(true)
    try {
      const order = await createOrder(parsed.data)
      navigate(`/orders/${order.id}`, {
        replace: true,
        state: {
          message: `Pedido #${order.id} registrado. Total calculado por el servidor: ${formatCurrency(order.total)}.`,
        },
      })
    } catch (requestError) {
      setFormError(getErrorMessage(requestError))
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) {
    return <LoadingScreen message="Cargando catálogo…" />
  }

  if (error) {
    return <ErrorState message={error} onRetry={reload} />
  }

  if (activeMaterials.length === 0) {
    return (
      <div className="space-y-6">
        <PageHeader title="Nuevo pedido" />
        <EmptyState
          title="No hay materiales disponibles"
          description="El catálogo no tiene materias primas activas en este momento."
          action={
            <LinkButton to="/materials" variant="secondary">
              Volver al catálogo
            </LinkButton>
          }
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Nuevo pedido"
        description="Selecciona materias primas y cantidades. El servidor valida el stock, descuenta las cantidades y calcula el total definitivo."
        actions={
          <LinkButton to="/orders" variant="secondary">
            <Icon name="arrow-left" className="h-4 w-4" />
            Volver
          </LinkButton>
        }
      />

      {formError ? <Alert tone="error">{formError}</Alert> : null}

      <div className="grid gap-6 xl:grid-cols-3">
        <div className="space-y-6 xl:col-span-2">
          <Card>
            <CardHeader
              title="Agregar materia prima"
              description="Solo se muestran materiales activos. La cantidad no puede superar el stock disponible."
            />
            <div className="grid gap-4 p-5 sm:grid-cols-[1fr_10rem_auto] sm:items-end">
              <FormField label="Materia prima" htmlFor="material">
                <select
                  id="material"
                  value={selectedMaterialId}
                  onChange={(event) =>
                    setSelectedMaterialId(event.target.value)
                  }
                  className={selectClass}
                >
                  <option value="">Selecciona un material</option>
                  {activeMaterials.map((material) => (
                    <option
                      key={material.id}
                      value={material.id}
                      disabled={material.stock <= 0}
                    >
                      {material.name} — {formatQuantity(material.stock)}{' '}
                      {material.unit} — {formatCurrency(material.price)}
                    </option>
                  ))}
                </select>
              </FormField>
              <FormField label="Cantidad" htmlFor="quantity">
                <input
                  id="quantity"
                  type="number"
                  inputMode="decimal"
                  min="0.0001"
                  step="0.0001"
                  value={quantity}
                  onChange={(event) => setQuantity(event.target.value)}
                  className={inputClass}
                />
              </FormField>
              <Button onClick={addToCart} className="sm:mb-0.5">
                <Icon name="plus" className="h-4 w-4" />
                Agregar
              </Button>
            </div>
          </Card>

          <Card>
            <CardHeader
              title="Detalle del pedido"
              description="Puedes ajustar las cantidades antes de registrar el pedido."
            />
            {cart.length === 0 ? (
              <div className="p-5">
                <EmptyState
                  title="Tu pedido está vacío"
                  description="Selecciona una materia prima y una cantidad para comenzar."
                />
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200 text-sm">
                  <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                    <tr>
                      <th className="px-5 py-3 font-medium">Material</th>
                      <th className="px-5 py-3 font-medium">Cantidad</th>
                      <th className="px-5 py-3 font-medium">Precio unitario</th>
                      <th className="px-5 py-3 text-right font-medium">
                        Acción
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 bg-white">
                    {cart.map((item) => {
                      const material = materialsById.get(item.raw_material_id)
                      if (!material) return null
                      return (
                        <tr key={item.raw_material_id}>
                          <td className="px-5 py-4">
                            <p className="font-medium text-slate-900">
                              {material.name}
                            </p>
                            <p className="text-xs text-slate-500">
                              Stock: {formatQuantity(material.stock)}{' '}
                              {material.unit}
                            </p>
                          </td>
                          <td className="px-5 py-4">
                            <div className="flex items-center gap-2">
                              <input
                                type="number"
                                inputMode="decimal"
                                min="0.0001"
                                step="0.0001"
                                value={item.quantity}
                                onChange={(event) =>
                                  updateQuantity(
                                    item.raw_material_id,
                                    Number(event.target.value),
                                  )
                                }
                                aria-label={`Cantidad de ${material.name}`}
                                className={`${inputClass} w-28`}
                              />
                              <span className="text-xs text-slate-500">
                                {material.unit}
                              </span>
                            </div>
                          </td>
                          <td className="px-5 py-4 text-slate-700">
                            {formatCurrency(material.price)}
                          </td>
                          <td className="px-5 py-4 text-right">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-rose-600 hover:bg-rose-50"
                              onClick={() =>
                                removeFromCart(item.raw_material_id)
                              }
                            >
                              <Icon name="trash" className="h-4 w-4" />
                              Quitar
                            </Button>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </div>

        <div>
          <Card className="p-5">
            <h2 className="text-base font-semibold text-slate-900">Resumen</h2>
            <div className="mt-4 space-y-2 text-sm">
              <div className="flex justify-between text-slate-600">
                <span>Líneas</span>
                <span>{cart.length}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Total estimado</span>
                <span className="font-medium text-slate-900">
                  {formatCurrency(estimatedTotal)}
                </span>
              </div>
            </div>
            <p className="mt-3 rounded-lg bg-amber-50 p-3 text-xs leading-relaxed text-amber-800">
              El total estimado es solo una referencia. El total definitivo es
              el que devuelve el servidor al registrar el pedido.
            </p>

            <div className="mt-5">
              <FormField
                label="Notas"
                htmlFor="notes"
                hint="Opcional. Máximo 500 caracteres."
              >
                <textarea
                  id="notes"
                  rows={4}
                  maxLength={500}
                  value={notes}
                  onChange={(event) => setNotes(event.target.value)}
                  className={textareaClass}
                />
              </FormField>
            </div>

            <Button
              className="mt-5 w-full"
              onClick={submitOrder}
              isLoading={isSubmitting}
              disabled={cart.length === 0}
            >
              Registrar pedido
            </Button>
            <p className="mt-3 text-xs leading-relaxed text-slate-500">
              Al registrar el pedido, el stock se descuenta de inmediato. Si se
              cancela, el stock se devuelve.
            </p>
          </Card>
        </div>
      </div>
    </div>
  )
}
