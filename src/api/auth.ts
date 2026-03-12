import apiClient from './client'
import type {
  ApiResponse,
  AuthRegisterRequest,
  AuthRegisterFamilyRequest,
  AuthLoginRequest,
  AuthRefreshRequest,
  AuthTokensResponse,
  AuthChildrenResponse,
  SwitchProfileRequest,
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

  async registerFamily(data: AuthRegisterFamilyRequest): Promise<ApiResponse<AuthTokensResponse>> {
    const response = await apiClient.post<ApiResponse<AuthTokensResponse>>(
      '/auth/register/family',
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

  async getChildren(): Promise<ApiResponse<AuthChildrenResponse>> {
    const response = await apiClient.get<ApiResponse<AuthChildrenResponse>>(
      '/auth/me/children'
    )
    return response.data
  },

  async switchProfile(data: SwitchProfileRequest): Promise<ApiResponse<AuthTokensResponse>> {
    const response = await apiClient.post<ApiResponse<AuthTokensResponse>>(
      '/auth/switch-profile',
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
