import { describe, expect, it } from 'vitest'
import { can, isStaff } from '../utils/permissions'

describe('permissions matrix', () => {
  it('solo admin crea y elimina materiales', () => {
    expect(can('admin', 'materials:create')).toBe(true)
    expect(can('analista', 'materials:create')).toBe(false)
    expect(can('cliente', 'materials:create')).toBe(false)
    expect(can('admin', 'materials:delete')).toBe(true)
    expect(can('analista', 'materials:delete')).toBe(false)
  })

  it('admin y analista editan materiales y pedidos', () => {
    expect(can('admin', 'materials:update')).toBe(true)
    expect(can('analista', 'materials:update')).toBe(true)
    expect(can('cliente', 'materials:update')).toBe(false)
    expect(can('admin', 'orders:update-status')).toBe(true)
    expect(can('analista', 'orders:update-status')).toBe(true)
    expect(can('cliente', 'orders:update-status')).toBe(false)
  })

  it('solo el cliente crea pedidos', () => {
    expect(can('cliente', 'orders:create')).toBe(true)
    expect(can('admin', 'orders:create')).toBe(false)
    expect(can('analista', 'orders:create')).toBe(false)
  })

  it('solo admin y analista ven auditoría', () => {
    expect(can('admin', 'audit:view')).toBe(true)
    expect(can('analista', 'audit:view')).toBe(true)
    expect(can('cliente', 'audit:view')).toBe(false)
  })

  it('identifica al personal interno', () => {
    expect(isStaff('admin')).toBe(true)
    expect(isStaff('analista')).toBe(true)
    expect(isStaff('cliente')).toBe(false)
    expect(isStaff(null)).toBe(false)
  })
})
