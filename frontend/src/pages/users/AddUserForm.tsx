import { Form, Formik, type FormikHelpers } from 'formik'
import * as yup from 'yup'

import { toApiError } from '../../api/errors'
import { addUser, type AddUserRequest } from '../../api/users'
import { Button } from '../../components/Button'
import { FormError } from '../../components/FormError'
import { TextField } from '../../components/TextField'
import { email, newPassword, requiredText } from '../../validation'

const addUserSchema = yup.object({
  full_name: requiredText('Full name'),
  email,
  password: newPassword,
})

const initialValues: AddUserRequest = { full_name: '', email: '', password: '' }

// No organization field: the backend always adds the user to the logged-in user's organization.
export function AddUserForm({ onAdded }: { onAdded: () => void }) {
  async function handleSubmit(values: AddUserRequest, helpers: FormikHelpers<AddUserRequest>) {
    helpers.setStatus(undefined)
    try {
      await addUser(values)
      helpers.resetForm() // empty the form for the next user
      onAdded()
    } catch (error) {
      const apiError = toApiError(error)
      if (apiError.status === 409) {
        helpers.setFieldError('email', apiError.message)
      } else if (Object.keys(apiError.fieldErrors).length > 0) {
        helpers.setErrors(apiError.fieldErrors)
      } else {
        helpers.setStatus(apiError.message)
      }
    }
  }

  return (
    <Formik initialValues={initialValues} validationSchema={addUserSchema} onSubmit={handleSubmit}>
      {({ isSubmitting, status }) => (
        <Form noValidate aria-label="Add user" className="flex max-w-sm flex-col gap-4">
          <h2 className="text-lg font-semibold">Add user</h2>
          <FormError message={status} />
          <TextField name="full_name" label="Full name" />
          <TextField name="email" label="Email" type="email" />
          <TextField name="password" label="Password" type="password" autoComplete="new-password" />
          <Button type="submit" disabled={isSubmitting}>
            Add user
          </Button>
        </Form>
      )}
    </Formik>
  )
}
