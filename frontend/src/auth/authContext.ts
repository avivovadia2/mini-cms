import { createContext, useContext } from 'react'

import type { MeResponse } from '../api/auth'

// Who is logged in, shared with every component through React context: AuthProvider (at the top
// of the app) loads it once, and any component below reads it with useAuth().
export type AuthState =
  | { kind: 'loading' } // asking the backend (/auth/me) whether the browser has a session
  | { kind: 'loggedIn'; me: MeResponse }
  | { kind: 'loggedOut' }

export interface AuthContextValue {
  state: AuthState
  setMe: (me: MeResponse) => void // after login or register: their response is the new user
  logOut: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext)
  if (value === null) throw new Error('useAuth must be used inside <AuthProvider>')
  return value
}

// For screens that only render behind <RequireAuth>, where a user is guaranteed.
export function useMe(): MeResponse {
  const { state } = useAuth()
  if (state.kind !== 'loggedIn') throw new Error('useMe must be used behind <RequireAuth>')
  return state.me
}
