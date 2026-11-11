export const USER_ROLES = ['admin', 'analista', 'cliente'] as const
export type UserRole = (typeof USER_ROLES)[number]

export const ORDER_STATUSES = [
  'pendiente',
  'confirmado',
  'preparando',
  'enviado',
  'entregado',
  'cancelado',
] as const
export type OrderStatus = (typeof ORDER_STATUSES)[number]

export const FINAL_ORDER_STATUSES: readonly OrderStatus[] = ['entregado', 'cancelado']

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface UserResponse {
  id: number
  username: string
  email: string
  role: UserRole
  is_active: boolean
}

export interface LoginInput {
  username: string
  password: string
}

export interface RegisterInput {
  username: string
  email: string
  password: string
}

export interface RawMaterial {
  id: number
  name: string
  category: string
  unit: string
  price: number
  stock: number
  description: string | null
  is_active: boolean
}

export interface RawMaterialCreateInput {
  name: string
  category: string
  unit: string
  price: number
  stock: number
  description?: string
}

export type RawMaterialUpdateInput = Partial<RawMaterialCreateInput>

export interface OrderItemCreateInput {
  raw_material_id: number
  quantity: number
}

export interface OrderCreateInput {
  items: OrderItemCreateInput[]
  notes?: string
}

export interface OrderItem {
  id: number
  raw_material_id: number
  quantity: number
  unit_price: number
  subtotal: number
}

export interface Order {
  id: number
  customer_id: number
  status: OrderStatus
  total: number
  notes: string | null
  items: OrderItem[]
  created_at: string
  updated_at: string
}

export interface OrderStatusUpdateInput {
  status: OrderStatus
}

export interface ChatHistoryMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface AIChatInput {
  message: string
  historial?: ChatHistoryMessage[]
}

export interface AIChatDatos {
  tipo?: string
  subtotal?: number
  iva?: number
  total?: number
  material?: string
  stock?: number
  unidad?: string
  tope_aplicado?: boolean
  requiere_revision?: boolean
  [clave: string]: unknown
}

export interface AIChatResponse {
  response: string
  transfer_to_employee: boolean
  reason: string | null
  motor?: string
  datos?: AIChatDatos | null
}

export interface AuditLog {
  id: number
  user_id: number | null
  action: string
  entity: string
  entity_id: number | null
  detail: string
  created_at: string
}

export interface JwtPayload {
  sub: string
  role: UserRole
  user_id: number
  exp: number
}

export interface ValidationErrorItem {
  loc: Array<string | number>
  msg: string
  type: string
}

export interface ApiErrorBody {
  detail?: string | ValidationErrorItem[]
}

export interface PaginationParams {
  skip?: number
  limit?: number
}
