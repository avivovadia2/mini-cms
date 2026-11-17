import { screen } from '@testing-library/react'
import { describe, expect, test } from 'vitest'

import { ME, renderApp } from '../tests/renderApp'

describe('HomePage', () => {
  test('without a session it sends the user to the login screen', async () => {
    renderApp('/', (server) => {
      server.onGet('/auth/me').reply(401, { message: 'Unauthorized' })
    })

    expect(await screen.findByRole('heading', { name: 'Log in' })).toBeInTheDocument()
  })

  test('log out ends the session and goes to the login screen', async () => {
    const { api, user } = renderApp('/', (server) => {
      server.onGet('/auth/me').reply(200, ME)
      server.onPost('/auth/logout').reply(204)
    })

    await user.click(await screen.findByRole('button', { name: 'Log out' }))

    expect(await screen.findByRole('heading', { name: 'Log in' })).toBeInTheDocument()
    expect(api.history.post.map((request) => request.url)).toEqual(['/auth/logout'])
  })
})
