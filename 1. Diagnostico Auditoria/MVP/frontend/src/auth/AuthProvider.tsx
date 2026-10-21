import { useCallback, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { login as loginRequest } from '../api/services/auth.service'
import { UNAUTHORIZED_EVENT } from '../config/env'
import type { LoginInput } from '../types/api'
import { isExpired } from '../utils/format'
import { AuthContext, type AuthContextValue } from './AuthContext'
import { decodeSessionToken, type SessionUser } from './jwt'
import {
  clearStoredToken,
  getStoredToken,
  storeToken,
} from './tokenStorage'

interface InitialAuth {
  session: SessionUser | null
  token: string | null
}

function readInitialAuth(): InitialAuth {
  const storedToken = getStoredToken()
  if (!storedToken) {
    return { session: null, token: null }
  }
  const decoded = decodeSessionToken(storedToken)
  if (!decoded || isExpired(decoded.expiresAt)) {
    clearStoredToken()
    return { session: null, token: null }
  }
  return { session: decoded, token: storedToken }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [initialAuth] = useState(readInitialAuth)
  const [session, setSession] = useState<SessionUser | null>(
    initialAuth.session,
  )
  const [token, setToken] = useState<string | null>(initialAuth.token)

  useEffect(() => {
    const handleUnauthorized = () => {
      clearStoredToken()
      setToken(null)
      setSession(null)
    }
    window.addEventListener(UNAUTHORIZED_EVENT, handleUnauthorized)
    return () =>
      window.removeEventListener(UNAUTHORIZED_EVENT, handleUnauthorized)
  }, [])

  const login = useCallback(async (input: LoginInput) => {
    const response = await loginRequest(input)
    const decoded = decodeSessionToken(response.access_token)
    if (!decoded) {
      throw new Error('La respuesta de autenticación no es válida.')
    }
    if (isExpired(decoded.expiresAt)) {
      throw new Error('El token recibido ya expiró.')
    }
    storeToken(response.access_token)
    setToken(response.access_token)
    setSession(decoded)
  }, [])

  const logout = useCallback(() => {
    clearStoredToken()
    setToken(null)
    setSession(null)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({ session, token, isReady: true, login, logout }),
    [session, token, login, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
