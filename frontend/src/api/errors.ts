import axios from 'axios'

// The two error bodies the backend sends (see backend/app/errors.py and the spectree hook):
// - a domain error (401, 404, 409, ...): {"message": "..."}
// - a request validation error (422): [{"loc": ["email"], "msg": "...", "type": "..."}, ...]
interface MessageBody {
  message: string
}
interface ValidationErrorItem {
  loc: (string | number)[]
  msg: string
}

export interface ApiError {
  status: number | null // null: no response at all (network down, backend not running)
  message: string
  fieldErrors: Record<string, string> // 422 only: first message per top-level field
}

export function toApiError(error: unknown): ApiError {
  if (!axios.isAxiosError(error) || !error.response) {
    return { status: null, message: 'Could not reach the server. Try again.', fieldErrors: {} }
  }
  const { status, data } = error.response
  if (Array.isArray(data)) {
    const fieldErrors: Record<string, string> = {}
    for (const item of data as ValidationErrorItem[]) {
      const field = String(item.loc[0])
      fieldErrors[field] ??= item.msg
    }
    return { status, message: 'Some fields are invalid.', fieldErrors }
  }
  const message = (data as Partial<MessageBody> | undefined)?.message
  return { status, message: message ?? 'Something went wrong. Try again.', fieldErrors: {} }
}
