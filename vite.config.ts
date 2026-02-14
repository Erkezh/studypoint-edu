import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  // Настройка для раздачи статических файлов из miniapp-v2
  publicDir: 'public',
  server: {
    host: '0.0.0.0',
    port: 5174,
    fs: {
      // Разрешаем доступ к файлам вне корня проекта
      allow: ['..']
    }
  },
  preview: {
    host: '0.0.0.0',
    port: 5174,
  },
})
