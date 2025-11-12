import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/run-calculation': 'http://localhost:5000',
      '/check-status': 'http://localhost:5000',
      '/stream-logs': 'http://localhost:5000',
      '/get-viz-data': 'http://localhost:5000',
      '/get-results': 'http://localhost:5000',
      '/download-result': 'http://localhost:5000',
      '/api': 'http://localhost:5000'
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
})
