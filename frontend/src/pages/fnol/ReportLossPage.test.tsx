import { screen, within } from '@testing-library/react'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, test } from 'vitest'

import { fnolInfo, ME, policyInfo, renderApp } from '../../tests/renderApp'
import { todayIso } from '../../validation'

function tomorrowIso(): string {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  const month = String(tomorrow.getMonth() + 1).padStart(2, '0')
  const day = String(tomorrow.getDate()).padStart(2, '0')
  return `${tomorrow.getFullYear()}-${month}-${day}`
}

const VALID = {
  'Reporter name': 'Ron Cohen',
  'Email (optional)': 'ron@example.com',
  'Phone (optional)': '',
  'Policy number': 'pol-7',
  'Loss date': '2026-03-10',
  Description: 'Rear-ended at a traffic light.',
  'State (optional)': 'CA',
}

async function fillForm(user: UserEvent, values: Partial<typeof VALID> = {}) {
  await screen.findByRole('form', { name: 'Report a loss' }) // wait for the session check
  for (const [label, value] of Object.entries({ ...VALID, ...values })) {
    if (value) await user.type(screen.getByLabelText(label), value)
  }
}

const submit = (user: UserEvent) =>
  user.click(
    within(screen.getByRole('form', { name: 'Report a loss' })).getByRole('button', {
      name: 'Report loss',
    }),
  )

describe('ReportLossPage', () => {
  test('a valid submit sends the report and opens the new FNOL', async () => {
    const created = fnolInfo(9, { reported_policy_number: 'pol-7', policy: policyInfo(7) })
    const { api, user } = renderApp('/fnol/new', {
      me: ME,
      mockApi: (server) => {
        server.onPost('/fnols').reply(201, created)
        server.onGet('/fnols/9').reply(200, created)
      },
    })

    await fillForm(user)
    await submit(user)

    expect(await screen.findByRole('heading', { name: 'FNOL pol-7' })).toBeInTheDocument()
    expect(JSON.parse(api.history.post[0].data)).toEqual({
      reporter_name: 'Ron Cohen',
      reporter_email: 'ron@example.com',
      reporter_phone: '', // optional: left empty, stored as null by the server
      reported_policy_number: 'pol-7',
      loss_date: '2026-03-10',
      loss_description: 'Rear-ended at a traffic light.',
      loss_state: 'CA',
    })
  })

  test('required fields show their messages and nothing is sent', async () => {
    const { api, user } = renderApp('/fnol/new', { me: ME })
    await screen.findByRole('form', { name: 'Report a loss' })

    await submit(user)

    expect(await screen.findByLabelText('Reporter name')).toHaveAccessibleDescription(
      'Reporter name is required',
    )
    expect(screen.getByLabelText('Policy number')).toHaveAccessibleDescription(
      'Policy number is required',
    )
    expect(screen.getByLabelText('Loss date')).toHaveAccessibleDescription('Loss date is required')
    expect(screen.getByLabelText('Description')).toHaveAccessibleDescription(
      'Description is required',
    )
    // Optional fields have no message.
    expect(screen.getByLabelText('Email (optional)')).not.toHaveAccessibleDescription()
    expect(api.history.post).toHaveLength(0)
  })

  test('a loss date in the future is refused', async () => {
    const { api, user } = renderApp('/fnol/new', { me: ME })

    await fillForm(user, { 'Loss date': tomorrowIso() })
    await submit(user)

    expect(await screen.findByLabelText('Loss date')).toHaveAccessibleDescription(
      'Loss date cannot be in the future',
    )
    expect(api.history.post).toHaveLength(0)
  })

  test('a loss dated today is accepted', async () => {
    const { api, user } = renderApp('/fnol/new', {
      me: ME,
      mockApi: (server) => {
        server.onPost('/fnols').reply(201, fnolInfo(9))
        server.onGet('/fnols/9').reply(200, fnolInfo(9))
      },
    })

    await fillForm(user, { 'Loss date': todayIso() })
    await submit(user)

    await screen.findByRole('heading', { name: 'FNOL POL-9' })
    expect(JSON.parse(api.history.post[0].data).loss_date).toBe(todayIso())
  })

  test('an invalid email is refused', async () => {
    const { api, user } = renderApp('/fnol/new', { me: ME })

    await fillForm(user, { 'Email (optional)': 'not-an-email' })
    await submit(user)

    expect(await screen.findByLabelText('Email (optional)')).toHaveAccessibleDescription(
      'Enter a valid email',
    )
    expect(api.history.post).toHaveLength(0)
  })

  test("the server's field errors show on their fields", async () => {
    const { user } = renderApp('/fnol/new', {
      me: ME,
      mockApi: (server) => {
        server.onPost('/fnols').reply(422, [
          { loc: ['loss_date'], msg: 'Value error, loss_date cannot be in the future' },
        ])
      },
    })

    await fillForm(user)
    await submit(user)

    expect(await screen.findByLabelText('Loss date')).toHaveAccessibleDescription(
      'Value error, loss_date cannot be in the future',
    )
  })
})
