import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { toApiError } from '../../api/errors'
import { getPolicy, LINE_OF_BUSINESS_LABELS, type PolicyInfo } from '../../api/policies'
import { buttonClassName } from '../../components/Button'
import { FormError } from '../../components/FormError'
import { PolicyStatusBadge } from './PolicyStatusBadge'

export function PolicyDetailPage() {
  const { policyId } = useParams<{ policyId: string }>()
  const [policy, setPolicy] = useState<PolicyInfo | null>(null)
  const [error, setError] = useState<string>()

  useEffect(() => {
    getPolicy(Number(policyId))
      .then(setPolicy)
      // 404 (unknown, or another organization's) → the server's "Policy not found".
      .catch((caught) => setError(toApiError(caught).message))
  }, [policyId])

  if (error) return <FormError message={error} />
  if (policy === null) return <p>Loading…</p>

  return (
    <section className="flex max-w-2xl flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Policy {policy.policy_number}</h1>
        <Link to={`/policies/${policy.id}/edit`} className={buttonClassName}>
          Edit
        </Link>
      </div>
      <dl className="grid grid-cols-[max-content_1fr] gap-x-8 gap-y-2 rounded bg-white p-6 shadow">
        <dt className="font-medium text-gray-600">Insured</dt>
        <dd>{policy.insured_name}</dd>
        <dt className="font-medium text-gray-600">Line of business</dt>
        <dd>{LINE_OF_BUSINESS_LABELS[policy.line_of_business]}</dd>
        <dt className="font-medium text-gray-600">Effective</dt>
        <dd>{policy.effective_date}</dd>
        <dt className="font-medium text-gray-600">Expiration</dt>
        <dd>{policy.expiration_date}</dd>
        <dt className="font-medium text-gray-600">Status</dt>
        <dd>
          <PolicyStatusBadge status={policy.status} />
        </dd>
      </dl>
      <section>
        <h2 className="text-lg font-semibold">Claims</h2>
        <p className="mt-2 text-gray-600">The claims of this policy arrive in M3.</p>
      </section>
      <Link to="/policies" className="text-sm text-blue-600 hover:underline">
        ← All policies
      </Link>
    </section>
  )
}
