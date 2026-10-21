import type { OrderStatus, UserRole } from '../types/api'

export const ROLE_LABELS: Record<UserRole, string> = {
  admin: 'Administrador',
  analista: 'Analista',
  cliente: 'Cliente',
}

export const ORDER_STATUS_LABELS: Record<OrderStatus, string> = {
  pendiente: 'Pendiente',
  confirmado: 'Confirmado',
  preparando: 'Preparando',
  enviado: 'Enviado',
  entregado: 'Entregado',
  cancelado: 'Cancelado',
}

export const ORDER_STATUS_STYLES: Record<OrderStatus, string> = {
  pendiente: 'bg-amber-100 text-amber-800 ring-amber-200',
  confirmado: 'bg-sky-100 text-sky-800 ring-sky-200',
  preparando: 'bg-indigo-100 text-indigo-800 ring-indigo-200',
  enviado: 'bg-violet-100 text-violet-800 ring-violet-200',
  entregado: 'bg-emerald-100 text-emerald-800 ring-emerald-200',
  cancelado: 'bg-rose-100 text-rose-800 ring-rose-200',
}
