import { screen } from '@testing-library/react'
import { describe, expect, test } from 'vitest'

import { ME, pageOf, policyInfo, renderApp } from '../../tests/renderApp'

describe('PoliciesPage', () => {
  test('lists the policies with number, insured, line of business, period and status', async () => {
    renderApp('/policies', {
      me: ME,
      mockApi: (server) => {
        server.onGet('/policies').reply(
          200,
          pageOf([
            policyInfo(1),
            policyInfo(2, { line_of_business: 'general_liability', status: 'cancelled' }),
          ]),
        )
      },
    })

    const rows = await screen.findAllByRole('row')
    expect(rows.map((row) => row.textContent)).toEqual([
      'Policy numberInsuredLine of businessPeriodStatus',
      'POL-1Insured 1Auto2026-01-01 → 2027-01-01Active',
      'POL-2Insured 2General liability2026-01-01 → 2027-01-01Cancelled',
    ])
    expect(screen.getByRole('link', { name: 'POL-1' })).toHaveAttribute('href', '/policies/1')
    expect(screen.getByText('Page 1 of 1 · 2 policies')).toBeInTheDocument()
  })

  test('search, status and line of business are sent with the request', async () => {
    const { api, user } = renderApp('/policies', {
      me: ME,
      mockApi: (server) => {
        server.onGet('/policies').reply(200, pageOf([policyInfo(1)]))
      },
    })
    await screen.findByText('POL-1')
    const lastParams = () => api.history.get[api.history.get.length - 1].params

    // No filters at first: nothing but the page is sent.
    expect(lastParams()).toEqual({ page_number: 1, page_size: 20 })

    await user.type(screen.getByRole('searchbox', { name: 'Search' }), ' acme {Enter}')
    await user.selectOptions(screen.getByRole('combobox', { name: 'Status' }), 'Cancelled')
    await user.selectOptions(screen.getByRole('combobox', { name: 'Line of business' }), 'Property')

    expect(lastParams()).toEqual({
      page_number: 1,
      page_size: 20,
      search: 'acme',
      status: 'cancelled',
      line_of_business: 'property',
    })
  })

  test('typing in the search box sends nothing until Search', async () => {
    const { api, user } = renderApp('/policies', {
      me: ME,
      mockApi: (server) => {
        server.onGet('/policies').reply(200, pageOf([policyInfo(1)]))
      },
    })
    await screen.findByText('POL-1')

    await user.type(screen.getByRole('searchbox', { name: 'Search' }), 'acme')

    expect(api.history.get.filter((request) => request.url === '/policies')).toHaveLength(1)
  })

  test('an empty result says so', async () => {
    renderApp('/policies', {
      me: ME,
      mockApi: (server) => {
        server.onGet('/policies').reply(200, pageOf([]))
      },
    })

    expect(await screen.findByText('No policies found.')).toBeInTheDocument()
  })

  test('"New policy" opens the policy form', async () => {
    const { user } = renderApp('/policies', {
      me: ME,
      mockApi: (server) => {
        server.onGet('/policies').reply(200, pageOf([]))
      },
    })

    await user.click(await screen.findByRole('link', { name: 'New policy' }))

    expect(screen.getByRole('heading', { name: 'New policy' })).toBeInTheDocument()
  })
})
