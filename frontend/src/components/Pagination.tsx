import { Button } from './Button'

interface PaginationProps {
  pageNumber: number
  pageSize: number
  totalCount: number
  noun: string // "users", "policies": shown after the total
  onPageChange: (pageNumber: number) => void
}

// Previous / "Page 2 of 5 · 93 policies" / Next, under every paginated table.
export function Pagination({
  pageNumber,
  pageSize,
  totalCount,
  noun,
  onPageChange,
}: PaginationProps) {
  const pageCount = Math.max(1, Math.ceil(totalCount / pageSize))
  return (
    <div className="flex items-center gap-4 text-sm">
      <Button disabled={pageNumber <= 1} onClick={() => onPageChange(pageNumber - 1)}>
        Previous
      </Button>
      <span>
        Page {pageNumber} of {pageCount} · {totalCount} {noun}
      </span>
      <Button disabled={pageNumber >= pageCount} onClick={() => onPageChange(pageNumber + 1)}>
        Next
      </Button>
    </div>
  )
}
