import { LinkButton } from '../../components/ui/LinkButton'

export function ForbiddenPage() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
      <p className="text-sm font-semibold uppercase tracking-wide text-rose-600">
        Error 403
      </p>
      <h1 className="mt-2 text-3xl font-semibold text-slate-900">
        No tienes permisos para esta sección
      </h1>
      <p className="mt-2 max-w-md text-sm text-slate-500">
        Tu rol no permite acceder a esta vista. Si crees que es un error,
        contacta a un administrador.
      </p>
      <LinkButton to="/" className="mt-6">
        Volver al panel
      </LinkButton>
    </div>
  )
}
