import { AxiosError, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios'
import { describe, expect, it } from 'vitest'
import { normalizeApiError } from '../api/errors'

function createAxiosError(status: number, data: unknown): AxiosError {
  const config = {} as InternalAxiosRequestConfig
  const response = {
    status,
    statusText: '',
    data,
    headers: {},
    config,
  } as AxiosResponse
  return new AxiosError('Request failed', 'ERR_BAD_RESPONSE', config, undefined, response)
}

describe('normalizeApiError', () => {
  it('mapea errores 422 por campo sin exponer mensajes técnicos', () => {
    const result = normalizeApiError(
      createAxiosError(422, {
        detail: [
          {
            loc: ['body', 'username'],
            msg: 'String should have at least 3 characters',
            type: 'string_too_short',
          },
        ],
      }),
    )
    expect(result.status).toBe(422)
    expect(result.fieldErrors.username).toBe(
      'Valor inválido según el servidor.',
    )
    expect(result.message).not.toContain('String should')
  })

  it('conserva el detalle de negocio en 409', () => {
    const result = normalizeApiError(
      createAxiosError(409, {
        detail: 'El pedido ya está en un estado final y no puede modificarse.',
      }),
    )
    expect(result.message).toContain('estado final')
  })

  it('devuelve un mensaje genérico para 403', () => {
    const result = normalizeApiError(createAxiosError(403, { detail: 'x' }))
    expect(result.message).toBe(
      'No tienes permisos para realizar esta acción.',
    )
  })

  it('explica que el backend no está disponible en un 502', () => {
    const result = normalizeApiError(createAxiosError(502, {}))
    expect(result.message).toContain('backend esté en ejecución')
  })

  it('detecta errores de red', () => {
    const result = normalizeApiError(
      new AxiosError('Network Error', 'ERR_NETWORK'),
    )
    expect(result.isNetworkError).toBe(true)
    expect(result.message).toContain('No se pudo conectar')
  })

  it('maneja errores no Axios', () => {
    const result = normalizeApiError(new Error('boom'))
    expect(result.status).toBeNull()
    expect(result.message).toContain('error inesperado')
  })
})
