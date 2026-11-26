import { screen } from '@testing-library/react'
import { describe, expect, test } from 'vitest'

import { ME, policyInfo, renderApp } from '../../tests/renderApp'

describe('PolicyDetailPage', () => {
  test("shows the policy's fields and an Edit link", async () => {
    renderApp('/policies/4', {
      me: ME,
      mockApi: (server) => {
        server
          .onGet('/policies/4')
          .reply(200, policyInfo(4, { line_of_business: 'general_liability' }))
      },
    })

    expect(await screen.findByRole('heading', { name: 'Policy POL-4' })).toBeInTheDocument()
    expect(screen.getByText('Insured 4')).toBeInTheDocument()
    expect(screen.getByText('General liability')).toBeInTheDocument()
    expect(screen.getByText('2027-01-01')).toBeInTheDocument()
    expect(screen.getByText('Active')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Edit' })).toHaveAttribute('href', '/policies/4/edit')
  })

  test("an unknown (or another organization's) policy shows the server's message", async () => {
    renderApp('/policies/999', {
      me: ME,
      mockApi: (server) => {
        server.onGet('/policies/999').reply(404, { message: 'Policy not found' })
      },
    })

    expect(await screen.findByRole('alert')).toHaveTextContent('Policy not found')
  })
})
