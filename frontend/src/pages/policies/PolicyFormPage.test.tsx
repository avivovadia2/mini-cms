import { screen, within } from '@testing-library/react'
import type { UserEvent } from '@testing-library/user-event'
import { describe, expect, test } from 'vitest'

import { ME, policyInfo, renderApp } from '../../tests/renderApp'

const VALID = {
  'Policy number': 'POL-7',
  'Insured name': 'Acme Corp',
  'Effective date': '2026-01-01',
  'Expiration date': '2027-01-01',
}

async function fillForm(user: UserEvent, values: Partial<typeof VALID> = {}) {
  await screen.findByRole('form', { name: 'Policy' }) // wait for the session check to finish
  for (const [label, value] of Object.entries({ ...VALID, ...values })) {
    const input = screen.getByLabelText(label)
    await user.clear(input)
    if (value) await user.type(input, value)
  }
  await user.selectOptions(screen.getByLabelText('Line of business'), 'Auto')
}

const form = () => screen.getByRole('form', { name: 'Policy' })

describe('PolicyFormPage: new policy', () => {
  test('a valid submit sends the policy without a status and opens it', async () => {
    const { api, user } = renderApp('/policies/new', {
      me: ME,
      mockApi: (server) => {
        server.onPost('/policies').reply(201, policyInfo(7, { policy_number: 'POL-7' }))
        server.onGet('/policies/7').reply(200, policyInfo(7, { policy_number: 'POL-7' }))
      },
    })

    await fillForm(user)
    await user.click(within(form()).getByRole('button', { name: 'Create policy' }))

    expect(await screen.findByRole('heading', { name: 'Policy POL-7' })).toBeInTheDocument()
    expect(JSON.parse(api.history.post[0].data)).toEqual({
      policy_number: 'POL-7',
      insured_name: 'Acme Corp',
      line_of_business: 'auto',
      effective_date: '2026-01-01',
      expiration_date: '2027-01-01',
    })
  })

  test('required fields show their messages and nothing is sent', async () => {
    const { api, user } = renderApp('/policies/new', { me: ME })

    await user.click(await screen.findByRole('button', { name: 'Create policy' }))

    expect(await screen.findByLabelText('Policy number')).toHaveAccessibleDescription(
      'Policy number is required',
    )
    expect(screen.getByLabelText('Insured name')).toHaveAccessibleDescription(
      'Insured name is required',
    )
    expect(screen.getByLabelText('Line of business')).toHaveAccessibleDescription(
      'Line of business is required',
    )
    expect(screen.getByLabelText('Effective date')).toHaveAccessibleDescription(
      'Effective date is required',
    )
    expect(api.history.post).toHaveLength(0)
  })

  test.each(['2026-01-01', '2025-06-30'])(
    'an expiration date of %s, not after the effective date, is refused',
    async (expiration) => {
      const { api, user } = renderApp('/policies/new', { me: ME })

      await fillForm(user, { 'Expiration date': expiration })
      await user.click(within(form()).getByRole('button', { name: 'Create policy' }))

      expect(await screen.findByLabelText('Expiration date')).toHaveAccessibleDescription(
        'Expiration date must be after the effective date',
      )
      expect(api.history.post).toHaveLength(0)
    },
  )

  test('a duplicate number from the server shows on the policy number field', async () => {
    const { user } = renderApp('/policies/new', {
      me: ME,
      mockApi: (server) => {
        server
          .onPost('/policies')
          .reply(409, { message: 'A policy with this number already exists' })
      },
    })

    await fillForm(user)
    await user.click(within(form()).getByRole('button', { name: 'Create policy' }))

    expect(await screen.findByLabelText('Policy number')).toHaveAccessibleDescription(
      'A policy with this number already exists',
    )
    expect(screen.getByRole('heading', { name: 'New policy' })).toBeInTheDocument()
  })

  test('a server error about the whole form shows at the top', async () => {
    const { user } = renderApp('/policies/new', {
      me: ME,
      mockApi: (server) => {
        // A model-level validation error has no field: its loc is empty.
        server.onPost('/policies').reply(422, [
          { loc: [], msg: 'Value error, expiration_date must be after effective_date' },
        ])
      },
    })

    await fillForm(user)
    await user.click(within(form()).getByRole('button', { name: 'Create policy' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'expiration_date must be after effective_date',
    )
  })
})

describe('PolicyFormPage: edit', () => {
  test('starts from the saved values, and cancelling sends the new status', async () => {
    const saved = policyInfo(3, { policy_number: 'POL-3', line_of_business: 'property' })
    const { api, user } = renderApp('/policies/3/edit', {
      me: ME,
      mockApi: (server) => {
        server.onGet('/policies/3').reply(200, saved)
        server.onPut('/policies/3').reply(200, { ...saved, status: 'cancelled' })
      },
    })

    expect(await screen.findByLabelText('Policy number')).toHaveValue('POL-3')
    expect(screen.getByLabelText('Line of business')).toHaveValue('property')

    await user.selectOptions(screen.getByLabelText('Status'), 'Cancelled')
    await user.click(within(form()).getByRole('button', { name: 'Save' }))

    expect(await screen.findByRole('heading', { name: 'Policy POL-3' })).toBeInTheDocument()
    expect(JSON.parse(api.history.put[0].data)).toEqual({
      policy_number: 'POL-3',
      insured_name: 'Insured 3',
      line_of_business: 'property',
      effective_date: '2026-01-01',
      expiration_date: '2027-01-01',
      status: 'cancelled',
    })
  })

  test('a new policy has no status field', async () => {
    renderApp('/policies/new', { me: ME })

    await screen.findByRole('heading', { name: 'New policy' })

    expect(screen.queryByLabelText('Status')).not.toBeInTheDocument()
  })
})
