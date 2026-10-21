import { endpoints } from '../../config/endpoints'
import type {
  PaginationParams,
  RawMaterial,
  RawMaterialCreateInput,
  RawMaterialUpdateInput,
} from '../../types/api'
import { apiClient } from '../client'

export async function listMaterials(
  params: PaginationParams = {},
): Promise<RawMaterial[]> {
  const { data } = await apiClient.get<RawMaterial[]>(endpoints.materials.list, {
    params,
  })
  return data
}

export async function getMaterial(id: number): Promise<RawMaterial> {
  const { data } = await apiClient.get<RawMaterial>(
    endpoints.materials.byId(id),
  )
  return data
}

export async function createMaterial(
  input: RawMaterialCreateInput,
): Promise<RawMaterial> {
  const { data } = await apiClient.post<RawMaterial>(
    endpoints.materials.list,
    input,
  )
  return data
}

export async function updateMaterial(
  id: number,
  input: RawMaterialUpdateInput,
): Promise<RawMaterial> {
  const { data } = await apiClient.put<RawMaterial>(
    endpoints.materials.byId(id),
    input,
  )
  return data
}

export async function deleteMaterial(id: number): Promise<void> {
  await apiClient.delete(endpoints.materials.byId(id))
}
