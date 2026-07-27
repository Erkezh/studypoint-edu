import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from './auth'
import { authApi } from '@/api/auth'

// Mock API
vi.mock('@/api/auth', () => ({
  authApi: {
    login: vi.fn(),
    register: vi.fn(),
    getMe: vi.fn(),
    logout: vi.fn(),
  },
}))

// Mock router
vi.mock('@/router', () => ({
  default: {
    push: vi.fn(),
  },
}))

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('initializes with no user', () => {
    const store = useAuthStore()

    expect(store.isAuthenticated).toBe(false)
    expect(store.user).toBeNull()
    expect(store.accessToken).toBeNull()
  })

  it('logs in successfully', async () => {
    const store = useAuthStore()
    const mockResponse = {
      data: {
        access_token: 'token123',
        refresh_token: 'refresh123',
        user: {
          id: '1',
          email: 'test@example.com',
          full_name: 'Test User',
          role: 'STUDENT' as const,
          is_active: true,
        },
      },
    }

    vi.mocked(authApi.login).mockResolvedValue(mockResponse as any)

    await store.login({
      email: 'test@example.com',
      password: 'password123',
    })

    expect(store.isAuthenticated).toBe(true)
    expect(store.user?.email).toBe('test@example.com')
    expect(store.accessToken).toBe('token123')
  })

  it('handles login error', async () => {
    const store = useAuthStore()

    vi.mocked(authApi.login).mockRejectedValue(new Error('Login failed'))

    await expect(
      store.login({
        email: 'test@example.com',
        password: 'wrong',
      })
    ).rejects.toThrow('Login failed')

    expect(store.isAuthenticated).toBe(false)
  })
})
