import type { ReactNode } from 'react'
import { cn } from '../../utils/cn'

type AlertTone = 'error' | 'success' | 'info' | 'warning'

const tones: Record<AlertTone, string> = {
  error: 'border-rose-200 bg-rose-50 text-rose-800',
  success: 'border-emerald-200 bg-emerald-50 text-emerald-800',
  info: 'border-sky-200 bg-sky-50 text-sky-800',
  warning: 'border-amber-200 bg-amber-50 text-amber-800',
}

export function Alert({
  tone = 'info',
  children,
  className,
}: {
  tone?: AlertTone
  children: ReactNode
  className?: string
}) {
  return (
    <div
      role={tone === 'error' ? 'alert' : 'status'}
      className={cn(
        'rounded-xl border px-4 py-3 text-sm leading-relaxed',
        tones[tone],
        className,
      )}
    >
      {children}
    </div>
  )
}
