import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate, useParams } from 'react-router-dom'
import { normalizeApiError } from '../../api/errors'
import {
  createMaterial,
  getMaterial,
  updateMaterial,
} from '../../api/services/materials.service'
import { Alert } from '../../components/feedback/Alert'
import { ErrorState } from '../../components/feedback/ErrorState'
import { LoadingScreen } from '../../components/feedback/LoadingScreen'
import { Button } from '../../components/ui/Button'
import { Card } from '../../components/ui/Card'
import { FormField } from '../../components/ui/FormField'
import { inputClass, textareaClass } from '../../components/ui/formStyles'
import { LinkButton } from '../../components/ui/LinkButton'
import { PageHeader } from '../../components/ui/PageHeader'
import { useApiData } from '../../hooks/useApiData'
import {
  materialFormSchema,
  type MaterialFormValues,
} from '../../schemas/material.schema'
import type { RawMaterial } from '../../types/api'

const editableFields = [
  'name',
  'category',
  'unit',
  'price',
  'stock',
  'description',
] as const

export function MaterialFormPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const isEdit = id !== undefined
  const materialId = Number(id)
  const [serverError, setServerError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const {
    data: material,
    isLoading,
    error,
    reload,
  } = useApiData<RawMaterial | null>(
    () =>
      isEdit && Number.isFinite(materialId)
        ? getMaterial(materialId)
        : Promise.resolve(null),
    [isEdit, materialId],
  )

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
    setError,
  } = useForm<MaterialFormValues>({
    resolver: zodResolver(materialFormSchema),
    defaultValues: {
      name: '',
      category: '',
      unit: '',
      price: 0,
      stock: 0,
      description: '',
    },
  })

  useEffect(() => {
    if (material) {
      reset({
        name: material.name,
        category: material.category,
        unit: material.unit,
        price: material.price,
        stock: material.stock,
        description: material.description ?? '',
      })
    }
  }, [material, reset])

  const onSubmit = handleSubmit(async (values) => {
    setServerError(null)
    setIsSubmitting(true)
    const payload = {
      name: values.name.trim(),
      category: values.category.trim(),
      unit: values.unit.trim(),
      price: values.price,
      stock: values.stock,
      description: values.description?.trim() || undefined,
    }
    try {
      if (isEdit) {
        await updateMaterial(materialId, payload)
      } else {
        await createMaterial(payload)
      }
      navigate('/materials', {
        replace: true,
        state: {
          message: isEdit
            ? 'Material actualizado correctamente.'
            : 'Material creado correctamente.',
        },
      })
    } catch (requestError) {
      const normalized = normalizeApiError(requestError)
      setServerError(normalized.message)
      for (const field of editableFields) {
        const message = normalized.fieldErrors[field]
        if (message) {
          setError(field, { type: 'server', message })
        }
      }
    } finally {
      setIsSubmitting(false)
    }
  })

  if (isEdit && isLoading) {
    return <LoadingScreen message="Cargando material…" />
  }

  if (isEdit && error) {
    return <ErrorState message={error} onRetry={reload} />
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={isEdit ? 'Editar material' : 'Nuevo material'}
        description={
          isEdit
            ? 'Actualiza la información del catálogo. Los cambios de stock se reflejan de inmediato.'
            : 'Registra una nueva materia prima en el catálogo e inventario.'
        }
      />

      {serverError ? <Alert tone="error">{serverError}</Alert> : null}

      <Card className="max-w-3xl p-5 sm:p-6">
        <form className="space-y-5" onSubmit={onSubmit} noValidate>
          <div className="grid gap-5 sm:grid-cols-2">
            <FormField
              label="Nombre"
              htmlFor="name"
              required
              error={errors.name?.message}
              className="sm:col-span-2"
            >
              <input
                id="name"
                type="text"
                className={inputClass}
                aria-invalid={Boolean(errors.name)}
                {...register('name')}
              />
            </FormField>

            <FormField
              label="Categoría"
              htmlFor="category"
              required
              error={errors.category?.message}
            >
              <input
                id="category"
                type="text"
                className={inputClass}
                aria-invalid={Boolean(errors.category)}
                {...register('category')}
              />
            </FormField>

            <FormField
              label="Unidad de medida"
              htmlFor="unit"
              required
              error={errors.unit?.message}
              hint="Ejemplo: kg, L, g."
            >
              <input
                id="unit"
                type="text"
                className={inputClass}
                aria-invalid={Boolean(errors.unit)}
                {...register('unit')}
              />
            </FormField>

            <FormField
              label="Precio"
              htmlFor="price"
              required
              error={errors.price?.message}
              hint="Debe ser mayor que cero. El precio se expresa en la moneda del sistema."
            >
              <input
                id="price"
                type="number"
                inputMode="decimal"
                min="0"
                step="0.01"
                className={inputClass}
                aria-invalid={Boolean(errors.price)}
                {...register('price', { valueAsNumber: true })}
              />
            </FormField>

            <FormField
              label="Stock"
              htmlFor="stock"
              required
              error={errors.stock?.message}
              hint="No puede ser negativo."
            >
              <input
                id="stock"
                type="number"
                inputMode="decimal"
                min="0"
                step="0.0001"
                className={inputClass}
                aria-invalid={Boolean(errors.stock)}
                {...register('stock', { valueAsNumber: true })}
              />
            </FormField>

            <FormField
              label="Descripción"
              htmlFor="description"
              error={errors.description?.message}
              hint="Máximo 500 caracteres."
              className="sm:col-span-2"
            >
              <textarea
                id="description"
                rows={4}
                className={textareaClass}
                aria-invalid={Boolean(errors.description)}
                {...register('description')}
              />
            </FormField>
          </div>

          <div className="flex flex-wrap justify-end gap-2 border-t border-slate-200 pt-5">
            <LinkButton to="/materials" variant="secondary">
              Cancelar
            </LinkButton>
            <Button type="submit" isLoading={isSubmitting}>
              {isEdit ? 'Guardar cambios' : 'Crear material'}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  )
}
