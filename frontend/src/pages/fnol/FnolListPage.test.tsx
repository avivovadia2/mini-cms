import { screen } from '@testing-library/react'
import { describe, expect, test } from 'vitest'

import { fnolInfo, ME, pageOf, policyInfo, renderApp } from '../../tests/renderApp'

describe('FnolListPage', () => {
  test('lists FNOLs with reporter, loss date, status and matched policy', async () => {
    renderApp('/fnol', {
      me: ME,
      mockApi: (server) => {
        server.onGet('/fnols').reply(
          200,
          pageOf([
            fnolInfo(1, { reported_policy_number: 'pol-7', policy: policyInfo(7) }),
            fnolInfo(2, { reported_policy_number: 'UNKNOWN' }),
          ]),
        )
      },
    })

    const rows = await screen.findAllByRole('row')
    expect(rows.map((row) => row.textContent)).toEqual([
      'Reported policy numberReporterLoss dateStatusMatched policy',
      'pol-7Reporter 12026-03-10SubmittedPOL-7',
      'UNKNOWNReporter 22026-03-10SubmittedNo match',
    ])
    expect(screen.getByRole('link', { name: 'pol-7' })).toHaveAttribute('href', '/fnol/1')
  })

  test('shows submitted FNOLs first, and the status filter changes the request', async () => {
    const { api, user } = renderApp('/fnol', {
      me: ME,
      mockApi: (server) => {
        server.onGet('/fnols').reply(200, pageOf([fnolInfo(1)]))
      },
    })
    await screen.findByText('POL-1')
    const lastParams = () => api.history.get[api.history.get.length - 1].params

    expect(screen.getByRole('combobox', { name: 'Status' })).toHaveValue('submitted')
    expect(lastParams()).toEqual({ page_number: 1, page_size: 20, status: 'submitted' })

    await user.selectOptions(screen.getByRole('combobox', { name: 'Status' }), 'Rejected')
    expect(lastParams()).toEqual({ page_number: 1, page_size: 20, status: 'rejected' })

    await user.selectOptions(screen.getByRole('combobox', { name: 'Status' }), 'All')
    expect(lastParams()).toEqual({ page_number: 1, page_size: 20 })
  })

  test('"Report a loss" opens the form', async () => {
    const { user } = renderApp('/fnol', {
      me: ME,
      mockApi: (server) => {
        server.onGet('/fnols').reply(200, pageOf([]))
      },
    })

    await user.click(await screen.findByRole('link', { name: 'Report a loss' }))

    expect(screen.getByRole('heading', { name: 'Report a loss' })).toBeInTheDocument()
  })
})
