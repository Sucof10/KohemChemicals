import { Spinner } from './Spinner'

export function LoadingScreen({ message = 'Cargando…' }: { message?: string }) {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-3 text-slate-500">
      <Spinner className="h-8 w-8 text-teal-700" />
      <p className="text-sm">{message}</p>
    </div>
  )
}
