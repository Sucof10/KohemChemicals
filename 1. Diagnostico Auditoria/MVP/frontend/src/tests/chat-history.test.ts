import { describe, expect, it } from 'vitest'
import { construirHistorial, MAX_HISTORIAL } from '../utils/chatHistory'

describe('construirHistorial', () => {
  it('descarta la bienvenida y conserva solo los últimos turnos', () => {
    const mensajes = [
      { role: 'assistant' as const, content: 'Hola', esBienvenida: true },
      ...Array.from({ length: 10 }, (_, indice) => ({
        role: (indice % 2 === 0 ? 'user' : 'assistant') as 'user' | 'assistant',
        content: `mensaje ${indice}`,
      })),
    ]

    const historial = construirHistorial(mensajes)

    expect(historial).toHaveLength(MAX_HISTORIAL)
    expect(historial.at(-1)?.content).toBe('mensaje 9')
    expect(historial.some((mensaje) => mensaje.content === 'Hola')).toBe(false)
  })

  it('ignora mensajes vacíos y recorta espacios', () => {
    const historial = construirHistorial([
      { role: 'user', content: '  hola  ' },
      { role: 'assistant', content: '   ' },
    ])

    expect(historial).toEqual([{ role: 'user', content: 'hola' }])
  })

  it('respeta un máximo personalizado', () => {
    const mensajes = Array.from({ length: 5 }, (_, indice) => ({
      role: 'user' as const,
      content: `m${indice}`,
    }))

    expect(construirHistorial(mensajes, 2)).toHaveLength(2)
  })
})
