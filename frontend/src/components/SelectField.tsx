import { Field } from '@base-ui/react/field'
import { useField } from 'formik'

interface SelectFieldProps {
  name: string // the Formik field name, which is also the key the backend uses
  label: string
  options: { value: string; label: string }[]
  placeholder?: string // a first, empty choice: "nothing chosen yet"
}

// TextField's twin for a fixed list of choices. Base UI's Field.Control renders a native
// <select> (the `render` prop), so the label, the error and data-invalid work exactly as in
// TextField, and the browser provides the dropdown and keyboard handling.
export function SelectField({ name, label, options, placeholder }: SelectFieldProps) {
  const [field, meta] = useField<string>(name)
  const invalid = meta.touched && Boolean(meta.error)

  return (
    <Field.Root name={name} invalid={invalid} className="flex flex-col gap-1">
      <Field.Label className="text-sm font-medium text-gray-700">{label}</Field.Label>
      <Field.Control
        {...field}
        render={<select />}
        className="rounded border border-gray-300 bg-white px-3 py-2 data-[invalid]:border-red-500"
      >
        {placeholder !== undefined && <option value="">{placeholder}</option>}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </Field.Control>
      {invalid && (
        <Field.Error match className="text-sm text-red-600">
          {meta.error}
        </Field.Error>
      )}
    </Field.Root>
  )
}
