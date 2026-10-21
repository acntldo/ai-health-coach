import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// in dev, requests to /api go to the backend, so the browser only sees one origin
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})