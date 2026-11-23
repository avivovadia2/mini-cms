import * as yup from 'yup'

// Client-side rules that mirror the server's (backend: RequiredText in app/schemas.py,
// Password in app/modules/users/schemas/user.py, EmailStr). The server still validates
// everything; these only give instant feedback. Change both sides together.

export const requiredText = (label: string) =>
  yup.string().trim().required(`${label} is required`).max(255, `${label} is too long`)

export const email = yup.string().trim().required('Email is required').email('Enter a valid email')

export const newPassword = yup
  .string()
  .required('Password is required')
  .min(8, 'Password must be at least 8 characters')
  .max(128, 'Password is too long')
