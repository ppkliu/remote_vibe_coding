import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/auth'
import type { User, LoginRequest, RegisterRequest } from '@/types/user'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))

  const isAuthenticated = computed(() => !!accessToken.value)

  async function login(credentials: LoginRequest) {
    const tokens = await authService.login(credentials)
    accessToken.value = tokens.access_token
    refreshToken.value = tokens.refresh_token
    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)
  }

  async function register(data: RegisterRequest) {
    await authService.register(data)
  }

  function logout() {
    authService.logout()
    user.value = null
    accessToken.value = null
    refreshToken.value = null
  }

  return {
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    login,
    register,
    logout
  }
})
