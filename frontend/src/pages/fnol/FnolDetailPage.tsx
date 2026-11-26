import { Form, Formik, type FormikHelpers } from 'formik'
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import * as yup from 'yup'

import { toApiError } from '../../api/errors'
import { getFnol, rejectFnol, type FnolInfo } from '../../api/fnol'
import { Button } from '../../components/Button'
import { FormError } from '../../components/FormError'
import { TextField } from '../../components/TextField'
import { FnolStatusBadge } from './FnolStatusBadge'

export function FnolDetailPage() {
  const { fnolId } = useParams<{ fnolId: string }>()
  const [fnol, setFnol] = useState<FnolInfo | null>(null)
  const [error, setError] = useState<string>()
  const [rejecting, setRejecting] = useState(false) // is the reject form open?

  useEffect(() => {
    getFnol(Number(fnolId))
      .then(setFnol)
      // 404 (unknown, or another organization's) → the server's "FNOL not found".
      .catch((caught) => setError(toApiError(caught).message))
  }, [fnolId])

  if (error) return <FormError message={error} />
  if (fnol === null) return <p>Loading…</p>

  return (
    <section className="flex max-w-2xl flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">FNOL {fnol.reported_policy_number}</h1>
        {/* Only a submitted FNOL can still be rejected. */}
        {fnol.status === 'submitted' && !rejecting && (
          <Button onClick={() => setRejecting(true)}>Reject</Button>
        )}
      </div>

      {rejecting && (
        <RejectForm
          fnolId={fnol.id}
          onRejected={(updated) => {
            setFnol(updated)
            setRejecting(false)
          }}
          onCancel={() => setRejecting(false)}
        />
      )}

      <dl className="grid grid-cols-[max-content_1fr] gap-x-8 gap-y-2 rounded bg-white p-6 shadow">
        <dt className="font-medium text-gray-600">Status</dt>
        <dd>
          <FnolStatusBadge status={fnol.status} />
        </dd>
        {fnol.rejection_reason !== null && (
          <>
            <dt className="font-medium text-gray-600">Rejection reason</dt>
            <dd className="whitespace-pre-line">{fnol.rejection_reason}</dd>
          </>
        )}
        <dt className="font-medium text-gray-600">Reporter</dt>
        <dd>{fnol.reporter_name}</dd>
        <dt className="font-medium text-gray-600">Email</dt>
        <dd>{fnol.reporter_email ?? '—'}</dd>
        <dt className="font-medium text-gray-600">Phone</dt>
        <dd>{fnol.reporter_phone ?? '—'}</dd>
        <dt className="font-medium text-gray-600">Loss date</dt>
        <dd>{fnol.loss_date}</dd>
        <dt className="font-medium text-gray-600">State</dt>
        <dd>{fnol.loss_state ?? '—'}</dd>
        <dt className="font-medium text-gray-600">Description</dt>
        <dd className="whitespace-pre-line">{fnol.loss_description}</dd>
      </dl>

      <section>
        <h2 className="text-lg font-semibold">Matched policy</h2>
        {fnol.policy ? (
          <p className="mt-2">
            <Link to={`/policies/${fnol.policy.id}`} className="text-blue-600 hover:underline">
              {fnol.policy.policy_number}
            </Link>{' '}
            · {fnol.policy.insured_name} · {fnol.policy.effective_date} →{' '}
            {fnol.policy.expiration_date}
          </p>
        ) : (
          <p className="mt-2 text-gray-600">No matching policy</p>
        )}
      </section>

      <Link to="/fnol" className="text-sm text-blue-600 hover:underline">
        ← All FNOLs
      </Link>
    </section>
  )
}

interface RejectValues {
  rejection_reason: string
}

const rejectSchema = yup.object({
  rejection_reason: yup
    .string()
    .trim()
    .required('A rejection reason is required')
    .max(5000, 'The reason is too long'),
})

interface RejectFormProps {
  fnolId: number
  onRejected: (fnol: FnolInfo) => void
  onCancel: () => void
}

function RejectForm({ fnolId, onRejected, onCancel }: RejectFormProps) {
  async function handleSubmit(values: RejectValues, helpers: FormikHelpers<RejectValues>) {
    helpers.setStatus(undefined)
    try {
      onRejected(await rejectFnol(fnolId, values.rejection_reason))
    } catch (error) {
      const apiError = toApiError(error)
      if (Object.keys(apiError.fieldErrors).length > 0) {
        helpers.setErrors(apiError.fieldErrors)
      } else {
        // e.g. 409 "This FNOL is already rejected", if someone else was quicker.
        helpers.setStatus(apiError.message)
      }
    }
  }

  return (
    <Formik
      initialValues={{ rejection_reason: '' }}
      validationSchema={rejectSchema}
      onSubmit={handleSubmit}
    >
      {({ isSubmitting, status }) => (
        <Form
          noValidate
          aria-label="Reject FNOL"
          className="flex flex-col gap-4 rounded border border-red-200 bg-red-50 p-4"
        >
          <FormError message={status} />
          <TextField name="rejection_reason" label="Rejection reason" multiline />
          <div className="flex items-center gap-4">
            <Button type="submit" disabled={isSubmitting}>
              Confirm rejection
            </Button>
            <button
              type="button"
              onClick={onCancel}
              className="text-sm text-gray-600 hover:underline"
            >
              Keep it
            </button>
          </div>
        </Form>
      )}
    </Formik>
  )
}
