import { z } from 'zod'
import { ORDER_STATUSES } from '../types/api'

export const orderItemSchema = z.object({
  raw_material_id: z
    .number({ error: 'Selecciona una materia prima.' })
    .int('La materia prima no es válida.')
    .positive('La materia prima no es válida.'),
  quantity: z
    .number({ error: 'Ingresa una cantidad válida.' })
    .positive('La cantidad debe ser mayor que cero.'),
})

export const orderFormSchema = z.object({
  items: z.array(orderItemSchema).min(1, 'Agrega al menos una materia prima.'),
  notes: z
    .string()
    .trim()
    .max(500, 'Las notas no pueden superar 500 caracteres.')
    .optional(),
})

export const orderStatusSchema = z.object({
  status: z.enum(ORDER_STATUSES),
})

export type OrderFormValues = z.infer<typeof orderFormSchema>
export type OrderItemFormValues = z.infer<typeof orderItemSchema>
