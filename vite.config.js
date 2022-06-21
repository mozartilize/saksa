const { resolve } = require('path')
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  esbuild: {
    sourcemap: true,
  },
  build: {
    outDir: 'saksa/static/',
    rollupOptions: {
      input: {
        home: resolve(__dirname, 'index.html'),
        auth: resolve(__dirname, 'templates/auth/index.html'),
      },
    },
  }
})
