import { render } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import MockAdapter from 'axios-mock-adapter'
import { MemoryRouter } from 'react-router-dom'

import App from '../App'
import type { MeResponse } from '../api/auth'
import { apiClient } from '../api/client'
import type { FnolInfo } from '../api/fnol'
import type { Page } from '../api/page'
import type { PolicyInfo } from '../api/policies'
import type { UserInfo } from '../api/users'

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

export function policyInfo(id: number, overrides: Partial<PolicyInfo> = {}): PolicyInfo {
  return {
    id,
    organization_id: ME.organization.id,
    policy_number: `POL-${id}`,
    insured_name: `Insured ${id}`,
    line_of_business: 'auto',
    effective_date: '2026-01-01',
    expiration_date: '2027-01-01',
    status: 'active',
    ...overrides,
  }
}

// An FNOL as the API returns it; unmatched unless a `policy` is given in the overrides.
export function fnolInfo(id: number, overrides: Partial<FnolInfo> = {}): FnolInfo {
  const policy = overrides.policy ?? null
  return {
    id,
    organization_id: ME.organization.id,
    reported_policy_number: `POL-${id}`,
    policy_id: policy?.id ?? null,
    reporter_name: `Reporter ${id}`,
    reporter_email: null,
    reporter_phone: null,
    loss_date: '2026-03-10',
    loss_description: 'Rear-ended at a traffic light.',
    loss_state: null,
    status: 'submitted',
    rejection_reason: null,
    submitted_by_id: ME.id,
    created_at: '2026-03-11T09:00:00+00:00',
    ...overrides,
    policy,
  }
}

// Any list endpoint's answer: these items, and (by default) no more pages.
export function pageOf<T>(items: T[], totalCount = items.length): Page<T> {
  return { results: items, total_count: totalCount }
}
