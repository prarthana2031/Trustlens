import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'https://dashboard.render.com/web/srv-d77tn2c50q8c73d2f760',
        changeOrigin: true
      }
    }
  }
})
