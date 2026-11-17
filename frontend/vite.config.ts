import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Forward /api calls to Flask so the browser sees one origin (no CORS setup needed in dev).
    proxy: {
      '/api': 'http://localhost:5001',
    },
  },
})
