import type { OrderStatus } from '../../types/api'
import { ORDER_STATUS_LABELS, ORDER_STATUS_STYLES } from '../../utils/labels'
import { Badge } from './Badge'

export function StatusBadge({ status }: { status: OrderStatus }) {
  return (
    <Badge className={ORDER_STATUS_STYLES[status]}>
      {ORDER_STATUS_LABELS[status]}
    </Badge>
  )
}
