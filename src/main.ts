import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './style.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Инициализируем auth store для установки interceptors
const authStore = useAuthStore()
authStore.init() // Инициализируем store из localStorage

app.mount('#app')
