const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim()

export const API_BASE_URL = (configuredBaseUrl || '/api/v1').replace(/\/+$/, '')

export const APP_NAME = 'Kohem Chemicals'

export const SESSION_STORAGE_KEY = 'kohem.session.token'

export const UNAUTHORIZED_EVENT = 'kohem:unauthorized'
