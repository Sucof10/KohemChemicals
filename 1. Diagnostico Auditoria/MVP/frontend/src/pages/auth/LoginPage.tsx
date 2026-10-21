import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { normalizeApiError } from '../../api/errors'
import { useAuth } from '../../auth/useAuth'
import { Alert } from '../../components/feedback/Alert'
import { AuthLayout } from '../../components/layout/AuthLayout'
import { Button } from '../../components/ui/Button'
import { FormField } from '../../components/ui/FormField'
import { inputClass } from '../../components/ui/formStyles'
import {
  loginSchema,
  type LoginFormValues,
} from '../../schemas/auth.schema'

interface LocationState {
  from?: string
  registered?: boolean
}

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const state = location.state as LocationState | null
  const [serverError, setServerError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { username: '', password: '' },
  })

  const onSubmit = handleSubmit(async (values) => {
    setServerError(null)
    setIsSubmitting(true)
    try {
      await login(values)
      navigate(state?.from ?? '/', { replace: true })
    } catch (error) {
      const normalized = normalizeApiError(error)
      if (normalized.status === 401) {
        setServerError('Usuario o contraseña incorrectos.')
      } else {
        setServerError(normalized.message)
      }
      if (normalized.fieldErrors.username) {
        setError('username', {
          type: 'server',
          message: normalized.fieldErrors.username,
        })
      }
      if (normalized.fieldErrors.password) {
        setError('password', {
          type: 'server',
          message: normalized.fieldErrors.password,
        })
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
          Inicia sesión
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Accede con tu usuario para gestionar pedidos, inventario y asesorías.
        </p>

        {state?.registered ? (
          <Alert tone="success" className="mt-5">
            Usuario registrado correctamente. Ya puedes iniciar sesión.
          </Alert>
        ) : null}

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
            label="Contraseña"
            htmlFor="password"
            required
            error={errors.password?.message}
          >
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              className={inputClass}
              aria-invalid={Boolean(errors.password)}
              {...register('password')}
            />
          </FormField>

          <Button type="submit" className="w-full" isLoading={isSubmitting}>
            Entrar
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-500">
          ¿No tienes cuenta?{' '}
          <Link
            to="/register"
            className="font-medium text-teal-700 hover:text-teal-800"
          >
            Regístrate
          </Link>
        </p>

        {import.meta.env.DEV ? (
          <div className="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs leading-relaxed text-slate-500">
            <p className="font-semibold text-slate-700">
              Credenciales de demostración
            </p>
            <p>Administrador: admin / AdminPass123!</p>
            <p>Cliente: cliente / ClientPass123!</p>
          </div>
        ) : null}
      </div>
    </AuthLayout>
  )
}
