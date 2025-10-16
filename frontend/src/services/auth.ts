import apiClient from './api'
import type { LoginRequest, RegisterRequest, TokenResponse } from '@/types/user'

export const authService = {
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/auth/login', credentials)
    return response.data
  },

  async register(data: RegisterRequest): Promise<void> {
    await apiClient.post('/auth/register', data)
  },

  async refresh(refreshToken: string): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken
    })
    return response.data
  },

  logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }
}
