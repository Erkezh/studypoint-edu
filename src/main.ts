import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './style.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

// Инициализируем auth store до router, чтобы guards видели состояние из localStorage.
const authStore = useAuthStore()
authStore.init()

app.use(router)

app.mount('#app')
