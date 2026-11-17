import { Redirect, Route, Switch } from 'react-router-dom'

import { AuthProvider } from './auth/AuthProvider'
import { RequireAuth } from './auth/RequireAuth'
import { AppShell } from './components/AppShell'
import { LoginPage } from './pages/LoginPage'
import { PlaceholderPage } from './pages/PlaceholderPage'
import { RegisterPage } from './pages/RegisterPage'
import { UsersPage } from './pages/users/UsersPage'

// The router itself (BrowserRouter) is in main.tsx, so tests can render <App /> inside a
// MemoryRouter instead and choose the starting URL.
function App() {
  return (
    <AuthProvider>
      <Switch>
        {/* The only two routes without a session. */}
        <Route path="/login">
          <LoginPage />
        </Route>
        <Route path="/register">
          <RegisterPage />
        </Route>
        {/* Everything else: needs a session, inside the app shell. */}
        <Route>
          <RequireAuth>
            <AppShell>
              <Switch>
                <Route path="/fnol">
                  <PlaceholderPage title="FNOL" milestone="M2" />
                </Route>
                <Route path="/claims">
                  <PlaceholderPage title="Claims" milestone="M3" />
                </Route>
                <Route path="/policies">
                  <PlaceholderPage title="Policies" milestone="M2" />
                </Route>
                <Route path="/users">
                  <UsersPage />
                </Route>
                <Redirect to="/users" />
              </Switch>
            </AppShell>
          </RequireAuth>
        </Route>
      </Switch>
    </AuthProvider>
  )
}

export default App
