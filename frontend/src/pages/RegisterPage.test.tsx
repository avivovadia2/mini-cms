import { screen } from '@testing-library/react'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, test } from 'vitest'

import { ME, renderApp } from '../tests/renderApp'

const VALID = {
  organization_name: 'Acme Insurance',
  full_name: 'Dana Levi',
  email: 'dana@acme.com',
  password: 'correct-horse',
  confirm_password: 'correct-horse',
}

async function fillForm(user: UserEvent, values: Partial<typeof VALID> = {}) {
  const v = { ...VALID, ...values }
  await user.type(screen.getByLabelText('Organization name'), v.organization_name)
  await user.type(screen.getByLabelText('Full name'), v.full_name)
  await user.type(screen.getByLabelText('Email'), v.email)
  await user.type(screen.getByLabelText('Password'), v.password)
  await user.type(screen.getByLabelText('Confirm password'), v.confirm_password)
}

const submit = (user: UserEvent) => user.click(screen.getByRole('button', { name: 'Register' }))

describe('RegisterPage', () => {
  test('a valid submit sends the right payload and lands in the app logged in', async () => {
    // Arrange
    const { api, user } = renderApp('/register', (server) => {
      server.onPost('/auth/register').reply(201, ME)
      server.onGet('/auth/me').reply(200, ME)
    })

    // Act
    await fillForm(user)
    await submit(user)

    // Assert
    expect(await screen.findByText('Acme Insurance')).toBeInTheDocument()
    expect(screen.getByText('Dana Levi')).toBeInTheDocument()
    expect(api.history.post).toHaveLength(1)
    expect(JSON.parse(api.history.post[0].data)).toEqual({
      organization_name: 'Acme Insurance',
      full_name: 'Dana Levi',
      email: 'dana@acme.com',
      password: 'correct-horse', // and no confirm_password
    })
  })

  test('passwords that do not match show an error and nothing is sent', async () => {
    const { api, user } = renderApp('/register')

    await fillForm(user, { confirm_password: 'different-horse' })
    await submit(user)

    expect(await screen.findByLabelText('Confirm password')).toHaveAccessibleDescription(
      'Passwords must match',
    )
    expect(api.history.post).toHaveLength(0)
  })

  test('a password shorter than 8 characters shows an error and nothing is sent', async () => {
    const { api, user } = renderApp('/register')

    await fillForm(user, { password: 'short', confirm_password: 'short' })
    await submit(user)

    expect(await screen.findByLabelText('Password')).toHaveAccessibleDescription(
      'Password must be at least 8 characters',
    )
    expect(api.history.post).toHaveLength(0)
  })

  test('"email already registered" from the server shows on the email field', async () => {
    const { user } = renderApp('/register', (server) => {
      server.onPost('/auth/register').reply(409, { message: 'This email is already registered' })
    })

    await fillForm(user)
    await submit(user)

    expect(await screen.findByLabelText('Email')).toHaveAccessibleDescription(
      'This email is already registered',
    )
    expect(screen.getByRole('heading', { name: 'Register a new organization' })).toBeInTheDocument()
  })

  test('the Log in link goes to the login screen', async () => {
    const { user } = renderApp('/register')

    await user.click(screen.getByRole('link', { name: 'Log in' }))

    expect(screen.getByRole('heading', { name: 'Log in' })).toBeInTheDocument()
  })
})
