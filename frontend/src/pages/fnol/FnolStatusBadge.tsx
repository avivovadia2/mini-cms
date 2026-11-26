import { FNOL_STATUS_LABELS, type FnolStatus } from '../../api/fnol'

const COLORS: Record<FnolStatus, string> = {
  submitted: 'bg-blue-100 text-blue-800',
  converted: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
}

export function FnolStatusBadge({ status }: { status: FnolStatus }) {
  return (
    <span className={`rounded px-2 py-0.5 text-xs font-medium ${COLORS[status]}`}>
      {FNOL_STATUS_LABELS[status]}
    </span>
  )
}
