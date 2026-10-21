import { endpoints } from '../../config/endpoints'
import type {
  Order,
  OrderCreateInput,
  OrderStatus,
  PaginationParams,
} from '../../types/api'
import { apiClient } from '../client'

export async function listOrders(
  params: PaginationParams = {},
): Promise<Order[]> {
  const { data } = await apiClient.get<Order[]>(endpoints.orders.list, {
    params,
  })
  return data
}

export async function getOrder(id: number): Promise<Order> {
  const { data } = await apiClient.get<Order>(endpoints.orders.byId(id))
  return data
}

export async function createOrder(input: OrderCreateInput): Promise<Order> {
  const { data } = await apiClient.post<Order>(endpoints.orders.list, input)
  return data
}

export async function updateOrderStatus(
  id: number,
  status: OrderStatus,
): Promise<Order> {
  const { data } = await apiClient.patch<Order>(endpoints.orders.status(id), {
    status,
  })
  return data
}
