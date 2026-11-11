import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect, useRef, useState } from 'react'
import { useForm, useWatch } from 'react-hook-form'
import { getErrorMessage } from '../../api/errors'
import { sendChatMessage } from '../../api/services/ai.service'
import { Alert } from '../../components/feedback/Alert'
import { Button } from '../../components/ui/Button'
import { Badge } from '../../components/ui/Badge'
import { Card } from '../../components/ui/Card'
import { FormField } from '../../components/ui/FormField'
import { textareaClass } from '../../components/ui/formStyles'
import { Icon } from '../../components/ui/Icon'
import { PageHeader } from '../../components/ui/PageHeader'
import {
  aiChatSchema,
  type AIChatFormValues,
} from '../../schemas/ai.schema'
import { cn } from '../../utils/cn'
import { construirHistorial } from '../../utils/chatHistory'
import { formatCurrency, formatQuantity } from '../../utils/format'
import type { AIChatDatos } from '../../types/api'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  transferToEmployee?: boolean
  reason?: string | null
  motor?: string
  datos?: AIChatDatos | null
  esBienvenida?: boolean
}

const suggestions = [
  '¿Hay disponibilidad de glicerina?',
  '¿Cómo puedo registrar un pedido?',
  'Necesito asesoría para una formulación.',
]

function createId(): string {
  return crypto.randomUUID()
}

export function AIChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: createId(),
      role: 'assistant',
      content:
        'Hola. Puedo orientarte sobre disponibilidad, pedidos y el proceso de compra. Recuerdo los últimos mensajes de esta conversación. Si tu consulta requiere apoyo técnico, la transferiré a un asesor.',
      esBienvenida: true,
    },
  ])
  const [isSending, setIsSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    control,
    formState: { errors },
  } = useForm<AIChatFormValues>({
    resolver: zodResolver(aiChatSchema),
    defaultValues: { message: '' },
  })

  const messageValue = useWatch({ control, name: 'message' })

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: 'smooth',
    })
  }, [messages, isSending])

  const onSubmit = handleSubmit(async (values) => {
    const message = values.message.trim()
    const historial = construirHistorial(messages)
    setError(null)
    setMessages((current) => [
      ...current,
      { id: createId(), role: 'user', content: message },
    ])
    reset({ message: '' })
    setIsSending(true)
    try {
      const response = await sendChatMessage({ message, historial })
      setMessages((current) => [
        ...current,
        {
          id: createId(),
          role: 'assistant',
          content: response.response,
          transferToEmployee: response.transfer_to_employee,
          reason: response.reason,
          motor: response.motor,
          datos: response.datos,
        },
      ])
    } catch (requestError) {
      setError(getErrorMessage(requestError))
    } finally {
      setIsSending(false)
    }
  })

  return (
    <div className="space-y-6">
      <PageHeader
        title="Asesoría IA"
        description="Agente conversacional que recuerda los últimos mensajes para orientar consultas sobre disponibilidad, pedidos y formulaciones. Si requiere intervención humana, la consulta se marca para transferencia a un empleado."
      />

      {error ? <Alert tone="error">{error}</Alert> : null}

      <Card className="flex h-[calc(100vh-16rem)] min-h-[28rem] flex-col">
        <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-5">
          {messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                'flex',
                message.role === 'user' ? 'justify-end' : 'justify-start',
              )}
            >
              <div
                className={cn(
                  'max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed',
                  message.role === 'user'
                    ? 'bg-teal-700 text-white'
                    : 'border border-slate-200 bg-slate-50 text-slate-700',
                )}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                {message.transferToEmployee ? (
                  <div className="mt-3 space-y-2 border-t border-slate-200 pt-3">
                    <Badge className="bg-amber-100 text-amber-800 ring-amber-200">
                      Transferencia a empleado
                    </Badge>
                    {message.reason ? (
                      <p className="text-xs text-slate-500">{message.reason}</p>
                    ) : null}
                  </div>
                ) : null}
                {message.role === 'assistant' && (message.motor || message.datos) ? (
                  <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-slate-200 pt-2 text-[11px] text-slate-500">
                    {message.motor ? (
                      <span className="rounded-full bg-slate-200/70 px-2 py-0.5">
                        Motor: {message.motor}
                      </span>
                    ) : null}
                    {message.datos?.tipo === 'cotizacion' &&
                    typeof message.datos.total === 'number' ? (
                      <span>Total calculado: {formatCurrency(message.datos.total)}</span>
                    ) : null}
                    {message.datos?.tipo === 'stock' &&
                    typeof message.datos.stock === 'number' ? (
                      <span>
                        Stock: {formatQuantity(message.datos.stock)}{' '}
                        {String(message.datos.unidad ?? '')}
                      </span>
                    ) : null}
                  </div>
                ) : null}
              </div>
            </div>
          ))}

          {isSending ? (
            <div className="flex justify-start">
              <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-500">
                El agente está respondiendo…
              </div>
            </div>
          ) : null}
        </div>

        <div className="border-t border-slate-200 p-4">
          <div className="mb-3 flex flex-wrap gap-2">
            {suggestions.map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() => setValue('message', suggestion)}
                className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-600 transition hover:border-teal-300 hover:text-teal-800"
              >
                {suggestion}
              </button>
            ))}
          </div>

          <form onSubmit={onSubmit} className="flex items-end gap-2" noValidate>
            <FormField
              label="Tu consulta"
              htmlFor="message"
              error={errors.message?.message}
              className="flex-1"
            >
              <textarea
                id="message"
                rows={2}
                maxLength={1000}
                placeholder="Escribe tu consulta…"
                className={textareaClass}
                aria-invalid={Boolean(errors.message)}
                {...register('message')}
              />
            </FormField>
            <Button
              type="submit"
              isLoading={isSending}
              disabled={(messageValue ?? '').trim().length === 0}
              className="mb-6"
            >
              <Icon name="send" className="h-4 w-4" />
              Enviar
            </Button>
          </form>
          <p className="mt-2 text-xs text-slate-400">
            {(messageValue ?? '').length}/1000 caracteres. Las respuestas son
            orientativas y no reemplazan una asesoría técnica formal.
          </p>
        </div>
      </Card>
    </div>
  )
}
