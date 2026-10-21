const hasTimezone = /(Z|[+-]\d{2}:?\d{2})$/i

export function parseApiDate(value: string): Date {
  return new Date(hasTimezone.test(value) ? value : `${value}Z`)
}

export function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat('es-CO', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(parseApiDate(value))
}

export function formatDate(value: string): string {
  return new Intl.DateTimeFormat('es-CO', { dateStyle: 'medium' }).format(
    parseApiDate(value),
  )
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(value)
}

export function formatQuantity(value: number): string {
  return new Intl.NumberFormat('es-CO', {
    maximumFractionDigits: 4,
  }).format(value)
}

export function isExpired(expiresAt: number): boolean {
  return expiresAt * 1000 <= Date.now()
}
