import { LinkButton } from '../../components/ui/LinkButton'

export function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
      <p className="text-sm font-semibold uppercase tracking-wide text-teal-700">
        Error 404
      </p>
      <h1 className="mt-2 text-3xl font-semibold text-slate-900">
        Página no encontrada
      </h1>
      <p className="mt-2 max-w-md text-sm text-slate-500">
        La dirección solicitada no existe o fue movida.
      </p>
      <LinkButton to="/" className="mt-6">
        Volver al panel
      </LinkButton>
    </div>
  )
}
