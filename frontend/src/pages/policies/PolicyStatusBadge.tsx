import { POLICY_STATUS_LABELS, type PolicyStatus } from '../../api/policies'

export function PolicyStatusBadge({ status }: { status: PolicyStatus }) {
  const colors = status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-200 text-gray-700'
  return (
    <span className={`rounded px-2 py-0.5 text-xs font-medium ${colors}`}>
      {POLICY_STATUS_LABELS[status]}
    </span>
  )
}
