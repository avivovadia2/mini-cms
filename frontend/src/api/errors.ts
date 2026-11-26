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
    let message = 'Some fields are invalid.'
    for (const item of data as ValidationErrorItem[]) {
      if (item.loc.length === 0) {
        // A rule about the whole request, e.g. "expiration_date must be after effective_date":
        // there is no field to show it under, so it becomes the form's message.
        message = item.msg
      } else {
        fieldErrors[String(item.loc[0])] ??= item.msg
      }
    }
    return { status, message, fieldErrors }
  }
  const message = (data as Partial<MessageBody> | undefined)?.message
  return { status, message: message ?? 'Something went wrong. Try again.', fieldErrors: {} }
}
