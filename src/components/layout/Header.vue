<template>
  <header class="shadow-md relative z-50" style="background-color: #38B000;">
    <nav class="container mx-auto px-4 py-3">
      <div class="flex items-center justify-between">
        <!-- Logo -->
        <router-link to="/" class="flex items-center shrink-0">
          <span class="text-white font-bold text-xl">StudyPoint</span>
        </router-link>

        <!-- Desktop Navigation (center) -->
        <div class="hidden md:flex items-center gap-6">
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
            <router-link v-if="authStore.user?.role === 'STUDENT'" to="/my-ixl" class="text-white hover:text-gray-100 transition-colors font-medium flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" /></svg>
              Менің IXL
            </router-link>
            <router-link v-if="authStore.user?.role === 'ADMIN'" to="/admin" class="text-white hover:text-gray-100 transition-colors font-medium flex items-center gap-2" title="Админ панелі">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              Админ
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

      <!-- Mobile Menu (Accordion style) -->
      <transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div v-if="showMobileMenu" class="md:hidden mt-4 pb-4 border-t border-white/20 pt-4 space-y-3">
          <template v-if="!authStore.isAuthenticated">
            <router-link to="/topics" @click="showMobileMenu = false" class="flex items-center gap-3 px-3 py-2.5 text-white hover:bg-white/10 rounded-xl transition-all font-medium">
              <svg class="w-5 h-5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>
              Оқу
            </router-link>
            <router-link to="/" @click="showMobileMenu = false" class="flex items-center gap-3 px-3 py-2.5 text-white hover:bg-white/10 rounded-xl transition-all font-medium">
              <svg class="w-5 h-5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              Диагностика
            </router-link>
            <router-link to="/analytics" @click="showMobileMenu = false" class="flex items-center gap-3 px-3 py-2.5 text-white hover:bg-white/10 rounded-xl transition-all font-medium">
              <svg class="w-5 h-5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
              Талдау
            </router-link>

            <div class="grid grid-cols-2 gap-3 pt-3">
              <router-link to="/auth/login" @click="showMobileMenu = false">
                <Button variant="outline" class="w-full bg-white border-0 py-3 rounded-xl shadow-sm" style="color: #38B000;">Кіру</Button>
              </router-link>
              <router-link to="/pricing" @click="showMobileMenu = false">
                <Button variant="primary" class="w-full py-3 rounded-xl shadow-lg border-0" style="background-color: #2d8a00;">Жазылым</Button>
              </router-link>
            </div>
          </template>

          <template v-else>
            <!-- User Profile Summary in Menu -->
            <div class="px-3 py-2 mb-2 flex items-center gap-3 bg-white/5 rounded-xl border border-white/10">
              <div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-lg"
                :style="{ backgroundColor: isParentRole ? '#6366f1' : '#22c55e' }">
                {{ (authStore.user?.full_name || '?')[0].toUpperCase() }}
              </div>
              <div class="min-w-0 flex-1">
                <p class="font-bold text-white truncate text-base">{{ authStore.user?.full_name }}</p>
                <p class="text-white/60 text-xs truncate">{{ isParentRole ? 'Ата-ана' : (authStore.user?.role === 'STUDENT' ? 'Оқушы' : authStore.user?.role) }}</p>
              </div>
            </div>

            <nav class="space-y-1">
              <router-link to="/" @click="showMobileMenu = false" class="flex items-center gap-3 px-3 py-2.5 text-white hover:bg-white/10 rounded-xl transition-all font-medium">
                <svg class="w-5 h-5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
                Басты бет
              </router-link>
              <router-link v-if="userGradeLevel" :to="{ name: 'class', params: { gradeId: userGradeLevel } }" @click="showMobileMenu = false" class="flex items-center gap-3 px-3 py-2.5 text-white hover:bg-white/10 rounded-xl transition-all font-medium">
                <svg class="w-5 h-5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>
                Оқу
              </router-link>
              <router-link to="/analytics" @click="showMobileMenu = false" class="flex items-center gap-3 px-3 py-2.5 text-white hover:bg-white/10 rounded-xl transition-all font-medium">
                <svg class="w-5 h-5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
                Талдау
              </router-link>
              <router-link v-if="authStore.user?.role === 'STUDENT'" to="/my-ixl" @click="showMobileMenu = false" class="flex items-center gap-3 px-3 py-2.5 text-white hover:bg-white/10 rounded-xl transition-all font-medium">
                <svg class="w-5 h-5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" /></svg>
                Менің IXL
              </router-link>
              <router-link v-if="authStore.user?.role === 'ADMIN'" to="/admin" @click="showMobileMenu = false" class="flex items-center gap-3 px-3 py-2.5 text-white hover:bg-white/10 rounded-xl transition-all font-medium">
                <svg class="w-5 h-5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                Админ панелі
              </router-link>
            </nav>

            <!-- Mobile family profile switcher (Vertical) -->
            <div v-if="familyProfiles.length > 0" class="pt-3 pb-1 border-t border-white/10 mt-2">
              <p class="px-3 py-1 text-[11px] font-bold text-white/40 uppercase tracking-widest">Профильді ауыстыру</p>
              <div class="space-y-1">
                <button
                  v-for="profile in familyProfiles"
                  :key="profile.id"
                  @click="switchToProfile(profile); showMobileMenu = false"
                  class="w-full flex items-center gap-3 px-3 py-2.5 text-white hover:bg-white/10 rounded-xl transition-all"
                >
                  <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shadow-sm"
                    :style="{ backgroundColor: profile.isParent ? '#6366f1' : '#f59e0b' }">
                    {{ profile.name[0].toUpperCase() }}
                  </div>
                  <div class="text-left flex-1 min-w-0">
                    <p class="font-semibold text-sm truncate text-white/90">{{ profile.name }}</p>
                    <p class="text-[10px] text-white/50">{{ profile.isParent ? 'Ата-ана' : `${profile.gradeLevel}-сынып` }}</p>
                  </div>
                </button>
              </div>
            </div>

            <div class="pt-3 border-t border-white/10 mt-2 space-y-1">
              <router-link to="/profile" @click="showMobileMenu = false" class="flex items-center gap-3 px-3 py-2.5 text-white hover:bg-white/10 rounded-xl transition-all font-medium">
                <svg class="w-5 h-5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
                Профиль
              </router-link>
              <button @click="handleLogout" class="w-full flex items-center gap-3 px-3 py-2.5 text-white hover:bg-white/10 rounded-xl transition-all font-medium">
                <svg class="w-5 h-5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
                Шығу
              </button>
            </div>
          </template>
        </div>
      </transition>
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
