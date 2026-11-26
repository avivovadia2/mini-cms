import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { FNOL_STATUS_LABELS, listFnols, type FnolInfo, type FnolStatus } from '../../api/fnol'
import type { Page } from '../../api/page'
import { buttonClassName } from '../../components/Button'
import { FormError } from '../../components/FormError'
import { Pagination } from '../../components/Pagination'
import { FnolStatusBadge } from './FnolStatusBadge'

const PAGE_SIZE = 20

export function FnolListPage() {
  // Starts on "submitted": the losses still waiting for someone. '' means every status.
  const [status, setStatus] = useState<FnolStatus | ''>('submitted')
  const [pageNumber, setPageNumber] = useState(1)
  const [page, setPage] = useState<Page<FnolInfo> | null>(null)
  const [error, setError] = useState<string>()

  useEffect(() => {
    let ignore = false // a slower, older request must not overwrite a newer one
    listFnols({ page_number: pageNumber, page_size: PAGE_SIZE, status: status || undefined })
      .then((result) => {
        if (!ignore) setPage(result)
      })
      .catch(() => {
        if (!ignore) setError('Could not load FNOLs.')
      })
    return () => {
      ignore = true
    }
  }, [pageNumber, status])

  return (
    <section className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">FNOL</h1>
        <Link to="/fnol/new" className={buttonClassName}>
          Report a loss
        </Link>
      </div>

      <label className="flex w-48 flex-col gap-1 text-sm font-medium text-gray-700">
        Status
        <select
          value={status}
          onChange={(event) => {
            setStatus(event.target.value as FnolStatus | '')
            setPageNumber(1)
          }}
          className="rounded border border-gray-300 bg-white px-3 py-2 text-sm"
        >
          <option value="">All</option>
          {Object.entries(FNOL_STATUS_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </label>

      <FormError message={error} />
      {page === null ? (
        !error && <p>Loading…</p>
      ) : page.total_count === 0 ? (
        <p className="text-gray-600">No FNOLs found.</p>
      ) : (
        <>
          <table className="w-full bg-white text-left text-sm shadow">
            <thead className="border-b bg-gray-100">
              <tr>
                <th className="px-4 py-2">Reported policy number</th>
                <th className="px-4 py-2">Reporter</th>
                <th className="px-4 py-2">Loss date</th>
                <th className="px-4 py-2">Status</th>
                <th className="px-4 py-2">Matched policy</th>
              </tr>
            </thead>
            <tbody>
              {page.results.map((fnol) => (
                <tr key={fnol.id} className="border-b last:border-0">
                  <td className="px-4 py-2">
                    <Link to={`/fnol/${fnol.id}`} className="text-blue-600 hover:underline">
                      {fnol.reported_policy_number}
                    </Link>
                  </td>
                  <td className="px-4 py-2">{fnol.reporter_name}</td>
                  <td className="px-4 py-2">{fnol.loss_date}</td>
                  <td className="px-4 py-2">
                    <FnolStatusBadge status={fnol.status} />
                  </td>
                  <td className="px-4 py-2">
                    {fnol.policy ? (
                      fnol.policy.policy_number
                    ) : (
                      <span className="text-gray-500">No match</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <Pagination
            pageNumber={pageNumber}
            pageSize={PAGE_SIZE}
            totalCount={page.total_count}
            noun="FNOLs"
            onPageChange={setPageNumber}
          />
        </>
      )}
    </section>
  )
}
