import { Field } from '@base-ui/react/field'
import { useField } from 'formik'

interface TextFieldProps {
  name: string // the Formik field name, which is also the key the backend uses
  label: string
  type?: 'text' | 'email' | 'password'
  autoComplete?: string
}

// One labelled input wired to Formik. Formik owns the value, "touched" and the error message;
// Base UI renders the <label>, <input> and error, and links them for screen readers
// (label → input, input → error through aria-describedby).
export function TextField({ name, label, type = 'text', autoComplete }: TextFieldProps) {
  const [field, meta] = useField<string>(name)
  // Show an error only once the user has left the field (or submitted), not while they type.
  const invalid = meta.touched && Boolean(meta.error)

  return (
    <Field.Root name={name} invalid={invalid} className="flex flex-col gap-1">
      <Field.Label className="text-sm font-medium text-gray-700">{label}</Field.Label>
      <Field.Control
        {...field}
        type={type}
        autoComplete={autoComplete}
        className="rounded border border-gray-300 px-3 py-2 data-[invalid]:border-red-500"
      />
      {invalid && (
        <Field.Error match className="text-sm text-red-600">
          {meta.error}
        </Field.Error>
      )}
    </Field.Root>
  )
}
