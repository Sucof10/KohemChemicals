import type { UserRole } from '../types/api'

function encodeBase64Url(value: Record<string, unknown>): string {
  return btoa(JSON.stringify(value))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '')
}

export function createTestToken(
  role: UserRole = 'cliente',
  overrides: Record<string, unknown> = {},
): string {
  const header = encodeBase64Url({ alg: 'HS256', typ: 'JWT' })
  const payload = encodeBase64Url({
    sub: 'testuser',
    role,
    user_id: 7,
    exp: Math.floor(Date.now() / 1000) + 3600,
    ...overrides,
  })
  return `${header}.${payload}.firma-de-prueba`
}
