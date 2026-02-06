<template>
  <header class="shadow-md" style="background-color: #38B000;">
    <nav class="container mx-auto px-4 py-3">
      <div class="flex items-center justify-between">
        <!-- Логотип слева -->
        <router-link to="/" class="flex items-center">
          <span class="text-white font-bold text-xl">StudyPoint</span>
        </router-link>

        <!-- Навигация по центру -->
        <div class="flex items-center gap-6 absolute left-1/2 transform -translate-x-1/2">
          <router-link v-if="authStore.isAuthenticated" to="/"
            class="text-white hover:text-gray-100 transition-colors font-medium">
            Менің кабинетім
          </router-link>
          <router-link v-if="authStore.isAuthenticated && userGradeLevel"
            :to="{ name: 'class', params: { gradeId: userGradeLevel } }"
            class="text-white hover:text-gray-100 transition-colors font-medium">
            Оқу
          </router-link>
          <span v-else-if="authStore.isAuthenticated && !userGradeLevel"
            class="text-white opacity-50 cursor-not-allowed font-medium" title="Сынып көрсетілмеген">
            Оқу
          </span>
          <router-link v-if="authStore.isAuthenticated" to="/"
            class="text-white hover:text-gray-100 transition-colors font-medium">
            Диагностика
          </router-link>
          <router-link v-if="authStore.isAuthenticated" to="/analytics"
            class="text-white hover:text-gray-100 transition-colors font-medium">
            Талдау
          </router-link>
          <div v-if="authStore.isAuthenticated && authStore.user?.role === 'ADMIN'" class="flex items-center gap-4">
            <router-link to="/admin/skills" class="text-white hover:text-gray-100 transition-colors font-medium"
              title="Навык қосу (Генератор)">
              ⚙️ Админ
            </router-link>
            <router-link to="/admin/plugins" class="text-white hover:text-gray-100 transition-colors font-medium"
              title="Плагиндерді жүктеу және тестке қосу">
              🔌 Плагиндер
            </router-link>
            <router-link to="/admin/questions/list" class="text-white hover:text-gray-100 transition-colors font-medium"
              title="Сұрақтарды басқару және жою">
              📝 Сұрақтар
            </router-link>
          </div>
        </div>

        <!-- Профиль справа -->
        <div class="flex items-center gap-3">
          <!-- Профиль пользователя -->
          <div v-if="authStore.isAuthenticated" class="relative">
            <button @click="showProfileMenu = !showProfileMenu"
              class="flex items-center gap-2 rounded-full px-3 py-1.5 transition-colors"
              style="background-color: #2d8a00;" onmouseover="this.style.backgroundColor='#338000'"
              onmouseout="this.style.backgroundColor='#2d8a00'">
              <div class="w-6 h-6 bg-white rounded-full flex items-center justify-center">
                <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <span class="text-white font-medium text-sm">{{ authStore.user?.full_name || 'Пайдаланушы' }}</span>
            </button>

            <!-- Выпадающее меню -->
            <div v-if="showProfileMenu" class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-2 z-50">
              <router-link to="/profile" @click="showProfileMenu = false"
                class="block px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors">
                Профиль
              </router-link>
              <button @click="handleLogout"
                class="w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors">
                Шығу
              </button>
            </div>
          </div>

          <!-- Кнопки входа/регистрации для неавторизованных -->
          <div v-else class="flex items-center gap-2">
            <router-link to="/auth/login">
              <Button variant="outline" class="bg-white border-white hover:bg-gray-100"
                style="color: #38B000;">Кіру</Button>
            </router-link>
            <router-link to="/auth/register">
              <Button variant="primary" class="text-white border"
                style="background-color: #2d8a00; border-color: #2d8a00;"
                onmouseover="this.style.backgroundColor='#338000'; this.style.borderColor='#338000'"
                onmouseout="this.style.backgroundColor='#2d8a00'; this.style.borderColor='#2d8a00'">Тіркелу</Button>
            </router-link>
          </div>
        </div>
      </div>
    </nav>
  </header>
</template>

<script setup lang="ts">
defineOptions({
  name: 'AppHeader'
})

import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import Button from '@/components/ui/Button.vue'


const authStore = useAuthStore()
const showProfileMenu = ref(false)

// Получаем класс пользователя из профиля
const userGradeLevel = computed(() => {
  return authStore.user?.profile?.grade_level || null
})

const handleLogout = async () => {
  showProfileMenu.value = false
  await authStore.logout()
}

// Закрываем меню при клике вне его
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    showProfileMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
