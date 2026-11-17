import { screen } from '@testing-library/react'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, test } from 'vitest'

import { ME, renderApp } from '../tests/renderApp'

async function logIn(user: UserEvent, email: string, password: string) {
  await user.type(screen.getByLabelText('Email'), email)
  await user.type(screen.getByLabelText('Password'), password)
  await user.click(screen.getByRole('button', { name: 'Log in' }))
}

describe('LoginPage', () => {
  test('bad credentials show the error message and stay on the login screen', async () => {
    const { user } = renderApp('/login', (server) => {
      server.onPost('/auth/login').reply(401, { message: 'Invalid email or password' })
    })

    await logIn(user, 'dana@acme.com', 'wrong-password')

    expect(await screen.findByRole('alert')).toHaveTextContent('Invalid email or password')
    expect(screen.getByRole('heading', { name: 'Log in' })).toBeInTheDocument()
  })

  test('valid credentials are sent and land in the app', async () => {
    const { api, user } = renderApp('/login', (server) => {
      server.onPost('/auth/login').reply(200, ME)
      server.onGet('/auth/me').reply(200, ME)
    })

    await logIn(user, 'dana@acme.com', 'correct-horse')

    expect(await screen.findByText('Acme Insurance')).toBeInTheDocument()
    expect(JSON.parse(api.history.post[0].data)).toEqual({
      email: 'dana@acme.com',
      password: 'correct-horse',
    })
  })

  test('an invalid email is caught before anything is sent', async () => {
    const { api, user } = renderApp('/login')

    await logIn(user, 'not-an-email', 'whatever')

    expect(await screen.findByLabelText('Email')).toHaveAccessibleDescription('Enter a valid email')
    expect(api.history.post).toHaveLength(0)
  })

  test('the register link goes to the register screen', async () => {
    const { user } = renderApp('/login')

    await user.click(screen.getByRole('link', { name: 'Register a new organization' }))

    expect(
      screen.getByRole('heading', { name: 'Register a new organization' }),
    ).toBeInTheDocument()
  })
})
