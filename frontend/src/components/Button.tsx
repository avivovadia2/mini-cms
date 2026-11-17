import { Button as BaseButton } from '@base-ui/react/button'
import type { ReactNode } from 'react'

interface ButtonProps {
  children: ReactNode
  type?: 'button' | 'submit'
  disabled?: boolean
  onClick?: () => void
}

export function Button({ children, type = 'button', disabled, onClick }: ButtonProps) {
  return (
    <BaseButton
      type={type}
      disabled={disabled}
      onClick={onClick}
      className="rounded bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 data-[disabled]:opacity-50"
    >
      {children}
    </BaseButton>
  )
}
