import { screen, within } from '@testing-library/react'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, test } from 'vitest'

import { ME, renderApp, userInfo, usersPage } from '../../tests/renderApp'

async function fillAddUserForm(user: UserEvent, values: Record<string, string>) {
  const form = screen.getByRole('form', { name: 'Add user' })
  for (const [label, value] of Object.entries(values)) {
    await user.type(within(form).getByLabelText(label), value)
  }
  await user.click(within(form).getByRole('button', { name: 'Add user' }))
}

describe('UsersPage', () => {
  test("lists my organization's users with name, email and active", async () => {
    renderApp('/users', {
      me: ME,
      mockApi: (server) => {
        server
          .onGet('/users')
          .reply(200, usersPage([userInfo(1), userInfo(2, { is_active: false })]))
      },
    })

    const rows = await screen.findAllByRole('row')
    expect(rows.map((row) => row.textContent)).toEqual([
      'NameEmailActive',
      'User 1user1@acme.comYes',
      'User 2user2@acme.comNo',
    ])
    expect(screen.getByText('Page 1 of 1 · 2 users')).toBeInTheDocument()
  })

  test('Next and Previous load the other pages', async () => {
    const { api, user } = renderApp('/users', {
      me: ME,
      mockApi: (server) => {
        server.onGet('/users', { params: { page_number: 1, page_size: 20 } })
          .reply(200, usersPage([userInfo(1)], 25))
        server.onGet('/users', { params: { page_number: 2, page_size: 20 } })
          .reply(200, usersPage([userInfo(21)], 25))
      },
    })
    await screen.findByText('Page 1 of 2 · 25 users')

    await user.click(screen.getByRole('button', { name: 'Next' }))

    expect(await screen.findByText('User 21')).toBeInTheDocument()
    expect(screen.getByText('Page 2 of 2 · 25 users')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Next' })).toBeDisabled()
    expect(api.history.get.filter((r) => r.url === '/users')).toHaveLength(2)
  })

  test('the add user form shows validation messages and sends nothing', async () => {
    const { api, user } = renderApp('/users', {
      me: ME,
      mockApi: (server) => {
        server.onGet('/users').reply(200, usersPage([userInfo(1)]))
      },
    })
    await screen.findByText('User 1')

    await fillAddUserForm(user, { Email: 'not-an-email', Password: 'short' })

    const form = screen.getByRole('form', { name: 'Add user' })
    expect(within(form).getByLabelText('Full name')).toHaveAccessibleDescription(
      'Full name is required',
    )
    expect(within(form).getByLabelText('Email')).toHaveAccessibleDescription('Enter a valid email')
    expect(within(form).getByLabelText('Password')).toHaveAccessibleDescription(
      'Password must be at least 8 characters',
    )
    expect(api.history.post).toHaveLength(0)
  })

  test('a valid submit sends the right payload, clears the form and refreshes the list', async () => {
    let listCalls = 0
    const { api, user } = renderApp('/users', {
      me: ME,
      mockApi: (server) => {
        server.onGet('/users').reply(() => {
          listCalls += 1
          const users = listCalls === 1 ? [userInfo(1)] : [userInfo(1), userInfo(2)]
          return [200, usersPage(users)]
        })
        server.onPost('/users').reply(201, userInfo(2))
      },
    })
    await screen.findByText('User 1')

    await fillAddUserForm(user, {
      'Full name': 'User 2',
      Email: 'user2@acme.com',
      Password: 'another-horse',
    })

    expect(await screen.findByText('user2@acme.com')).toBeInTheDocument()
    expect(JSON.parse(api.history.post[0].data)).toEqual({
      full_name: 'User 2',
      email: 'user2@acme.com',
      password: 'another-horse',
    })
    const form = screen.getByRole('form', { name: 'Add user' })
    expect(within(form).getByLabelText('Email')).toHaveValue('')
  })

  test('"email already registered" from the server shows on the email field', async () => {
    const { user } = renderApp('/users', {
      me: ME,
      mockApi: (server) => {
        server.onGet('/users').reply(200, usersPage([userInfo(1)]))
        server.onPost('/users').reply(409, { message: 'This email is already registered' })
      },
    })
    await screen.findByText('User 1')

    await fillAddUserForm(user, {
      'Full name': 'Someone',
      Email: 'taken@acme.com',
      Password: 'another-horse',
    })

    const form = screen.getByRole('form', { name: 'Add user' })
    expect(await within(form).findByLabelText('Email')).toHaveAccessibleDescription(
      'This email is already registered',
    )
  })
})
