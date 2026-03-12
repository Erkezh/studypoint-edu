<template>
  <header class="shadow-md relative z-50" style="background-color: #38B000;">
    <nav class="container mx-auto px-4 py-3">
      <div class="flex items-center justify-between">
        <!-- Logo -->
        <router-link to="/" class="flex items-center shrink-0">
          <span class="text-white font-bold text-xl">StudyPoint</span>
        </router-link>

        <!-- Desktop Navigation (center) -->
        <div class="hidden md:flex items-center gap-6 absolute left-1/2 transform -translate-x-1/2">
          <!-- Unauthenticated nav links -->
          <template v-if="!authStore.isAuthenticated">
            <router-link to="/topics"
              class="text-white hover:text-gray-100 transition-colors font-medium">
              Оқу
            </router-link>
            <router-link to="/"
              class="text-white hover:text-gray-100 transition-colors font-medium">
              Диагностика
            </router-link>
            <router-link to="/analytics"
              class="text-white hover:text-gray-100 transition-colors font-medium">
              Талдау
            </router-link>
          </template>

          <!-- Authenticated nav links -->
          <template v-else>
            <router-link to="/"
              class="text-white hover:text-gray-100 transition-colors font-medium">
              Менің кабинетім
            </router-link>
            <router-link v-if="userGradeLevel"
              :to="{ name: 'class', params: { gradeId: userGradeLevel } }"
              class="text-white hover:text-gray-100 transition-colors font-medium">
              Оқу
            </router-link>
            <span v-else
              class="text-white opacity-50 cursor-not-allowed font-medium" title="Сынып көрсетілмеген">
              Оқу
            </span>
            <router-link to="/"
              class="text-white hover:text-gray-100 transition-colors font-medium">
              Диагностика
            </router-link>
            <router-link to="/analytics"
              class="text-white hover:text-gray-100 transition-colors font-medium">
              Талдау
            </router-link>
            <router-link v-if="authStore.user?.role === 'ADMIN'"
              to="/admin" class="text-white hover:text-gray-100 transition-colors font-medium flex items-center gap-2"
              title="Админ панелі">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              Админ панелі
            </router-link>
          </template>
        </div>

        <!-- Right side -->
        <div class="flex items-center gap-3">
          <!-- Profile (authenticated) -->
          <div v-if="authStore.isAuthenticated" class="relative hidden md:block">
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

            <!-- Dropdown menu -->
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

          <!-- Login/Register buttons (unauthenticated, desktop) -->
          <div v-if="!authStore.isAuthenticated" class="hidden md:flex items-center gap-2">
            <router-link to="/auth/login">
              <Button variant="outline" class="bg-white border-white hover:bg-gray-100"
                style="color: #38B000;">Кіру</Button>
            </router-link>
            <router-link to="/pricing">
              <Button variant="primary" class="text-white border"
                style="background-color: #2d8a00; border-color: #2d8a00;"
                onmouseover="this.style.backgroundColor='#338000'; this.style.borderColor='#338000'"
                onmouseout="this.style.backgroundColor='#2d8a00'; this.style.borderColor='#2d8a00'">Жазылым</Button>
            </router-link>
          </div>

          <!-- Mobile hamburger button -->
          <button @click="showMobileMenu = !showMobileMenu"
            class="md:hidden text-white p-1.5 rounded-lg hover:bg-white/10 transition-colors">
            <svg v-if="!showMobileMenu" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile Menu -->
      <div v-if="showMobileMenu" class="md:hidden mt-4 pb-2 border-t border-white/20 pt-4 space-y-2">
        <template v-if="!authStore.isAuthenticated">
          <router-link to="/topics" @click="showMobileMenu = false"
            class="block px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium">
            Оқу
          </router-link>
          <router-link to="/" @click="showMobileMenu = false"
            class="block px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium">
            Диагностика
          </router-link>
          <router-link to="/analytics" @click="showMobileMenu = false"
            class="block px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium">
            Талдау
          </router-link>
          <div class="pt-2 border-t border-white/20 flex gap-2">
            <router-link to="/auth/login" @click="showMobileMenu = false" class="flex-1">
              <Button variant="outline" class="w-full bg-white border-white hover:bg-gray-100"
                style="color: #38B000;">Кіру</Button>
            </router-link>
            <router-link to="/pricing" @click="showMobileMenu = false" class="flex-1">
              <Button variant="primary" class="w-full text-white border"
                style="background-color: #2d8a00; border-color: #2d8a00;">Жазылым</Button>
            </router-link>
          </div>
        </template>

        <template v-else>
          <router-link to="/" @click="showMobileMenu = false"
            class="block px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium">
            Менің кабинетім
          </router-link>
          <router-link v-if="userGradeLevel" :to="{ name: 'class', params: { gradeId: userGradeLevel } }"
            @click="showMobileMenu = false"
            class="block px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium">
            Оқу
          </router-link>
          <router-link to="/" @click="showMobileMenu = false"
            class="block px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium">
            Диагностика
          </router-link>
          <router-link to="/analytics" @click="showMobileMenu = false"
            class="block px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium">
            Талдау
          </router-link>
          <router-link v-if="authStore.user?.role === 'ADMIN'" to="/admin" @click="showMobileMenu = false"
            class="block px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium">
            Админ панелі
          </router-link>
          <div class="pt-2 border-t border-white/20">
            <router-link to="/profile" @click="showMobileMenu = false"
              class="block px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium">
              Профиль
            </router-link>
            <button @click="handleLogout"
              class="w-full text-left px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium">
              Шығу
            </button>
          </div>
        </template>
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
const showMobileMenu = ref(false)

// User grade level from profile
const userGradeLevel = computed(() => {
  return authStore.user?.profile?.grade_level || null
})

const handleLogout = async () => {
  showProfileMenu.value = false
  showMobileMenu.value = false
  await authStore.logout()
}

// Close menus on outside click
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
