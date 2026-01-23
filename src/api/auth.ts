import apiClient from './client'
import type {
  ApiResponse,
  AuthRegisterRequest,
  AuthLoginRequest,
  AuthRefreshRequest,
  AuthTokensResponse,
  LogoutRequest,
  UserMeResponse,
} from '@/types/api'

export const authApi = {
  async register(data: AuthRegisterRequest): Promise<ApiResponse<AuthTokensResponse>> {
    const response = await apiClient.post<ApiResponse<AuthTokensResponse>>(
      '/auth/register',
      data
    )
    return response.data
  },

  async login(data: AuthLoginRequest): Promise<ApiResponse<AuthTokensResponse>> {
    const response = await apiClient.post<ApiResponse<AuthTokensResponse>>(
      '/auth/login',
      data
    )
    return response.data
  },

  async refresh(data: AuthRefreshRequest): Promise<ApiResponse<AuthTokensResponse>> {
    const response = await apiClient.post<ApiResponse<AuthTokensResponse>>(
      '/auth/refresh',
      data
    )
    return response.data
  },

  async logout(data: LogoutRequest): Promise<ApiResponse<Record<string, any>>> {
    const response = await apiClient.post<ApiResponse<Record<string, any>>>(
      '/auth/logout',
      data
    )
    return response.data
  },

  async getMe(): Promise<ApiResponse<UserMeResponse>> {
    const response = await apiClient.get<ApiResponse<UserMeResponse>>('/users/me')
    return response.data
  },
}
