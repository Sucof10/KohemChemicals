import { endpoints } from '../../config/endpoints'
import type {
  LoginInput,
  RegisterInput,
  TokenResponse,
  UserResponse,
} from '../../types/api'
import { apiClient } from '../client'

export async function login(input: LoginInput): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>(endpoints.auth.login, input)
  return data
}

export async function register(input: RegisterInput): Promise<UserResponse> {
  const { data } = await apiClient.post<UserResponse>(
    endpoints.auth.register,
    input,
  )
  return data
}
