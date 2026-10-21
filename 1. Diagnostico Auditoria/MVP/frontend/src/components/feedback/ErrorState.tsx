import { Button } from '../ui/Button'
import { Alert } from './Alert'

export function ErrorState({
  message,
  onRetry,
}: {
  message: string
  onRetry?: () => void
}) {
  return (
    <div className="space-y-4">
      <Alert tone="error">{message}</Alert>
      {onRetry ? (
        <Button variant="secondary" onClick={onRetry}>
          Reintentar
        </Button>
      ) : null}
    </div>
  )
}
