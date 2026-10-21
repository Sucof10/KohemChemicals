import { describe, expect, it } from 'vitest'
import { loginSchema, registerSchema } from '../schemas/auth.schema'
import { materialFormSchema } from '../schemas/material.schema'
import { orderFormSchema } from '../schemas/order.schema'
import { aiChatSchema } from '../schemas/ai.schema'

describe('auth schemas', () => {
  it('rechaza un login vacío', () => {
    expect(loginSchema.safeParse({ username: '', password: '' }).success).toBe(
      false,
    )
  })

  it('rechaza un correo inválido y una contraseña corta', () => {
    const result = registerSchema.safeParse({
      username: 'usuario',
      email: 'correo-invalido',
      password: 'corta',
      confirmPassword: 'corta',
    })
    expect(result.success).toBe(false)
  })

  it('rechaza contraseñas que no coinciden', () => {
    const result = registerSchema.safeParse({
      username: 'usuario',
      email: 'usuario@kohem.com',
      password: 'Password123!',
      confirmPassword: 'Password123',
    })
    expect(result.success).toBe(false)
  })
})

describe('material schema', () => {
  it('rechaza precio cero y stock negativo', () => {
    const result = materialFormSchema.safeParse({
      name: 'Glicerina',
      category: 'Humectantes',
      unit: 'kg',
      price: 0,
      stock: -1,
      description: '',
    })
    expect(result.success).toBe(false)
  })

  it('acepta un material válido', () => {
    const result = materialFormSchema.safeParse({
      name: 'Glicerina',
      category: 'Humectantes',
      unit: 'kg',
      price: 18000,
      stock: 10,
      description: 'Materia prima',
    })
    expect(result.success).toBe(true)
  })
})

describe('order schema', () => {
  it('rechaza un pedido sin líneas', () => {
    expect(orderFormSchema.safeParse({ items: [] }).success).toBe(false)
  })

  it('rechaza cantidades no positivas', () => {
    const result = orderFormSchema.safeParse({
      items: [{ raw_material_id: 1, quantity: 0 }],
    })
    expect(result.success).toBe(false)
  })

  it('acepta un pedido válido', () => {
    const result = orderFormSchema.safeParse({
      items: [{ raw_material_id: 1, quantity: 2 }],
      notes: 'Pedido de prueba',
    })
    expect(result.success).toBe(true)
  })
})

describe('AI schema', () => {
  it('rechaza mensajes vacíos o mayores a 1000 caracteres', () => {
    expect(aiChatSchema.safeParse({ message: '   ' }).success).toBe(false)
    expect(
      aiChatSchema.safeParse({ message: 'a'.repeat(1001) }).success,
    ).toBe(false)
  })
})
