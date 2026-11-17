import { defineConfig } from 'vitest/config'

// Separate from vite.config.ts: Vitest 2 ships its own (newer) Vite, and its config types don't
// mix with the Vite 4 plugin there. JSX still compiles, from tsconfig's "jsx": "react-jsx".
export default defineConfig({
  test: {
    environment: 'jsdom', // a simulated browser DOM, so components can render in Node
    setupFiles: ['./src/setupTests.ts'],
    css: false,
  },
})
