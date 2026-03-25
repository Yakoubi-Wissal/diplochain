import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3001,
    proxy: {
      '/api': 'http://localhost:8000',
      '/discovery': 'http://localhost:8000',
      '/health': 'http://localhost:8000'
    }
  }
})
