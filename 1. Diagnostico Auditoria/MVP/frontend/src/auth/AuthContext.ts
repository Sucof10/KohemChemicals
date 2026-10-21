import { createContext } from 'react'
import type { LoginInput } from '../types/api'
import type { SessionUser } from './jwt'

export interface AuthContextValue {
  session: SessionUser | null
  token: string | null
  isReady: boolean
  login: (input: LoginInput) => Promise<void>
  logout: () => void
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined)
