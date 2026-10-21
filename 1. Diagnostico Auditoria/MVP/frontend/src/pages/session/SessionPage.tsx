import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../auth/useAuth'
import { Alert } from '../../components/feedback/Alert'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Card, CardHeader } from '../../components/ui/Card'
import { PageHeader } from '../../components/ui/PageHeader'
import { ROLE_LABELS } from '../../utils/labels'

export function SessionPage() {
  const { session, logout } = useAuth()
  const navigate = useNavigate()

  if (!session) return null

  const expiresAt = new Intl.DateTimeFormat('es-CO', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(session.expiresAt * 1000))

  return (
    <div className="space-y-6">
      <PageHeader
        title="Mi sesión"
        description="Datos obtenidos del token emitido por el backend. Esta vista es informativa: la API no expone un endpoint de perfil editable."
      />

      <Card className="max-w-2xl">
        <CardHeader
          title="Información de la cuenta"
          description="El rol mostrado solo controla la interfaz; el backend valida los permisos en cada solicitud."
          action={
            <Badge className="bg-teal-50 text-teal-700 ring-teal-200">
              {ROLE_LABELS[session.role]}
            </Badge>
          }
        />
        <dl className="divide-y divide-slate-100">
          <div className="flex items-center justify-between gap-4 px-5 py-4 text-sm">
            <dt className="text-slate-500">Usuario</dt>
            <dd className="font-medium text-slate-900">{session.username}</dd>
          </div>
          <div className="flex items-center justify-between gap-4 px-5 py-4 text-sm">
            <dt className="text-slate-500">Rol</dt>
            <dd className="text-slate-700">{session.role}</dd>
          </div>
          <div className="flex items-center justify-between gap-4 px-5 py-4 text-sm">
            <dt className="text-slate-500">ID de usuario</dt>
            <dd className="text-slate-700">{session.userId}</dd>
          </div>
          <div className="flex items-center justify-between gap-4 px-5 py-4 text-sm">
            <dt className="text-slate-500">Expiración del token</dt>
            <dd className="text-slate-700">{expiresAt}</dd>
          </div>
        </dl>
        <div className="border-t border-slate-200 p-5">
          <Button
            variant="secondary"
            onClick={() => {
              logout()
              navigate('/login', { replace: true })
            }}
          >
            Cerrar sesión
          </Button>
        </div>
      </Card>

      <div className="max-w-2xl">
        <Alert tone="info">
          El token se guarda en sessionStorage para esta pestaña. El backend no
          ofrece refresh token ni cookies HttpOnly, por lo que la sesión expira
          a los 60 minutos y debe iniciarse de nuevo.
        </Alert>
      </div>
    </div>
  )
}
