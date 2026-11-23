import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'

import { getMe, logout, type MeResponse } from '../api/auth'
import { apiClient } from '../api/client'
import { AuthContext, type AuthState } from './authContext'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({ kind: 'loading' })

  // Once, when the app starts: is there already a session cookie? (e.g. after a page refresh)
  useEffect(() => {
    getMe()
      .then((me) => setState({ kind: 'loggedIn', me }))
      .catch(() => setState({ kind: 'loggedOut' }))
  }, [])

  // If the session ends while the app is open (expired, user deactivated), the next API call
  // gets a 401: switch to logged out, and <RequireAuth> sends the user to Login.
  useEffect(() => {
    const interceptor = apiClient.interceptors.response.use(undefined, (error) => {
      if (error.response?.status === 401) setState({ kind: 'loggedOut' })
      return Promise.reject(error)
    })
    return () => apiClient.interceptors.response.eject(interceptor)
  }, [])

  const setMe = useCallback((me: MeResponse) => setState({ kind: 'loggedIn', me }), [])
  const logOut = useCallback(async () => {
    await logout()
    setState({ kind: 'loggedOut' })
  }, [])

  // useMemo: a new object only when `state` changes, so consumers don't re-render needlessly.
  const value = useMemo(() => ({ state, setMe, logOut }), [state, setMe, logOut])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
