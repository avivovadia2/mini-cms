import { render } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import MockAdapter from 'axios-mock-adapter'
import { MemoryRouter } from 'react-router-dom'

import App from '../App'
import { apiClient } from '../api/client'

// Render the whole app at `url`, with the network replaced by a mock (the only thing tests mock).
// MemoryRouter keeps the URL in memory instead of the browser's address bar.
//
// `mockApi` sets up the server's answers *before* rendering: some pages call the API as soon as
// they mount. A request with no matching answer fails the test instead of silently getting a 404.
export function renderApp(url: string, mockApi: (server: MockAdapter) => void = () => {}) {
  const api = new MockAdapter(apiClient)
  mockApi(api)
  api.onAny().reply((config) => {
    throw new Error(`Unexpected request: ${config.method?.toUpperCase()} ${config.url}`)
  })
  const user = userEvent.setup()
  render(
    <MemoryRouter initialEntries={[url]}>
      <App />
    </MemoryRouter>,
  )
  return { api, user }
}

export const ME = {
  id: 1,
  email: 'dana@acme.com',
  full_name: 'Dana Levi',
  organization: { id: 1, name: 'Acme Insurance' },
}
