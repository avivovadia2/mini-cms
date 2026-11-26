// Mirrors Page (backend app/schemas.py): one page of any list, plus the total for the pager.
export interface Page<T> {
  results: T[]
  total_count: number
}
