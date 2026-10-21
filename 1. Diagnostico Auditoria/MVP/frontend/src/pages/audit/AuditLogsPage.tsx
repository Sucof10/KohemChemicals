import { listAuditLogs } from '../../api/services/audit.service'
import { EmptyState } from '../../components/feedback/EmptyState'
import { ErrorState } from '../../components/feedback/ErrorState'
import { LoadingScreen } from '../../components/feedback/LoadingScreen'
import { Card } from '../../components/ui/Card'
import { PageHeader } from '../../components/ui/PageHeader'
import { useApiData } from '../../hooks/useApiData'
import { formatDateTime } from '../../utils/format'

export function AuditLogsPage() {
  const { data, isLoading, error, reload } = useApiData(
    () => listAuditLogs(100),
    [],
  )

  if (isLoading) {
    return <LoadingScreen message="Cargando logs de auditoría…" />
  }

  if (error) {
    return <ErrorState message={error} onRetry={reload} />
  }

  const logs = data ?? []

  return (
    <div className="space-y-6">
      <PageHeader
        title="Logs de auditoría"
        description="Registro de solo lectura de las operaciones sobre pedidos. La API devuelve hasta 100 registros y no expone filtros ni total paginado."
      />

      <Card>
        {logs.length === 0 ? (
          <div className="p-5">
            <EmptyState
              title="Sin eventos registrados"
              description="Los cambios de pedidos aparecerán aquí cuando se realicen operaciones."
            />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-5 py-3 font-medium">ID</th>
                  <th className="px-5 py-3 font-medium">Fecha</th>
                  <th className="px-5 py-3 font-medium">Usuario</th>
                  <th className="px-5 py-3 font-medium">Acción</th>
                  <th className="px-5 py-3 font-medium">Entidad</th>
                  <th className="px-5 py-3 font-medium">Detalle</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {logs.map((log) => (
                  <tr key={log.id}>
                    <td className="px-5 py-4 text-slate-500">{log.id}</td>
                    <td className="px-5 py-4 whitespace-nowrap text-slate-600">
                      {formatDateTime(log.created_at)}
                    </td>
                    <td className="px-5 py-4 text-slate-600">
                      {log.user_id ?? 'Sistema'}
                    </td>
                    <td className="px-5 py-4">
                      <span className="rounded-md bg-slate-100 px-2 py-1 font-mono text-xs text-slate-700">
                        {log.action}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-slate-600">
                      {log.entity}
                      {log.entity_id !== null ? ` #${log.entity_id}` : ''}
                    </td>
                    <td className="max-w-md px-5 py-4 text-slate-600">
                      {log.detail}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  )
}
