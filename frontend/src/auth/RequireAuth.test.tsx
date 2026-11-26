import { screen } from '@testing-library/react'
import { describe, expect, test } from 'vitest'

import { ME, renderApp, userInfo, pageOf } from '../tests/renderApp'

describe('protected routes', () => {
  test.each(['/users', '/claims', '/policies', '/fnol', '/'])(
    'visiting %s without a session redirects to Login',
    async (url) => {
      renderApp(url)

      expect(await screen.findByRole('heading', { name: 'Log in' })).toBeInTheDocument()
      expect(screen.queryByRole('navigation', { name: 'Main' })).not.toBeInTheDocument()
    },
  )

  test('with a session the page itself is shown', async () => {
    renderApp('/users', {
      me: ME,
      mockApi: (server) => {
        server.onGet('/users').reply(200, pageOf([userInfo(1)]))
      },
    })

    expect(await screen.findByRole('heading', { name: 'Users' })).toBeInTheDocument()
  })
})
