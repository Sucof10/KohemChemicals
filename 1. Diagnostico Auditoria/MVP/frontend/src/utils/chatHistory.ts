import type { ChatHistoryMessage } from '../types/api'

/** Límite alineado con AI_HISTORY_MAX del backend. */
export const MAX_HISTORIAL = 8

interface MensajeConversacion {
  role: 'user' | 'assistant'
  content: string
  esBienvenida?: boolean
}

/**
 * Construye el historial que se envía al backend: descarta el saludo inicial,
 * ignora mensajes vacíos y conserva solo los últimos `maximo` turnos.
 */
export function construirHistorial(
  mensajes: MensajeConversacion[],
  maximo: number = MAX_HISTORIAL,
): ChatHistoryMessage[] {
  return mensajes
    .filter((mensaje) => !mensaje.esBienvenida && mensaje.content.trim().length > 0)
    .slice(-maximo)
    .map((mensaje) => ({
      role: mensaje.role,
      content: mensaje.content.trim(),
    }))
}
