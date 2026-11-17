import { render } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import MockAdapter from 'axios-mock-adapter'
import { MemoryRouter } from 'react-router-dom'

import App from '../App'
import type { MeResponse } from '../api/auth'
import { apiClient } from '../api/client'
import type { Page, UserInfo } from '../api/users'

interface RenderAppOptions {
  // The session the app finds when it starts (its first call is GET /auth/me). null: logged out.
  me?: MeResponse | null
  // The server's other answers. Set up *before* rendering, because pages call the API on mount.
  mockApi?: (server: MockAdapter) => void
}

// Render the whole app at `url`, with the network replaced by a mock (the only thing tests mock).
// MemoryRouter keeps the URL in memory instead of the browser's address bar.
// A request with no prepared answer fails the test instead of silently getting a 404.
export function renderApp(url: string, { me = null, mockApi = () => {} }: RenderAppOptions = {}) {
  const api = new MockAdapter(apiClient)
  if (me) {
    api.onGet('/auth/me').reply(200, me)
  } else {
    api.onGet('/auth/me').reply(401, { message: 'Unauthorized' })
  }
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

export const ME: MeResponse = {
  id: 1,
  email: 'dana@acme.com',
  full_name: 'Dana Levi',
  organization: { id: 1, name: 'Acme Insurance' },
}

export function userInfo(id: number, overrides: Partial<UserInfo> = {}): UserInfo {
  return {
    id,
    organization_id: ME.organization.id,
    email: `user${id}@acme.com`,
    full_name: `User ${id}`,
    is_active: true,
    ...overrides,
  }
}

export function usersPage(users: UserInfo[], totalCount = users.length): Page<UserInfo> {
  return { results: users, total_count: totalCount }
}
