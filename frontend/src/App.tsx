import { useEffect, useState } from 'react'
import { fetchHealth, HealthResponse } from './api/health'

type HealthState =
  | { kind: 'loading' }
  | { kind: 'ok'; health: HealthResponse }
  | { kind: 'error'; message: string }

function App() {
  const [state, setState] = useState<HealthState>({ kind: 'loading' })

  useEffect(() => {
    fetchHealth()
      .then((health) => setState({ kind: 'ok', health }))
      .catch((error: Error) => setState({ kind: 'error', message: error.message }))
  }, [])

  return (
    <main style={{ fontFamily: 'sans-serif', padding: 24 }}>
      <h1>Mini CMS</h1>
      {state.kind === 'loading' && <p>Checking backend…</p>}
      {state.kind === 'ok' && (
        <p data-testid="health-status">
          Backend: <strong>{state.health.status}</strong> · Database:{' '}
          <strong>{state.health.database}</strong>
        </p>
      )}
      {state.kind === 'error' && <p role="alert">Backend unreachable: {state.message}</p>}
    </main>
  )
}

export default App
