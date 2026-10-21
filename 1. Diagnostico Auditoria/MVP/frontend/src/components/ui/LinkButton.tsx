import type { ComponentProps } from 'react'
import { Link } from 'react-router-dom'
import { cn } from '../../utils/cn'

type Variant = 'primary' | 'secondary' | 'ghost'

const variants: Record<Variant, string> = {
  primary: 'bg-teal-700 text-white shadow-sm hover:bg-teal-800',
  secondary:
    'border border-slate-300 bg-white text-slate-700 hover:bg-slate-50',
  ghost: 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
}

export function LinkButton({
  variant = 'primary',
  className,
  children,
  ...props
}: ComponentProps<typeof Link> & { variant?: Variant }) {
  return (
    <Link
      className={cn(
        'inline-flex h-10 items-center justify-center gap-2 rounded-lg px-4 text-sm font-medium transition focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700',
        variants[variant],
        className,
      )}
      {...props}
    >
      {children}
    </Link>
  )
}
