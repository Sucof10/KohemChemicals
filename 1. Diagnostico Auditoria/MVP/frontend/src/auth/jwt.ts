import { jwtDecode } from 'jwt-decode'
import { USER_ROLES, type UserRole } from '../types/api'

export interface SessionUser {
  username: string
  role: UserRole
  userId: number
  expiresAt: number
}

function isUserRole(value: unknown): value is UserRole {
  return (
    typeof value === 'string' &&
    (USER_ROLES as readonly string[]).includes(value)
  )
}

export function decodeSessionToken(token: string): SessionUser | null {
  try {
    const payload = jwtDecode<Record<string, unknown>>(token)
    if (
      typeof payload.sub !== 'string' ||
      typeof payload.user_id !== 'number' ||
      typeof payload.exp !== 'number' ||
      !isUserRole(payload.role)
    ) {
      return null
    }

    return {
      username: payload.sub,
      role: payload.role,
      userId: payload.user_id,
      expiresAt: payload.exp,
    }
  } catch {
    return null
  }
}
