import type { UserRole } from '../types/api'

export type Permission =
  | 'materials:create'
  | 'materials:update'
  | 'materials:delete'
  | 'orders:create'
  | 'orders:update-status'
  | 'audit:view'

const permissionRoles: Record<Permission, readonly UserRole[]> = {
  'materials:create': ['admin'],
  'materials:update': ['admin', 'analista'],
  'materials:delete': ['admin'],
  'orders:create': ['cliente'],
  'orders:update-status': ['admin', 'analista'],
  'audit:view': ['admin', 'analista'],
}

export function can(role: UserRole | null, permission: Permission): boolean {
  return role !== null && permissionRoles[permission].includes(role)
}

export function isStaff(role: UserRole | null): boolean {
  return role === 'admin' || role === 'analista'
}
