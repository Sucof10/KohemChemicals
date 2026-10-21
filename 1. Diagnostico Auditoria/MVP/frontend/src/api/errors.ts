import axios from 'axios'
import type { ApiErrorBody, ValidationErrorItem } from '../types/api'

export interface NormalizedApiError {
  status: number | null
  message: string
  fieldErrors: Record<string, string>
  isNetworkError: boolean
}

const fallbackByStatus: Record<number, string> = {
  401: 'Tu sesión expiró. Inicia sesión nuevamente.',
  403: 'No tienes permisos para realizar esta acción.',
  404: 'El recurso solicitado no existe.',
  409: 'La operación entra en conflicto con el estado actual.',
  422: 'Revisa los campos marcados e inténtalo de nuevo.',
  429: 'Demasiados intentos. Espera un momento antes de continuar.',
  500: 'Ocurrió un error interno. Inténtalo más tarde.',
  502: 'El servicio no está disponible. Verifica que el backend esté en ejecución e inténtalo de nuevo.',
  503: 'El servicio no está disponible en este momento. Inténtalo más tarde.',
  504: 'El servidor tardó demasiado en responder. Inténtalo de nuevo.',
}

function isValidationError(value: unknown): value is ValidationErrorItem[] {
  return (
    Array.isArray(value) &&
    value.every(
      (item) =>
        typeof item === 'object' &&
        item !== null &&
        'loc' in item &&
        'msg' in item,
    )
  )
}

function fieldFromLocation(item: ValidationErrorItem): string | null {
  const field = [...item.loc].reverse().find((part) => typeof part === 'string')
  return field ?? null
}

export function normalizeApiError(error: unknown): NormalizedApiError {
  if (!axios.isAxiosError(error)) {
    return {
      status: null,
      message: 'Ocurrió un error inesperado. Inténtalo de nuevo.',
      fieldErrors: {},
      isNetworkError: false,
    }
  }

  if (!error.response) {
    return {
      status: null,
      message:
        'No se pudo conectar con el servidor. Verifica tu conexión e inténtalo de nuevo.',
      fieldErrors: {},
      isNetworkError: true,
    }
  }

  const status = error.response.status
  const body = error.response.data as ApiErrorBody | undefined
  const detail = body?.detail

  if (status === 422 && isValidationError(detail)) {
    const fieldErrors: Record<string, string> = {}
    for (const item of detail) {
      const field = fieldFromLocation(item)
      if (field && !fieldErrors[field]) {
        fieldErrors[field] = 'Valor inválido según el servidor.'
      }
    }
    return {
      status,
      message: fallbackByStatus[422],
      fieldErrors,
      isNetworkError: false,
    }
  }

  const backendDetail = typeof detail === 'string' ? detail.trim() : ''
  const domainMessage =
    (status === 400 || status === 409) && backendDetail ? backendDetail : ''

  return {
    status,
    message:
      domainMessage ||
      fallbackByStatus[status] ||
      'No se pudo completar la operación. Inténtalo de nuevo.',
    fieldErrors: {},
    isNetworkError: false,
  }
}

export function getErrorMessage(error: unknown): string {
  return normalizeApiError(error).message
}
