import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { normalizeApiError } from '../../api/errors'
import { register as registerUser } from '../../api/services/auth.service'
import { Alert } from '../../components/feedback/Alert'
import { AuthLayout } from '../../components/layout/AuthLayout'
import { Button } from '../../components/ui/Button'
import { FormField } from '../../components/ui/FormField'
import { inputClass } from '../../components/ui/formStyles'
import {
  registerSchema,
  type RegisterFormValues,
} from '../../schemas/auth.schema'

const fieldNames = ['username', 'email', 'password', 'confirmPassword'] as const

export function RegisterPage() {
  const navigate = useNavigate()
  const [serverError, setServerError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
    },
  })

  const onSubmit = handleSubmit(async (values) => {
    setServerError(null)
    setIsSubmitting(true)
    try {
      await registerUser({
        username: values.username,
        email: values.email,
        password: values.password,
      })
      navigate('/login', { replace: true, state: { registered: true } })
    } catch (error) {
      const normalized = normalizeApiError(error)
      setServerError(normalized.message)
      for (const field of fieldNames) {
        const message = normalized.fieldErrors[field]
        if (message) {
          setError(field, { type: 'server', message })
        }
      }
    } finally {
      setIsSubmitting(false)
    }
  })

  return (
    <AuthLayout>
      <div className="rounded-2xl border border-slate-200 bg-white p-7 shadow-sm sm:p-8">
        <p className="text-sm font-semibold uppercase tracking-wide text-teal-700">
          Kohem Chemicals
        </p>
        <h1 className="mt-2 text-2xl font-semibold text-slate-900">
          Crea tu cuenta
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Las cuentas nuevas se crean con rol Cliente. Un administrador puede
          gestionar los demás roles desde la API.
        </p>

        {serverError ? (
          <Alert tone="error" className="mt-5">
            {serverError}
          </Alert>
        ) : null}

        <form className="mt-6 space-y-4" onSubmit={onSubmit} noValidate>
          <FormField
            label="Usuario"
            htmlFor="username"
            required
            error={errors.username?.message}
            hint="Entre 3 y 50 caracteres."
          >
            <input
              id="username"
              type="text"
              autoComplete="username"
              className={inputClass}
              aria-invalid={Boolean(errors.username)}
              {...register('username')}
            />
          </FormField>

          <FormField
            label="Correo electrónico"
            htmlFor="email"
            required
            error={errors.email?.message}
          >
            <input
              id="email"
              type="email"
              autoComplete="email"
              className={inputClass}
              aria-invalid={Boolean(errors.email)}
              {...register('email')}
            />
          </FormField>

          <FormField
            label="Contraseña"
            htmlFor="password"
            required
            error={errors.password?.message}
            hint="Mínimo 8 caracteres."
          >
            <input
              id="password"
              type="password"
              autoComplete="new-password"
              className={inputClass}
              aria-invalid={Boolean(errors.password)}
              {...register('password')}
            />
          </FormField>

          <FormField
            label="Confirmar contraseña"
            htmlFor="confirmPassword"
            required
            error={errors.confirmPassword?.message}
          >
            <input
              id="confirmPassword"
              type="password"
              autoComplete="new-password"
              className={inputClass}
              aria-invalid={Boolean(errors.confirmPassword)}
              {...register('confirmPassword')}
            />
          </FormField>

          <Button type="submit" className="w-full" isLoading={isSubmitting}>
            Crear cuenta
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-500">
          ¿Ya tienes cuenta?{' '}
          <Link
            to="/login"
            className="font-medium text-teal-700 hover:text-teal-800"
          >
            Inicia sesión
          </Link>
        </p>
      </div>
    </AuthLayout>
  )
}
