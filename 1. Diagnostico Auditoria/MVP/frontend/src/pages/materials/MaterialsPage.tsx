import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { getErrorMessage } from '../../api/errors'
import { deleteMaterial, listMaterials } from '../../api/services/materials.service'
import { useAuth } from '../../auth/useAuth'
import { Alert } from '../../components/feedback/Alert'
import { EmptyState } from '../../components/feedback/EmptyState'
import { ErrorState } from '../../components/feedback/ErrorState'
import { LoadingScreen } from '../../components/feedback/LoadingScreen'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Card } from '../../components/ui/Card'
import { ConfirmDialog } from '../../components/ui/ConfirmDialog'
import { Icon } from '../../components/ui/Icon'
import { inputClass } from '../../components/ui/formStyles'
import { LinkButton } from '../../components/ui/LinkButton'
import { PageHeader } from '../../components/ui/PageHeader'
import { useApiData } from '../../hooks/useApiData'
import type { RawMaterial } from '../../types/api'
import { formatCurrency, formatQuantity } from '../../utils/format'
import { can } from '../../utils/permissions'

interface LocationState {
  message?: string
}

export function MaterialsPage() {
  const { session } = useAuth()
  const role = session?.role ?? null
  const location = useLocation()
  const navigate = useNavigate()
  const state = location.state as LocationState | null
  const [search, setSearch] = useState('')
  const [toDelete, setToDelete] = useState<RawMaterial | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const [actionError, setActionError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(
    state?.message ?? null,
  )

  const { data, isLoading, error, reload } = useApiData(
    () => listMaterials({ limit: 100 }),
    [],
  )

  const materials = data ?? []
  const term = search.trim().toLowerCase()
  const filtered = term
    ? materials.filter(
        (material) =>
          material.name.toLowerCase().includes(term) ||
          material.category.toLowerCase().includes(term),
      )
    : materials

  const handleDelete = async () => {
    if (!toDelete) return
    setActionError(null)
    setIsDeleting(true)
    try {
      await deleteMaterial(toDelete.id)
      setSuccessMessage(`Material "${toDelete.name}" eliminado.`)
      setToDelete(null)
      await reload()
    } catch (requestError) {
      setActionError(getErrorMessage(requestError))
    } finally {
      setIsDeleting(false)
    }
  }

  if (isLoading) {
    return <LoadingScreen message="Cargando materiales…" />
  }

  if (error) {
    return <ErrorState message={error} onRetry={reload} />
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Materias primas"
        description="Catálogo e inventario disponible. El stock se descuenta al registrar un pedido y se devuelve al cancelarlo."
        actions={
          can(role, 'materials:create') ? (
            <LinkButton to="/materials/new">
              <Icon name="plus" className="h-4 w-4" />
              Nuevo material
            </LinkButton>
          ) : undefined
        }
      />

      {successMessage ? (
        <Alert tone="success">{successMessage}</Alert>
      ) : null}
      {actionError ? <Alert tone="error">{actionError}</Alert> : null}

      <Card>
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 p-4">
          <div className="relative w-full max-w-sm">
            <Icon
              name="search"
              className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
            />
            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Buscar por nombre o categoría"
              aria-label="Buscar materiales"
              className={`${inputClass} pl-9`}
            />
          </div>
          <p className="text-sm text-slate-500">
            {filtered.length} de {materials.length} materiales
          </p>
        </div>

        {materials.length === 0 ? (
          <div className="p-5">
            <EmptyState
              title="No hay materiales registrados"
              description="El catálogo está vacío. Un administrador puede registrar la primera materia prima."
              action={
                can(role, 'materials:create') ? (
                  <LinkButton to="/materials/new">Crear material</LinkButton>
                ) : undefined
              }
            />
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-5">
            <EmptyState
              title="Sin coincidencias"
              description="Prueba con otro nombre o categoría."
              action={
                <Button variant="secondary" onClick={() => setSearch('')}>
                  Limpiar búsqueda
                </Button>
              }
            />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-5 py-3 font-medium">Material</th>
                  <th className="px-5 py-3 font-medium">Categoría</th>
                  <th className="px-5 py-3 font-medium">Precio</th>
                  <th className="px-5 py-3 font-medium">Stock</th>
                  <th className="px-5 py-3 font-medium">Estado</th>
                  <th className="px-5 py-3 text-right font-medium">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {filtered.map((material) => (
                  <tr key={material.id}>
                    <td className="px-5 py-4">
                      <p className="font-medium text-slate-900">
                        {material.name}
                      </p>
                      {material.description ? (
                        <p className="mt-0.5 max-w-xs truncate text-xs text-slate-500">
                          {material.description}
                        </p>
                      ) : null}
                    </td>
                    <td className="px-5 py-4 text-slate-600">
                      {material.category}
                    </td>
                    <td className="px-5 py-4 text-slate-700">
                      {formatCurrency(material.price)}
                      <span className="ml-1 text-xs text-slate-400">
                        / {material.unit}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <span
                        className={
                          material.stock <= 0
                            ? 'font-medium text-rose-600'
                            : 'text-slate-700'
                        }
                      >
                        {formatQuantity(material.stock)} {material.unit}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <Badge
                        className={
                          material.is_active
                            ? 'bg-emerald-100 text-emerald-800 ring-emerald-200'
                            : 'bg-slate-100 text-slate-600 ring-slate-200'
                        }
                      >
                        {material.is_active ? 'Activo' : 'Inactivo'}
                      </Badge>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex justify-end gap-1">
                        {can(role, 'orders:create') ? (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => navigate('/orders/new')}
                            disabled={!material.is_active || material.stock <= 0}
                          >
                            Pedir
                          </Button>
                        ) : null}
                        {can(role, 'materials:update') ? (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() =>
                              navigate(`/materials/${material.id}/edit`)
                            }
                          >
                            <Icon name="edit" className="h-4 w-4" />
                            Editar
                          </Button>
                        ) : null}
                        {can(role, 'materials:delete') ? (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-rose-600 hover:bg-rose-50 hover:text-rose-700"
                            onClick={() => setToDelete(material)}
                          >
                            <Icon name="trash" className="h-4 w-4" />
                            Eliminar
                          </Button>
                        ) : null}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      <ConfirmDialog
        open={toDelete !== null}
        title="Eliminar material"
        description={`Se eliminará permanentemente "${toDelete?.name ?? ''}". Esta operación es un borrado físico y no se puede deshacer.`}
        confirmLabel="Eliminar"
        isConfirming={isDeleting}
        onConfirm={handleDelete}
        onCancel={() => setToDelete(null)}
      />
    </div>
  )
}
