import { Redirect, Route, Switch } from 'react-router-dom'

import { HomePage } from './pages/HomePage'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'

// The router itself (BrowserRouter) is in main.tsx, so tests can render <App /> inside a
// MemoryRouter instead and choose the starting URL.
function App() {
  return (
    <Switch>
      <Route path="/login">
        <LoginPage />
      </Route>
      <Route path="/register">
        <RegisterPage />
      </Route>
      <Route exact path="/">
        <HomePage />
      </Route>
      <Redirect to="/" />
    </Switch>
  )
}

export default App
