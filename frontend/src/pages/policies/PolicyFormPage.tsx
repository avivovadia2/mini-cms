import { Form, Formik, type FormikHelpers } from 'formik'
import { useEffect, useState } from 'react'
import { Link, useHistory, useParams } from 'react-router-dom'
import * as yup from 'yup'

import { toApiError } from '../../api/errors'
import {
  createPolicy,
  getPolicy,
  LINE_OF_BUSINESS_LABELS,
  POLICY_STATUS_LABELS,
  updatePolicy,
  type LineOfBusiness,
  type PolicyInfo,
  type PolicyStatus,
} from '../../api/policies'
import { Button } from '../../components/Button'
import { FormError } from '../../components/FormError'
import { SelectField } from '../../components/SelectField'
import { TextField } from '../../components/TextField'
import { requiredText } from '../../validation'

// Form values are strings: '' is "nothing chosen / typed yet", dates are "YYYY-MM-DD".
interface PolicyFormValues {
  policy_number: string
  insured_name: string
  line_of_business: LineOfBusiness | ''
  effective_date: string
  expiration_date: string
  status: PolicyStatus
}

// Mirrors CreatePolicyRequest / UpdatePolicyRequest on the server.
const policySchema = yup.object({
  policy_number: requiredText('Policy number'),
  insured_name: requiredText('Insured name'),
  line_of_business: yup.string().required('Line of business is required'),
  effective_date: yup.string().required('Effective date is required'),
  expiration_date: yup
    .string()
    .required('Expiration date is required')
    // "YYYY-MM-DD" strings compare in date order, so no Date objects (or time zones) needed.
    // `this.parent` is the whole form's values.
    .test('after-effective', 'Expiration date must be after the effective date', function (value) {
      const effective = this.parent.effective_date as string | undefined
      return !value || !effective || value > effective
    }),
})

const EMPTY_VALUES: PolicyFormValues = {
  policy_number: '',
  insured_name: '',
  line_of_business: '',
  effective_date: '',
  expiration_date: '',
  status: 'active',
}

const lineOfBusinessOptions = Object.entries(LINE_OF_BUSINESS_LABELS).map(([value, label]) => ({
  value,
  label,
}))
const statusOptions = Object.entries(POLICY_STATUS_LABELS).map(([value, label]) => ({
  value,
  label,
}))

// One page for both /policies/new and /policies/:policyId/edit.
export function PolicyFormPage() {
  const { policyId } = useParams<{ policyId?: string }>()
  const [policy, setPolicy] = useState<PolicyInfo | null>(null)
  const [loadError, setLoadError] = useState<string>()

  useEffect(() => {
    if (policyId === undefined) return // creating: nothing to load
    getPolicy(Number(policyId))
      .then(setPolicy)
      .catch((error) => setLoadError(toApiError(error).message))
  }, [policyId])

  if (policyId === undefined) return <PolicyForm policy={null} />
  if (loadError) return <FormError message={loadError} />
  if (policy === null) return <p>Loading…</p>
  return <PolicyForm policy={policy} />
}

// Rendered only once the policy (if any) is loaded, so the initial values are final.
function PolicyForm({ policy }: { policy: PolicyInfo | null }) {
  const history = useHistory()
  const isEdit = policy !== null
  const initialValues: PolicyFormValues = policy ?? EMPTY_VALUES

  async function handleSubmit(values: PolicyFormValues, helpers: FormikHelpers<PolicyFormValues>) {
    helpers.setStatus(undefined)
    // The schema has already checked that a line of business is chosen.
    const request = {
      policy_number: values.policy_number,
      insured_name: values.insured_name,
      line_of_business: values.line_of_business as LineOfBusiness,
      effective_date: values.effective_date,
      expiration_date: values.expiration_date,
    }
    try {
      const saved = isEdit
        ? await updatePolicy(policy.id, { ...request, status: values.status })
        : await createPolicy(request) // a new policy always starts active: no status sent
      history.push(`/policies/${saved.id}`)
    } catch (error) {
      const apiError = toApiError(error)
      if (apiError.status === 409) {
        // The only conflict here: the number is taken in this organization.
        helpers.setFieldError('policy_number', apiError.message)
      } else if (Object.keys(apiError.fieldErrors).length > 0) {
        helpers.setErrors(apiError.fieldErrors)
      } else {
        helpers.setStatus(apiError.message)
      }
    }
  }

  const title = isEdit ? `Edit policy ${policy.policy_number}` : 'New policy'
  return (
    <section className="flex max-w-md flex-col gap-4">
      <h1 className="text-2xl font-semibold">{title}</h1>
      <Formik initialValues={initialValues} validationSchema={policySchema} onSubmit={handleSubmit}>
        {({ isSubmitting, status }) => (
          <Form noValidate aria-label="Policy" className="flex flex-col gap-4">
            <FormError message={status} />
            <TextField name="policy_number" label="Policy number" />
            <TextField name="insured_name" label="Insured name" />
            <SelectField
              name="line_of_business"
              label="Line of business"
              options={lineOfBusinessOptions}
              placeholder="Choose…"
            />
            <TextField name="effective_date" label="Effective date" type="date" />
            <TextField name="expiration_date" label="Expiration date" type="date" />
            {/* Only when editing: cancelling a policy is setting its status to Cancelled. */}
            {isEdit && <SelectField name="status" label="Status" options={statusOptions} />}
            <div className="flex items-center gap-4">
              <Button type="submit" disabled={isSubmitting}>
                {isEdit ? 'Save' : 'Create policy'}
              </Button>
              <Link
                to={isEdit ? `/policies/${policy.id}` : '/policies'}
                className="text-sm text-gray-600 hover:underline"
              >
                Cancel
              </Link>
            </div>
          </Form>
        )}
      </Formik>
    </section>
  )
}
