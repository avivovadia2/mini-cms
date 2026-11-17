import { screen, within } from '@testing-library/react'
import { describe, expect, test } from 'vitest'

import { ME, renderApp } from '../tests/renderApp'

describe('AppShell', () => {
  test('the top bar shows the organization and user names', async () => {
    renderApp('/claims', { me: ME })

    const header = await screen.findByRole('banner')
    expect(within(header).getByText('Acme Insurance')).toBeInTheDocument()
    expect(within(header).getByText('Dana Levi')).toBeInTheDocument()
  })

  test('Log out ends the session and returns to Login', async () => {
    const { api, user } = renderApp('/claims', {
      me: ME,
      mockApi: (server) => {
        server.onPost('/auth/logout').reply(204)
      },
    })

    await user.click(await screen.findByRole('button', { name: 'Log out' }))

    expect(await screen.findByRole('heading', { name: 'Log in' })).toBeInTheDocument()
    expect(api.history.post.map((request) => request.url)).toEqual(['/auth/logout'])
  })

  test('the navigation opens each screen', async () => {
    const { user } = renderApp('/claims', { me: ME })
    const nav = await screen.findByRole('navigation', { name: 'Main' })

    await user.click(within(nav).getByRole('link', { name: 'Policies' }))
    expect(screen.getByRole('heading', { name: 'Policies' })).toBeInTheDocument()

    await user.click(within(nav).getByRole('link', { name: 'FNOL' }))
    expect(screen.getByRole('heading', { name: 'FNOL' })).toBeInTheDocument()
  })

  test('a session that ends while the app is open sends the user to Login', async () => {
    // The app starts logged in, then the session expires: the users list gets a 401.
    renderApp('/users', {
      me: ME,
      mockApi: (server) => {
        server.onGet('/users').reply(401, { message: 'Unauthorized' })
      },
    })

    expect(await screen.findByRole('heading', { name: 'Log in' })).toBeInTheDocument()
  })
})
