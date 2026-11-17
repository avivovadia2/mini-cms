import { Form, Formik, type FormikHelpers } from 'formik'
import { Link, useHistory } from 'react-router-dom'
import * as yup from 'yup'

import { register } from '../api/auth'
import { toApiError } from '../api/errors'
import { AuthCard } from '../components/AuthCard'
import { Button } from '../components/Button'
import { FormError } from '../components/FormError'
import { TextField } from '../components/TextField'
import { email, newPassword, requiredText } from '../validation'

interface RegisterValues {
  organization_name: string
  full_name: string
  email: string
  password: string
  confirm_password: string // client only: never sent to the server
}

const registerSchema = yup.object({
  organization_name: requiredText('Organization name'),
  full_name: requiredText('Full name'),
  email,
  password: newPassword,
  confirm_password: yup
    .string()
    .required('Confirm your password')
    .oneOf([yup.ref('password')], 'Passwords must match'),
})

const initialValues: RegisterValues = {
  organization_name: '',
  full_name: '',
  email: '',
  password: '',
  confirm_password: '',
}

export function RegisterPage() {
  const history = useHistory()

  async function handleSubmit(values: RegisterValues, helpers: FormikHelpers<RegisterValues>) {
    helpers.setStatus(undefined)
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { confirm_password, ...request } = values
    try {
      await register(request)
      history.push('/') // the backend logged the new user in
    } catch (error) {
      const apiError = toApiError(error)
      if (apiError.status === 409) {
        // The only conflict register can return: the email is taken. Show it on that field.
        helpers.setFieldError('email', apiError.message)
      } else if (Object.keys(apiError.fieldErrors).length > 0) {
        helpers.setErrors(apiError.fieldErrors) // 422: the server's message under each field
      } else {
        helpers.setStatus(apiError.message)
      }
    }
  }

  return (
    <AuthCard title="Register a new organization">
      <Formik
        initialValues={initialValues}
        validationSchema={registerSchema}
        onSubmit={handleSubmit}
      >
        {({ isSubmitting, status }) => (
          <Form noValidate className="flex flex-col gap-4">
            <FormError message={status} />
            <TextField name="organization_name" label="Organization name" />
            <TextField name="full_name" label="Full name" autoComplete="name" />
            <TextField name="email" label="Email" type="email" autoComplete="email" />
            <TextField
              name="password"
              label="Password"
              type="password"
              autoComplete="new-password"
            />
            <TextField
              name="confirm_password"
              label="Confirm password"
              type="password"
              autoComplete="new-password"
            />
            <Button type="submit" disabled={isSubmitting}>
              Register
            </Button>
          </Form>
        )}
      </Formik>
      <p className="mt-4 text-sm">
        Already have an account?{' '}
        <Link to="/login" className="text-blue-600 hover:underline">
          Log in
        </Link>
      </p>
    </AuthCard>
  )
}
