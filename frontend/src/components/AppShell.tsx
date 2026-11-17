import type { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'

import { useAuth, useMe } from '../auth/authContext'
import { Button } from './Button'

const NAV_ITEMS = [
  { to: '/fnol', label: 'FNOL' },
  { to: '/claims', label: 'Claims' },
  { to: '/policies', label: 'Policies' },
  { to: '/users', label: 'Users' },
]

// The frame around every logged-in screen: top bar, navigation, then the screen itself.
export function AppShell({ children }: { children: ReactNode }) {
  const me = useMe()
  const { logOut } = useAuth()

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="flex items-center justify-between bg-white px-6 py-3 shadow">
        <span className="text-lg font-semibold">{me.organization.name}</span>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-700">{me.full_name}</span>
          <Button onClick={logOut}>Log out</Button>
        </div>
      </header>
      <nav aria-label="Main" className="flex gap-1 border-b bg-white px-4">
        {NAV_ITEMS.map((item) => (
          // NavLink: a Link that adds `activeClassName` while its URL is the current page.
          <NavLink
            key={item.to}
            to={item.to}
            className="border-b-2 border-transparent px-3 py-2 text-sm text-gray-600 hover:text-gray-900"
            activeClassName="!border-blue-600 !text-blue-700"
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
      <main className="p-6">{children}</main>
    </div>
  )
}
