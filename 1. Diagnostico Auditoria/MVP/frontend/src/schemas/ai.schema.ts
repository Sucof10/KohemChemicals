import { z } from 'zod'

export const aiChatSchema = z.object({
  message: z
    .string()
    .trim()
    .min(1, 'Escribe una consulta.')
    .max(1000, 'La consulta no puede superar 1000 caracteres.'),
})

export type AIChatFormValues = z.infer<typeof aiChatSchema>
