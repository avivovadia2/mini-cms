import { screen, within } from '@testing-library/react'
import { describe, expect, test } from 'vitest'

import { fnolInfo, ME, policyInfo, renderApp } from '../../tests/renderApp'

describe('FnolDetailPage', () => {
  test('shows the report and its matched policy, linked', async () => {
    renderApp('/fnol/5', {
      me: ME,
      mockApi: (server) => {
        server.onGet('/fnols/5').reply(
          200,
          fnolInfo(5, {
            reported_policy_number: 'pol-7',
            reporter_email: 'ron@example.com',
            policy: policyInfo(7),
          }),
        )
      },
    })

    expect(await screen.findByRole('heading', { name: 'FNOL pol-7' })).toBeInTheDocument()
    expect(screen.getByText('Reporter 5')).toBeInTheDocument()
    expect(screen.getByText('ron@example.com')).toBeInTheDocument()
    expect(screen.getByText('Rear-ended at a traffic light.')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'POL-7' })).toHaveAttribute('href', '/policies/7')
    expect(screen.queryByText('No matching policy')).not.toBeInTheDocument()
  })

  test('an unmatched FNOL says "No matching policy"', async () => {
    renderApp('/fnol/5', {
      me: ME,
      mockApi: (server) => {
        server.onGet('/fnols/5').reply(200, fnolInfo(5))
      },
    })

    expect(await screen.findByText('No matching policy')).toBeInTheDocument()
  })

  test('rejecting needs a reason, then shows the new status and the reason', async () => {
    const { api, user } = renderApp('/fnol/5', {
      me: ME,
      mockApi: (server) => {
        server.onGet('/fnols/5').reply(200, fnolInfo(5))
        server.onPost('/fnols/5/reject').reply(
          200,
          fnolInfo(5, { status: 'rejected', rejection_reason: 'Duplicate report' }),
        )
      },
    })
    await user.click(await screen.findByRole('button', { name: 'Reject' }))
    const rejectForm = screen.getByRole('form', { name: 'Reject FNOL' })

    // Without a reason: a message, and nothing sent.
    await user.click(within(rejectForm).getByRole('button', { name: 'Confirm rejection' }))
    expect(await within(rejectForm).findByLabelText('Rejection reason')).toHaveAccessibleDescription(
      'A rejection reason is required',
    )
    expect(api.history.post).toHaveLength(0)

    await user.type(within(rejectForm).getByLabelText('Rejection reason'), 'Duplicate report')
    await user.click(within(rejectForm).getByRole('button', { name: 'Confirm rejection' }))

    expect(await screen.findByText('Rejected')).toBeInTheDocument()
    expect(screen.getByText('Duplicate report')).toBeInTheDocument()
    expect(JSON.parse(api.history.post[0].data)).toEqual({ rejection_reason: 'Duplicate report' })
    // Rejected is final: no more Reject button, and the form is gone.
    expect(screen.queryByRole('button', { name: 'Reject' })).not.toBeInTheDocument()
    expect(screen.queryByRole('form', { name: 'Reject FNOL' })).not.toBeInTheDocument()
  })

  test('a rejected FNOL shows its reason and offers no Reject', async () => {
    renderApp('/fnol/5', {
      me: ME,
      mockApi: (server) => {
        server
          .onGet('/fnols/5')
          .reply(200, fnolInfo(5, { status: 'rejected', rejection_reason: 'Not our customer' }))
      },
    })

    expect(await screen.findByText('Not our customer')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Reject' })).not.toBeInTheDocument()
  })

  test('a 409 from the server (already rejected elsewhere) shows on the reject form', async () => {
    const { user } = renderApp('/fnol/5', {
      me: ME,
      mockApi: (server) => {
        server.onGet('/fnols/5').reply(200, fnolInfo(5))
        server.onPost('/fnols/5/reject').reply(409, { message: 'This FNOL is already rejected' })
      },
    })
    await user.click(await screen.findByRole('button', { name: 'Reject' }))

    await user.type(screen.getByLabelText('Rejection reason'), 'Duplicate report')
    await user.click(screen.getByRole('button', { name: 'Confirm rejection' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('This FNOL is already rejected')
  })

  test("an unknown (or another organization's) FNOL shows the server's message", async () => {
    renderApp('/fnol/999', {
      me: ME,
      mockApi: (server) => {
        server.onGet('/fnols/999').reply(404, { message: 'FNOL not found' })
      },
    })

    expect(await screen.findByRole('alert')).toHaveTextContent('FNOL not found')
  })
})
