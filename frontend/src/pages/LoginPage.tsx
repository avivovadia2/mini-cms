import { Form, Formik, type FormikHelpers } from 'formik'
import { Link, useHistory } from 'react-router-dom'
import * as yup from 'yup'

import { login, type LoginRequest } from '../api/auth'
import { toApiError } from '../api/errors'
import { AuthCard } from '../components/AuthCard'
import { Button } from '../components/Button'
import { FormError } from '../components/FormError'
import { TextField } from '../components/TextField'
import { email } from '../validation'

const loginSchema = yup.object({
  email,
  // Like the server: only "not empty", not the new-password rule (old passwords must still work).
  password: yup.string().required('Password is required'),
})

const initialValues: LoginRequest = { email: '', password: '' }

export function LoginPage() {
  const history = useHistory()

  async function handleSubmit(values: LoginRequest, helpers: FormikHelpers<LoginRequest>) {
    helpers.setStatus(undefined)
    try {
      await login(values)
      history.push('/')
    } catch (error) {
      // 401 "Invalid email or password" (or a network error) is about the whole form.
      helpers.setStatus(toApiError(error).message)
    }
  }

  return (
    <AuthCard title="Log in">
      <Formik initialValues={initialValues} validationSchema={loginSchema} onSubmit={handleSubmit}>
        {({ isSubmitting, status }) => (
          <Form noValidate className="flex flex-col gap-4">
            <FormError message={status} />
            <TextField name="email" label="Email" type="email" autoComplete="email" />
            <TextField
              name="password"
              label="Password"
              type="password"
              autoComplete="current-password"
            />
            <Button type="submit" disabled={isSubmitting}>
              Log in
            </Button>
          </Form>
        )}
      </Formik>
      <p className="mt-4 text-sm">
        <Link to="/register" className="text-blue-600 hover:underline">
          Register a new organization
        </Link>
      </p>
    </AuthCard>
  )
}
