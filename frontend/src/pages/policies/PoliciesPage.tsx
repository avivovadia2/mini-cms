import { useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'

import type { Page } from '../../api/page'
import {
  LINE_OF_BUSINESS_LABELS,
  listPolicies,
  POLICY_STATUS_LABELS,
  type LineOfBusiness,
  type PolicyInfo,
  type PolicyStatus,
} from '../../api/policies'
import { buttonClassName } from '../../components/Button'
import { FormError } from '../../components/FormError'
import { Pagination } from '../../components/Pagination'
import { PolicyStatusBadge } from './PolicyStatusBadge'

const PAGE_SIZE = 20

const filterClassName = 'rounded border border-gray-300 bg-white px-3 py-2 text-sm'

export function PoliciesPage() {
  // What's typed in the search box, and what was last searched for (sent on Enter / Search),
  // so the list isn't reloaded on every keystroke.
  const [searchText, setSearchText] = useState('')
  const [search, setSearch] = useState('')
  // '' means "no filter".
  const [status, setStatus] = useState<PolicyStatus | ''>('')
  const [lineOfBusiness, setLineOfBusiness] = useState<LineOfBusiness | ''>('')
  const [pageNumber, setPageNumber] = useState(1)
  const [page, setPage] = useState<Page<PolicyInfo> | null>(null)
  const [error, setError] = useState<string>()

  useEffect(() => {
    let ignore = false // a slower, older request must not overwrite a newer one
    listPolicies({
      page_number: pageNumber,
      page_size: PAGE_SIZE,
      search: search || undefined,
      status: status || undefined,
      line_of_business: lineOfBusiness || undefined,
    })
      .then((result) => {
        if (!ignore) setPage(result)
      })
      .catch(() => {
        if (!ignore) setError('Could not load policies.')
      })
    return () => {
      ignore = true
    }
  }, [pageNumber, search, status, lineOfBusiness])

  function handleSearch(event: FormEvent) {
    event.preventDefault() // a plain <form> would reload the page
    setSearch(searchText.trim())
    setPageNumber(1) // new results: back to their first page
  }

  return (
    <section className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Policies</h1>
        <Link to="/policies/new" className={buttonClassName}>
          New policy
        </Link>
      </div>

      <div className="flex flex-wrap items-end gap-4">
        <form role="search" onSubmit={handleSearch} className="flex items-end gap-2">
          <label className="flex flex-col gap-1 text-sm font-medium text-gray-700">
            Search
            <input
              type="search"
              value={searchText}
              onChange={(event) => setSearchText(event.target.value)}
              placeholder="Policy number or insured"
              className={`${filterClassName} w-64 font-normal`}
            />
          </label>
          <button type="submit" className={buttonClassName}>
            Search
          </button>
        </form>
        <label className="flex flex-col gap-1 text-sm font-medium text-gray-700">
          Status
          <select
            value={status}
            onChange={(event) => {
              setStatus(event.target.value as PolicyStatus | '')
              setPageNumber(1)
            }}
            className={filterClassName}
          >
            <option value="">All</option>
            {Object.entries(POLICY_STATUS_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm font-medium text-gray-700">
          Line of business
          <select
            value={lineOfBusiness}
            onChange={(event) => {
              setLineOfBusiness(event.target.value as LineOfBusiness | '')
              setPageNumber(1)
            }}
            className={filterClassName}
          >
            <option value="">All</option>
            {Object.entries(LINE_OF_BUSINESS_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <FormError message={error} />
      {page === null ? (
        !error && <p>Loading…</p>
      ) : page.total_count === 0 ? (
        <p className="text-gray-600">No policies found.</p>
      ) : (
        <>
          <table className="w-full bg-white text-left text-sm shadow">
            <thead className="border-b bg-gray-100">
              <tr>
                <th className="px-4 py-2">Policy number</th>
                <th className="px-4 py-2">Insured</th>
                <th className="px-4 py-2">Line of business</th>
                <th className="px-4 py-2">Period</th>
                <th className="px-4 py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {page.results.map((policy) => (
                <tr key={policy.id} className="border-b last:border-0">
                  <td className="px-4 py-2">
                    <Link to={`/policies/${policy.id}`} className="text-blue-600 hover:underline">
                      {policy.policy_number}
                    </Link>
                  </td>
                  <td className="px-4 py-2">{policy.insured_name}</td>
                  <td className="px-4 py-2">{LINE_OF_BUSINESS_LABELS[policy.line_of_business]}</td>
                  <td className="px-4 py-2">
                    {policy.effective_date} → {policy.expiration_date}
                  </td>
                  <td className="px-4 py-2">
                    <PolicyStatusBadge status={policy.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <Pagination
            pageNumber={pageNumber}
            pageSize={PAGE_SIZE}
            totalCount={page.total_count}
            noun="policies"
            onPageChange={setPageNumber}
          />
        </>
      )}
    </section>
  )
}
