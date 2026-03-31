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
          <template v-if="!authStore.isAuthenticated">
            <router-link to="/topics" class="text-white hover:text-gray-100 transition-colors font-medium">Оқу</router-link>
            <router-link to="/" class="text-white hover:text-gray-100 transition-colors font-medium">Диагностика</router-link>
            <router-link to="/analytics" class="text-white hover:text-gray-100 transition-colors font-medium">Талдау</router-link>
          </template>
          <template v-else>
            <router-link to="/" class="text-white hover:text-gray-100 transition-colors font-medium">Менің кабинетім</router-link>
            <router-link v-if="userGradeLevel" :to="{ name: 'class', params: { gradeId: userGradeLevel } }" class="text-white hover:text-gray-100 transition-colors font-medium">Оқу</router-link>
            <span v-else class="text-white opacity-50 cursor-not-allowed font-medium" title="Сынып көрсетілмеген">Оқу</span>
            <router-link to="/" class="text-white hover:text-gray-100 transition-colors font-medium">Диагностика</router-link>
            <router-link to="/analytics" class="text-white hover:text-gray-100 transition-colors font-medium">Талдау</router-link>
            <router-link v-if="authStore.user?.role === 'ADMIN'" to="/admin" class="text-white hover:text-gray-100 transition-colors font-medium flex items-center gap-2" title="Админ панелі">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              Админ панелі
            </router-link>
            <router-link v-if="authStore.user?.role === 'TEACHER'" to="/teacher" class="text-white hover:text-gray-100 transition-colors font-medium flex items-center gap-2" title="Мұғалім кабинеті">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
              Мұғалім кабинеті
            </router-link>
          </template>
        </div>

        <!-- Right side -->
        <div class="flex items-center gap-3">
          <!-- Profile (authenticated) -->
          <div v-if="authStore.isAuthenticated" class="relative hidden md:block" ref="profileDropdownRef">
            <button @click="toggleProfileMenu"
              class="flex items-center gap-2 rounded-full px-3 py-1.5 transition-colors"
              style="background-color: #2d8a00;" onmouseover="this.style.backgroundColor='#338000'"
              onmouseout="this.style.backgroundColor='#2d8a00'">
              <div class="w-6 h-6 bg-white rounded-full flex items-center justify-center">
                <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <span class="text-white font-medium text-sm">{{ authStore.user?.full_name || 'Пайдаланушы' }}</span>
              <svg class="w-3 h-3 text-white/70 transition-transform" :class="{ 'rotate-180': showProfileMenu }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            <!-- Dropdown menu -->
            <div v-if="showProfileMenu" class="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-xl py-2 z-50 border border-gray-100 overflow-hidden">
              <!-- Current user -->
              <div class="px-4 py-3 border-b border-gray-100">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-full flex items-center justify-center text-white font-bold text-sm"
                    :style="{ backgroundColor: isParentRole ? '#6366f1' : '#22c55e' }">
                    {{ (authStore.user?.full_name || '?')[0].toUpperCase() }}
                  </div>
                  <div>
                    <p class="font-semibold text-sm text-gray-900">{{ authStore.user?.full_name }}</p>
                    <p class="text-xs text-gray-400">{{ isParentRole ? 'Ата-ана' : (authStore.user?.role === 'STUDENT' ? 'Оқушы' : authStore.user?.role) }}</p>
                  </div>
                </div>
              </div>

              <!-- Family profiles section -->
              <div v-if="familyProfiles.length > 0" class="border-b border-gray-100">
                <p class="px-4 pt-2 pb-1 text-[11px] font-semibold text-gray-400 uppercase tracking-wide">Профильді ауыстыру</p>
                <button
                  v-for="profile in familyProfiles"
                  :key="profile.id"
                  @click="switchToProfile(profile)"
                  class="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-gray-50 transition-colors"
                  :class="{ 'opacity-50 pointer-events-none': switchingProfile }"
                >
                  <div class="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-xs"
                    :style="{ backgroundColor: profile.isParent ? '#6366f1' : '#f59e0b' }">
                    {{ profile.name[0].toUpperCase() }}
                  </div>
                  <div class="text-left">
                    <p class="text-sm font-medium text-gray-800">{{ profile.name }}</p>
                    <p class="text-[11px] text-gray-400">{{ profile.isParent ? 'Ата-ана' : `${profile.gradeLevel}-сынып` }}</p>
                  </div>
                </button>
              </div>

              <!-- Menu items -->
              <router-link to="/profile" @click="showProfileMenu = false"
                class="flex items-center gap-3 px-4 py-2.5 text-gray-700 hover:bg-gray-50 transition-colors">
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <span class="text-sm">Профиль</span>
              </router-link>
              <button @click="handleLogout"
                class="w-full flex items-center gap-3 px-4 py-2.5 text-gray-700 hover:bg-gray-50 transition-colors">
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                <span class="text-sm">Шығу</span>
              </button>
            </div>
          </div>

          <!-- Login/Register buttons (unauthenticated, desktop) -->
          <div v-if="!authStore.isAuthenticated" class="hidden md:flex items-center gap-2">
            <router-link to="/auth/login">
              <Button variant="outline" class="bg-white border-white hover:bg-gray-100" style="color: #38B000;">Кіру</Button>
            </router-link>
            <router-link to="/pricing">
              <Button variant="primary" class="text-white border"
                style="background-color: #2d8a00; border-color: #2d8a00;"
                onmouseover="this.style.backgroundColor='#338000'; this.style.borderColor='#338000'"
                onmouseout="this.style.backgroundColor='#2d8a00'; this.style.borderColor='#2d8a00'">Жазылым</Button>
            </router-link>
          </div>

          <!-- Mobile hamburger -->
          <button @click="showMobileMenu = !showMobileMenu" class="md:hidden text-white p-1.5 rounded-lg hover:bg-white/10 transition-colors">
            <svg v-if="!showMobileMenu" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" /></svg>
            <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
      </div>

      <!-- Mobile Menu -->
      <div v-if="showMobileMenu" class="md:hidden mt-4 pb-2 border-t border-white/20 pt-4 space-y-2">
        <template v-if="!authStore.isAuthenticated">
          <router-link to="/topics" @click="showMobileMenu = false" class="block px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium">Оқу</router-link>
          <router-link to="/" @click="showMobileMenu = false" class="block px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium">Диагностика</router-link>
          <router-link to="/analytics" @click="showMobileMenu = false" class="block px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium">Талдау</router-link>
          <div class="pt-2 border-t border-white/20 flex gap-2">
            <router-link to="/auth/login" @click="showMobileMenu = false" class="flex-1">
              <Button variant="outline" class="w-full bg-white border-white hover:bg-gray-100" style="color: #38B000;">Кіру</Button>
            </router-link>
            <router-link to="/pricing" @click="showMobileMenu = false" class="flex-1">
              <Button variant="primary" class="w-full text-white border" style="background-color: #2d8a00; border-color: #2d8a00;">Жазылым</Button>
            </router-link>
          </div>
        </template>

        <template v-else>
          <router-link to="/" @click="showMobileMenu = false" class="block px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium">Менің кабинетім</router-link>
          <router-link v-if="userGradeLevel" :to="{ name: 'class', params: { gradeId: userGradeLevel } }" @click="showMobileMenu = false" class="block px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium">Оқу</router-link>
          <router-link to="/" @click="showMobileMenu = false" class="block px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium">Диагностика</router-link>
          <router-link to="/analytics" @click="showMobileMenu = false" class="block px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium">Талдау</router-link>
          <router-link v-if="authStore.user?.role === 'ADMIN'" to="/admin" @click="showMobileMenu = false" class="block px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium">Админ панелі</router-link>
          <router-link v-if="authStore.user?.role === 'TEACHER'" to="/teacher" @click="showMobileMenu = false" class="block px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium">Мұғалім кабинеті</router-link>

          <!-- Mobile family profile switcher -->
          <div v-if="familyProfiles.length > 0" class="pt-2 border-t border-white/20">
            <p class="px-3 py-1 text-[11px] font-semibold text-white/50 uppercase tracking-wide">Профильді ауыстыру</p>
            <button
              v-for="profile in familyProfiles"
              :key="profile.id"
              @click="switchToProfile(profile); showMobileMenu = false"
              class="w-full flex items-center gap-3 px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors"
            >
              <div class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold"
                :style="{ backgroundColor: profile.isParent ? '#6366f1' : '#f59e0b' }">
                {{ profile.name[0].toUpperCase() }}
              </div>
              <span class="font-medium text-sm">{{ profile.name }}</span>
            </button>
          </div>

          <div class="pt-2 border-t border-white/20">
            <router-link to="/profile" @click="showMobileMenu = false" class="block px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium">Профиль</router-link>
            <button @click="handleLogout" class="w-full text-left px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium">Шығу</button>
          </div>
        </template>
      </div>
    </nav>
  </header>
</template>

<script setup lang="ts">
defineOptions({ name: 'AppHeader' })

import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'
import Button from '@/components/ui/Button.vue'

interface FamilyProfile {
  id: string
  name: string
  gradeLevel?: number | null
  isParent: boolean
  isCurrent: boolean
}

const authStore = useAuthStore()
const showProfileMenu = ref(false)
const showMobileMenu = ref(false)
const switchingProfile = ref(false)
const familyProfiles = ref<FamilyProfile[]>([])
const profileDropdownRef = ref<HTMLElement | null>(null)

const userGradeLevel = computed(() => authStore.user?.profile?.grade_level || null)
const isParentRole = computed(() => authStore.user?.role === 'PARENT')
const isChildWithParent = computed(() => authStore.user?.role === 'STUDENT' && !!(authStore.user as Record<string, unknown>)?.parent_id)
const isFamilyUser = computed(() => isParentRole.value || isChildWithParent.value)

const loadFamilyProfiles = async () => {
  if (!authStore.isAuthenticated || !isFamilyUser.value) {
    familyProfiles.value = []
    return
  }
  try {
    const resp = await authApi.getFamilyMembers()
    if (resp.data?.members) {
      familyProfiles.value = resp.data.members
        .filter(m => !m.is_current) // don't show the currently active profile in the switch list
        .map(m => ({
          id: String(m.id),
          name: m.full_name,
          gradeLevel: m.grade_level,
          isParent: m.role === 'PARENT',
          isCurrent: m.is_current,
        }))
    }
  } catch (err) {
    console.error('Failed to load family profiles:', err)
    familyProfiles.value = []
  }
}

const switchToProfile = async (profile: FamilyProfile) => {
  if (switchingProfile.value) return
  switchingProfile.value = true
  try {
    const resp = await authApi.switchProfile({ target_user_id: profile.id })
    if (resp.data) {
      authStore.setAccessToken(resp.data.access_token)
      authStore.setRefreshToken(resp.data.refresh_token)
      authStore.user = resp.data.user
      localStorage.setItem('user', JSON.stringify(resp.data.user))
    }
    showProfileMenu.value = false
    window.location.reload()
  } catch (err) {
    console.error('Failed to switch profile:', err)
  } finally {
    switchingProfile.value = false
  }
}

const toggleProfileMenu = () => {
  showProfileMenu.value = !showProfileMenu.value
}

const handleLogout = async () => {
  showProfileMenu.value = false
  showMobileMenu.value = false
  await authStore.logout()
}

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (profileDropdownRef.value && !profileDropdownRef.value.contains(target)) {
    showProfileMenu.value = false
  }
}

watch(() => authStore.user?.id, () => { loadFamilyProfiles() })

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  loadFamilyProfiles()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
