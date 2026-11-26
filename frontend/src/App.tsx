import { Redirect, Route, Switch } from 'react-router-dom'

import { AuthProvider } from './auth/AuthProvider'
import { RequireAuth } from './auth/RequireAuth'
import { AppShell } from './components/AppShell'
import { FnolDetailPage } from './pages/fnol/FnolDetailPage'
import { FnolListPage } from './pages/fnol/FnolListPage'
import { ReportLossPage } from './pages/fnol/ReportLossPage'
import { LoginPage } from './pages/LoginPage'
import { PlaceholderPage } from './pages/PlaceholderPage'
import { PoliciesPage } from './pages/policies/PoliciesPage'
import { PolicyDetailPage } from './pages/policies/PolicyDetailPage'
import { PolicyFormPage } from './pages/policies/PolicyFormPage'
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
                <Route exact path="/fnol">
                  <FnolListPage />
                </Route>
                <Route path="/fnol/new">
                  <ReportLossPage />
                </Route>
                <Route path="/fnol/:fnolId(\d+)">
                  <FnolDetailPage />
                </Route>
                <Route path="/claims">
                  <PlaceholderPage title="Claims" milestone="M3" />
                </Route>
                {/* First match wins: "new" before ":policyId", and only numeric ids. */}
                <Route exact path="/policies">
                  <PoliciesPage />
                </Route>
                <Route path="/policies/new">
                  <PolicyFormPage />
                </Route>
                <Route path="/policies/:policyId(\d+)/edit">
                  <PolicyFormPage />
                </Route>
                <Route path="/policies/:policyId(\d+)">
                  <PolicyDetailPage />
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
