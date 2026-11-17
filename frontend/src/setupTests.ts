import '@testing-library/jest-dom/vitest' // adds DOM matchers: toBeInTheDocument, toHaveValue, ...
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// Unmount whatever a test rendered, so the next test starts from an empty page.
afterEach(() => {
  cleanup()
})
