import type { ReactNode } from 'react'
import { APP_NAME } from '../../config/env'
import { Icon } from '../ui/Icon'

const highlights = [
  'Consulta disponibilidad de materias primas en tiempo real.',
  'Registra y sigue tus pedidos desde un solo lugar.',
  'Solicita asesoría técnica cuando la necesites.',
]

export function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-100 lg:grid lg:grid-cols-2">
      <aside className="relative hidden overflow-hidden bg-teal-800 p-12 text-white lg:flex lg:flex-col lg:justify-between">
        <div className="absolute -right-24 -top-24 h-80 w-80 rounded-full bg-teal-700/60" />
        <div className="absolute -bottom-32 -left-16 h-96 w-96 rounded-full bg-teal-900/50" />

        <div className="relative">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-white/15 text-xl font-bold">
              K
            </div>
            <div>
              <p className="text-lg font-semibold">{APP_NAME}</p>
              <p className="text-sm text-teal-100">
                Distribución de materias primas
              </p>
            </div>
          </div>
          <h1 className="mt-16 max-w-md text-4xl font-semibold leading-tight">
            Gestión de inventario y pedidos para tu operación química.
          </h1>
          <p className="mt-4 max-w-md text-base leading-relaxed text-teal-100">
            Un espacio único para consultar productos, registrar pedidos y
            recibir acompañamiento técnico.
          </p>
        </div>

        <ul className="relative mt-12 space-y-4">
          {highlights.map((item) => (
            <li key={item} className="flex items-start gap-3 text-sm text-teal-50">
              <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-white/15">
                <Icon name="check" className="h-4 w-4" />
              </span>
              {item}
            </li>
          ))}
        </ul>
      </aside>

      <main className="flex min-h-screen items-center justify-center px-4 py-10 sm:px-8">
        <div className="w-full max-w-md">{children}</div>
      </main>
    </div>
  )
}
