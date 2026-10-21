import { http, HttpResponse } from 'msw'
import { describe, expect, it } from 'vitest'
import { login, register } from '../api/services/auth.service'
import {
  createMaterial,
  listMaterials,
} from '../api/services/materials.service'
import { updateOrderStatus } from '../api/services/orders.service'
import { storeToken } from '../auth/tokenStorage'
import type { Order, RawMaterial } from '../types/api'
import { createTestToken } from './helpers'
import { server } from './server'

const api = 'http://localhost:8000/api/v1'

const material: RawMaterial = {
  id: 1,
  name: 'Glicerina vegetal',
  category: 'Humectantes',
  unit: 'kg',
  price: 18000,
  stock: 100,
  description: null,
  is_active: true,
}

const order: Order = {
  id: 5,
  customer_id: 2,
  status: 'confirmado',
  total: 36000,
  notes: null,
  items: [
    {
      id: 10,
      raw_material_id: 1,
      quantity: 2,
      unit_price: 18000,
      subtotal: 36000,
    },
  ],
  created_at: '2026-10-19T10:00:00',
  updated_at: '2026-10-19T10:05:00',
}

describe('auth service', () => {
  it('envía el login como JSON al endpoint real', async () => {
    let body: unknown
    server.use(
      http.post(`${api}/auth/token`, async ({ request }) => {
        body = await request.json()
        return HttpResponse.json({
          access_token: createTestToken('admin'),
          token_type: 'bearer',
        })
      }),
    )

    const response = await login({
      username: 'admin',
      password: 'AdminPass123!',
    })

    expect(body).toEqual({
      username: 'admin',
      password: 'AdminPass123!',
    })
    expect(response.token_type).toBe('bearer')
    expect(response.access_token.split('.')).toHaveLength(3)
  })

  it('el registro no envía el campo role', async () => {
    let body: Record<string, unknown> = {}
    server.use(
      http.post(`${api}/auth/register`, async ({ request }) => {
        body = (await request.json()) as Record<string, unknown>
        return HttpResponse.json(
          {
            id: 3,
            username: 'nuevo',
            email: 'nuevo@kohem.com',
            role: 'cliente',
            is_active: true,
          },
          { status: 201 },
        )
      }),
    )

    const response = await register({
      username: 'nuevo',
      email: 'nuevo@kohem.com',
      password: 'Password123!',
    })

    expect(body).not.toHaveProperty('role')
    expect(response.role).toBe('cliente')
  })
})

describe('materials service', () => {
  it('lista materiales con paginación', async () => {
    server.use(
      http.get(`${api}/materials`, ({ request }) => {
        const url = new URL(request.url)
        expect(url.searchParams.get('limit')).toBe('100')
        return HttpResponse.json([material])
      }),
    )

    const result = await listMaterials({ limit: 100 })
    expect(result).toHaveLength(1)
    expect(result[0]?.name).toBe('Glicerina vegetal')
  })

  it('adjunta el Bearer token al crear un material', async () => {
    storeToken(createTestToken('admin'))
    let authorization: string | null = null
    let body: Record<string, unknown> = {}

    server.use(
      http.post(`${api}/materials`, async ({ request }) => {
        authorization = request.headers.get('Authorization')
        body = (await request.json()) as Record<string, unknown>
        return HttpResponse.json(material, { status: 201 })
      }),
    )

    const created = await createMaterial({
      name: 'Glicerina vegetal',
      category: 'Humectantes',
      unit: 'kg',
      price: 18000,
      stock: 100,
    })

    expect(authorization).toMatch(/^Bearer /)
    expect(body.name).toBe('Glicerina vegetal')
    expect(created.id).toBe(1)
  })
})

describe('orders service', () => {
  it('cambia el estado con PATCH y JSON', async () => {
    storeToken(createTestToken('admin'))
    let method = ''
    let body: Record<string, unknown> = {}

    server.use(
      http.patch(`${api}/orders/5/status`, async ({ request }) => {
        method = request.method
        body = (await request.json()) as Record<string, unknown>
        return HttpResponse.json(order)
      }),
    )

    const result = await updateOrderStatus(5, 'confirmado')

    expect(method).toBe('PATCH')
    expect(body).toEqual({ status: 'confirmado' })
    expect(result.status).toBe('confirmado')
    expect(result.total).toBe(36000)
  })
})
