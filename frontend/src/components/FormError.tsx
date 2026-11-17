// An error about the whole form rather than one field (bad credentials, server unreachable).
// role="alert" makes screen readers announce it as soon as it appears.
export function FormError({ message }: { message: string | undefined }) {
  if (!message) return null
  return (
    <p role="alert" className="rounded bg-red-50 px-3 py-2 text-sm text-red-700">
      {message}
    </p>
  )
}
