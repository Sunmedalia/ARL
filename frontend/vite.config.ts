import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  base: '/next/',
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: { '/api': { target: 'https://127.0.0.1:5003', secure: false } },
  },
})
