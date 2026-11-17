import { useEffect, useState } from 'react'
import { Redirect, useHistory } from 'react-router-dom'

import { getMe, logout, type MeResponse } from '../api/auth'
import { Button } from '../components/Button'

// Temporary landing page so register and login have somewhere to go. M1 4/4 replaces it with the
// app shell and protected routes.
type MeState = { kind: 'loading' } | { kind: 'loggedIn'; me: MeResponse } | { kind: 'loggedOut' }

export function HomePage() {
  const history = useHistory()
  const [state, setState] = useState<MeState>({ kind: 'loading' })

  useEffect(() => {
    getMe()
      .then((me) => setState({ kind: 'loggedIn', me }))
      .catch(() => setState({ kind: 'loggedOut' })) // 401: no session
  }, [])

  async function handleLogout() {
    await logout()
    history.push('/login')
  }

  if (state.kind === 'loading') return <p className="p-6">Loading…</p>
  if (state.kind === 'loggedOut') return <Redirect to="/login" />

  return (
    <main className="flex flex-col items-start gap-4 p-6">
      <h1 className="text-2xl font-semibold">{state.me.organization.name}</h1>
      <p>
        Logged in as <strong>{state.me.full_name}</strong> ({state.me.email})
      </p>
      <Button onClick={handleLogout}>Log out</Button>
    </main>
  )
}
