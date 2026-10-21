import axios from 'axios'
import { clearStoredToken, getStoredToken } from '../auth/tokenStorage'
import { API_BASE_URL, UNAUTHORIZED_EVENT } from '../config/env'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  adapter: 'fetch',
  headers: {
    Accept: 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  const token = getStoredToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      const isLoginRequest = error.config?.url?.endsWith('/auth/token')
      if (!isLoginRequest) {
        clearStoredToken()
        window.dispatchEvent(new Event(UNAUTHORIZED_EVENT))
      }
    }
    return Promise.reject(error)
  },
)
