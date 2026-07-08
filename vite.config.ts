import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const allowedHosts = ['edu.studypoint.kz']
const apiProxy = {
  '/api': {
    target: 'http://127.0.0.1:8001',
    changeOrigin: true,
  },
  '/static/modules': {
    target: 'http://127.0.0.1:8001',
    changeOrigin: true,
  },
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) return
          if (id.includes('chart.js') || id.includes('vue-chartjs')) return 'charts'
          if (id.includes('axios') || id.includes('uuid')) return 'network'
          if (id.includes('vue') || id.includes('pinia') || id.includes('vue-router')) return 'framework'
        },
      },
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  publicDir: 'public',
  server: {
    host: '0.0.0.0',
    port: 5174,
    allowedHosts,
    proxy: apiProxy,
    fs: {
      // Разрешаем доступ к файлам вне корня проекта
      allow: ['..']
    }
  },
  preview: {
    host: '0.0.0.0',
    port: 5174,
    allowedHosts,
    proxy: apiProxy,
  },
})
