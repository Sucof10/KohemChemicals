import { describe, expect, it } from 'vitest'
import { decodeSessionToken } from '../auth/jwt'
import { isExpired } from '../utils/format'
import { createTestToken } from './helpers'

describe('decodeSessionToken', () => {
  it('decodifica los claims reales del backend', () => {
    const token = createTestToken('analista')
    const session = decodeSessionToken(token)
    expect(session).not.toBeNull()
    expect(session?.username).toBe('testuser')
    expect(session?.role).toBe('analista')
    expect(session?.userId).toBe(7)
  })

  it('rechaza un rol desconocido', () => {
    const token = createTestToken('cliente', { role: 'superadmin' })
    expect(decodeSessionToken(token)).toBeNull()
  })

  it('rechaza un token malformado', () => {
    expect(decodeSessionToken('no-es-un-jwt')).toBeNull()
  })

  it('detecta la expiración', () => {
    const expired = Math.floor(Date.now() / 1000) - 10
    expect(isExpired(expired)).toBe(true)
  })
})
