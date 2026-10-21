import { z } from 'zod'

const descriptionSchema = z
  .string()
  .trim()
  .max(500, 'La descripción no puede superar 500 caracteres.')
  .optional()

export const materialFormSchema = z.object({
  name: z
    .string()
    .trim()
    .min(2, 'El nombre debe tener al menos 2 caracteres.')
    .max(120, 'El nombre no puede superar 120 caracteres.'),
  category: z
    .string()
    .trim()
    .min(2, 'La categoría debe tener al menos 2 caracteres.')
    .max(80, 'La categoría no puede superar 80 caracteres.'),
  unit: z
    .string()
    .trim()
    .min(1, 'La unidad es obligatoria.')
    .max(20, 'La unidad no puede superar 20 caracteres.'),
  price: z
    .number({ error: 'Ingresa un precio válido.' })
    .positive('El precio debe ser mayor que cero.'),
  stock: z
    .number({ error: 'Ingresa un stock válido.' })
    .min(0, 'El stock no puede ser negativo.'),
  description: descriptionSchema,
})

export type MaterialFormValues = z.infer<typeof materialFormSchema>
