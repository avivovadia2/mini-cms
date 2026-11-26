import { Form, Formik, type FormikHelpers } from 'formik'
import { Link, useHistory } from 'react-router-dom'
import * as yup from 'yup'

import { toApiError } from '../../api/errors'
import { reportLoss, type ReportLossRequest } from '../../api/fnol'
import { Button } from '../../components/Button'
import { FormError } from '../../components/FormError'
import { TextField } from '../../components/TextField'
import { requiredText, todayIso } from '../../validation'

// Mirrors ReportLossRequest on the server.
const reportLossSchema = yup.object({
  reporter_name: requiredText('Reporter name'),
  reporter_email: yup.string().trim().email('Enter a valid email'), // optional: '' is fine
  reporter_phone: yup.string().trim().max(255, 'Phone is too long'),
  reported_policy_number: requiredText('Policy number'),
  loss_date: yup
    .string()
    .required('Loss date is required')
    // "YYYY-MM-DD" strings compare in date order.
    .test('not-in-future', 'Loss date cannot be in the future', (value) => {
      return !value || value <= todayIso()
    }),
  loss_description: yup
    .string()
    .trim()
    .required('Description is required')
    .max(5000, 'Description is too long'),
  loss_state: yup.string().trim().max(255, 'State is too long'),
})

const initialValues: ReportLossRequest = {
  reporter_name: '',
  reporter_email: '',
  reporter_phone: '',
  reported_policy_number: '',
  loss_date: '',
  loss_description: '',
  loss_state: '',
}

export function ReportLossPage() {
  const history = useHistory()

  async function handleSubmit(
    values: ReportLossRequest,
    helpers: FormikHelpers<ReportLossRequest>,
  ) {
    helpers.setStatus(undefined)
    try {
      const fnol = await reportLoss(values)
      history.push(`/fnol/${fnol.id}`) // the new FNOL shows whether it matched a policy
    } catch (error) {
      const apiError = toApiError(error)
      if (Object.keys(apiError.fieldErrors).length > 0) {
        helpers.setErrors(apiError.fieldErrors)
      } else {
        helpers.setStatus(apiError.message)
      }
    }
  }

  return (
    <section className="flex max-w-md flex-col gap-4">
      <h1 className="text-2xl font-semibold">Report a loss</h1>
      <Formik
        initialValues={initialValues}
        validationSchema={reportLossSchema}
        onSubmit={handleSubmit}
      >
        {({ isSubmitting, status }) => (
          <Form noValidate aria-label="Report a loss" className="flex flex-col gap-4">
            <FormError message={status} />
            <TextField name="reporter_name" label="Reporter name" autoComplete="name" />
            <TextField name="reporter_email" label="Email (optional)" type="email" />
            <TextField name="reporter_phone" label="Phone (optional)" type="tel" />
            <TextField name="reported_policy_number" label="Policy number" />
            <TextField name="loss_date" label="Loss date" type="date" />
            <TextField name="loss_description" label="Description" multiline />
            <TextField name="loss_state" label="State (optional)" />
            <div className="flex items-center gap-4">
              <Button type="submit" disabled={isSubmitting}>
                Report loss
              </Button>
              <Link to="/fnol" className="text-sm text-gray-600 hover:underline">
                Cancel
              </Link>
            </div>
          </Form>
        )}
      </Formik>
    </section>
  )
}
