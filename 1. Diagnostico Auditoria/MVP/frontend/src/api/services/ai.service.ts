import { endpoints } from '../../config/endpoints'
import type { AIChatInput, AIChatResponse } from '../../types/api'
import { apiClient } from '../client'

export async function sendChatMessage(
  input: AIChatInput,
): Promise<AIChatResponse> {
  const { data } = await apiClient.post<AIChatResponse>(
    endpoints.ai.chat,
    input,
  )
  return data
}
