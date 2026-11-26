import { useEffect, useState } from 'react'

import type { Page } from '../../api/page'
import { listUsers, type UserInfo } from '../../api/users'
import { FormError } from '../../components/FormError'
import { Pagination } from '../../components/Pagination'
import { AddUserForm } from './AddUserForm'

const PAGE_SIZE = 20

export function UsersPage() {
  const [pageNumber, setPageNumber] = useState(1)
  const [page, setPage] = useState<Page<UserInfo> | null>(null)
  const [error, setError] = useState<string>()
  // Bumped after adding a user, to load the list again.
  const [reloadKey, setReloadKey] = useState(0)

  // Runs on first render and again whenever pageNumber or reloadKey changes.
  useEffect(() => {
    let ignore = false // a slower, older request must not overwrite a newer one
    listUsers(pageNumber, PAGE_SIZE)
      .then((result) => {
        if (!ignore) setPage(result)
      })
      .catch(() => {
        if (!ignore) setError('Could not load users.')
      })
    return () => {
      ignore = true
    }
  }, [pageNumber, reloadKey])

  return (
    <div className="flex flex-col gap-8">
      <section className="flex flex-col gap-4">
        <h1 className="text-2xl font-semibold">Users</h1>
        <FormError message={error} />
        {page === null ? (
          !error && <p>Loading…</p>
        ) : (
          <>
            <table className="w-full max-w-3xl bg-white text-left text-sm shadow">
              <thead className="border-b bg-gray-100">
                <tr>
                  <th className="px-4 py-2">Name</th>
                  <th className="px-4 py-2">Email</th>
                  <th className="px-4 py-2">Active</th>
                </tr>
              </thead>
              <tbody>
                {page.results.map((user) => (
                  <tr key={user.id} className="border-b last:border-0">
                    <td className="px-4 py-2">{user.full_name}</td>
                    <td className="px-4 py-2">{user.email}</td>
                    <td className="px-4 py-2">{user.is_active ? 'Yes' : 'No'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <Pagination
              pageNumber={pageNumber}
              pageSize={PAGE_SIZE}
              totalCount={page.total_count}
              noun="users"
              onPageChange={setPageNumber}
            />
          </>
        )}
      </section>
      <AddUserForm onAdded={() => setReloadKey((key) => key + 1)} />
    </div>
  )
}
