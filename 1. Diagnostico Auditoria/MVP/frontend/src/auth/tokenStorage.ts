import { SESSION_STORAGE_KEY } from '../config/env'

export function getStoredToken(): string | null {
  try {
    return sessionStorage.getItem(SESSION_STORAGE_KEY)
  } catch {
    return null
  }
}

export function storeToken(token: string): void {
  try {
    sessionStorage.setItem(SESSION_STORAGE_KEY, token)
  } catch {
    // Si el navegador bloquea sessionStorage, la sesión vive solo en memoria.
  }
}

export function clearStoredToken(): void {
  try {
    sessionStorage.removeItem(SESSION_STORAGE_KEY)
  } catch {
    // No hay nada que limpiar si el almacenamiento no está disponible.
  }
}
