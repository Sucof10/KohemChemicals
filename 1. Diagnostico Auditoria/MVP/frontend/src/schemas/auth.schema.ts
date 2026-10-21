import { z } from 'zod'

export const loginSchema = z.object({
  username: z
    .string()
    .trim()
    .min(1, 'Ingresa tu usuario.')
    .max(50, 'El usuario no puede superar 50 caracteres.'),
  password: z.string().min(1, 'Ingresa tu contraseña.'),
})

export const registerSchema = z
  .object({
    username: z
      .string()
      .trim()
      .min(3, 'El usuario debe tener al menos 3 caracteres.')
      .max(50, 'El usuario no puede superar 50 caracteres.'),
    email: z
      .string()
      .trim()
      .min(1, 'Ingresa un correo electrónico.')
      .email('Ingresa un correo electrónico válido.'),
    password: z
      .string()
      .min(8, 'La contraseña debe tener al menos 8 caracteres.'),
    confirmPassword: z.string().min(1, 'Confirma la contraseña.'),
  })
  .superRefine((values, context) => {
    if (values.password !== values.confirmPassword) {
      context.addIssue({
        code: 'custom',
        path: ['confirmPassword'],
        message: 'Las contraseñas no coinciden.',
      })
    }
  })

export type LoginFormValues = z.infer<typeof loginSchema>
export type RegisterFormValues = z.infer<typeof registerSchema>
