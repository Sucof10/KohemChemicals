import { endpoints } from '../../config/endpoints'
import type { AuditLog } from '../../types/api'
import { apiClient } from '../client'

export async function listAuditLogs(limit = 100): Promise<AuditLog[]> {
  const { data } = await apiClient.get<AuditLog[]>(endpoints.audit.list, {
    params: { limit },
  })
  return data
}
