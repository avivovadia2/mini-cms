import type { ReactNode } from 'react'
import { Redirect, useLocation } from 'react-router-dom'

import { useAuth } from './authContext'

// Wraps every route that needs a session. Without one, go to Login and remember where the user
// was going (`state.from`), so Login can send them back there.
export function RequireAuth({ children }: { children: ReactNode }) {
  const { state } = useAuth()
  const location = useLocation()

  if (state.kind === 'loading') return <p className="p-6">Loading…</p>
  if (state.kind === 'loggedOut') {
    return <Redirect to={{ pathname: '/login', state: { from: location } }} />
  }
  return <>{children}</>
}
