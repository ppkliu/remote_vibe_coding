/**
 * Unit tests for auth store (T120)
 *
 * Tests the authentication store:
 * - Login/logout functionality
 * - Token management
 * - User state persistence
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'

describe('Auth Store (T120)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    // Clear localStorage
    localStorage.clear()
    // Mock fetch
    global.fetch = vi.fn()
  })

  describe('Initial State', () => {
    it('should have empty initial state', () => {
      const store = useAuthStore()
      expect(store.user).toBeNull()
      expect(store.accessToken).toBeNull()
      expect(store.refreshToken).toBeNull()
      expect(store.isAuthenticated).toBe(false)
    })

    it('should restore tokens from localStorage', () => {
      localStorage.setItem('accessToken', 'test_access_token')
      localStorage.setItem('refreshToken', 'test_refresh_token')

      const store = useAuthStore()
      expect(store.accessToken).toBe('test_access_token')
      expect(store.refreshToken).toBe('test_refresh_token')
    })
  })

  describe('Login', () => {
    it('should successfully login user', async () => {
      const store = useAuthStore()

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access_token: 'access123',
          refresh_token: 'refresh123'
        })
      })

      await store.login({
        username: 'testuser',
        password: 'password123'
      })

      expect(store.isAuthenticated).toBe(true)
      expect(store.accessToken).toBe('access123')
      expect(store.refreshToken).toBe('refresh123')
      expect(localStorage.getItem('accessToken')).toBe('access123')
    })

    it('should handle login errors', async () => {
      const store = useAuthStore()

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({
          detail: 'Incorrect username or password'
        })
      })

      try {
        await store.login({
          username: 'testuser',
          password: 'wrongpassword'
        })
        expect.fail('Should have thrown error')
      } catch (error: any) {
        expect(error.message).toContain('Incorrect')
      }

      expect(store.isAuthenticated).toBe(false)
    })

    it('should handle network errors', async () => {
      const store = useAuthStore()

      ;(global.fetch as any).mockRejectedValueOnce(
        new Error('Network error')
      )

      try {
        await store.login({
          username: 'testuser',
          password: 'password123'
        })
        expect.fail('Should have thrown error')
      } catch (error: any) {
        expect(error.message).toContain('Network error')
      }

      expect(store.isAuthenticated).toBe(false)
    })
  })

  describe('Register', () => {
    it('should successfully register user', async () => {
      const store = useAuthStore()

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          id: 'user123',
          username: 'newuser',
          email: 'new@example.com'
        })
      })

      const result = await store.register({
        username: 'newuser',
        email: 'new@example.com',
        password: 'password123'
      })

      expect(result.username).toBe('newuser')
      expect(result.email).toBe('new@example.com')
    })

    it('should handle duplicate username error', async () => {
      const store = useAuthStore()

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({
          detail: 'Username or email already registered'
        })
      })

      try {
        await store.register({
          username: 'existing',
          email: 'new@example.com',
          password: 'password123'
        })
        expect.fail('Should have thrown error')
      } catch (error: any) {
        expect(error.message).toContain('already registered')
      }
    })
  })

  describe('Logout', () => {
    it('should clear auth state on logout', async () => {
      const store = useAuthStore()

      // Set initial state
      store.accessToken = 'test_token'
      store.refreshToken = 'test_refresh'
      store.user = { id: '123', username: 'testuser', email: 'test@example.com' }

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ detail: 'Logout successful' })
      })

      await store.logout()

      expect(store.isAuthenticated).toBe(false)
      expect(store.accessToken).toBeNull()
      expect(store.refreshToken).toBeNull()
      expect(store.user).toBeNull()
      expect(localStorage.getItem('accessToken')).toBeNull()
    })
  })

  describe('Token Refresh', () => {
    it('should refresh access token', async () => {
      const store = useAuthStore()
      store.refreshToken = 'old_refresh_token'

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access_token: 'new_access_token',
          refresh_token: 'new_refresh_token'
        })
      })

      await store.refreshToken()

      expect(store.accessToken).toBe('new_access_token')
      expect(store.refreshToken).toBe('new_refresh_token')
    })

    it('should handle refresh errors', async () => {
      const store = useAuthStore()
      store.refreshToken = 'invalid_refresh_token'

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({
          detail: 'Invalid refresh token'
        })
      })

      try {
        await store.refreshToken()
        expect.fail('Should have thrown error')
      } catch (error: any) {
        expect(error.message).toContain('Invalid')
      }
    })
  })

  describe('Computed Properties', () => {
    it('should correctly compute isAuthenticated', () => {
      const store = useAuthStore()

      expect(store.isAuthenticated).toBe(false)

      store.accessToken = 'test_token'
      expect(store.isAuthenticated).toBe(true)

      store.accessToken = null
      expect(store.isAuthenticated).toBe(false)
    })
  })

  describe('Persistence', () => {
    it('should persist auth state to localStorage', async () => {
      const store = useAuthStore()

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access_token: 'persist_access',
          refresh_token: 'persist_refresh'
        })
      })

      await store.login({
        username: 'testuser',
        password: 'password123'
      })

      expect(localStorage.getItem('accessToken')).toBe('persist_access')
      expect(localStorage.getItem('refreshToken')).toBe('persist_refresh')
    })

    it('should clear localStorage on logout', async () => {
      localStorage.setItem('accessToken', 'test_token')
      localStorage.setItem('refreshToken', 'test_refresh')

      const store = useAuthStore()

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ detail: 'Logout successful' })
      })

      await store.logout()

      expect(localStorage.getItem('accessToken')).toBeNull()
      expect(localStorage.getItem('refreshToken')).toBeNull()
    })
  })
})
