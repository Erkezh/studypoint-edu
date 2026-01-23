import apiClient from './client'
import { rateLimitedAttempt } from './client'
import type {
  ApiResponse,
  PracticeSessionCreateRequest,
  PracticeSessionResponse,
  PracticeSubmitRequest,
  PracticeSubmitResponse,
} from '@/types/api'

export const practiceApi = {
  async createSession(
    data: PracticeSessionCreateRequest
  ): Promise<ApiResponse<PracticeSessionResponse>> {
    const response = await apiClient.post<ApiResponse<PracticeSessionResponse>>(
      '/practice/sessions',
      data
    )
    return response.data
  },

  async getSession(sessionId: string): Promise<ApiResponse<PracticeSessionResponse>> {
    const response = await apiClient.get<ApiResponse<PracticeSessionResponse>>(
      `/practice/sessions/${sessionId}`
    )
    return response.data
  },

  async getNextQuestion(sessionId: string): Promise<ApiResponse<Record<string, any>>> {
    const response = await apiClient.post<ApiResponse<Record<string, any>>>(
      `/practice/sessions/${sessionId}/next`
    )
    return response.data
  },

  async submitAnswer(
    sessionId: string,
    data: PracticeSubmitRequest,
    onRateLimit?: (retryAfter: number) => void
  ): Promise<ApiResponse<PracticeSubmitResponse>> {
    return rateLimitedAttempt(
      async () => {
        const response = await apiClient.post<ApiResponse<PracticeSubmitResponse>>(
          `/practice/sessions/${sessionId}/submit`,
          data
        )
        return response.data
      },
      onRateLimit
    )
  },

  async finishSession(sessionId: string): Promise<ApiResponse<Record<string, any>>> {
    const response = await apiClient.post<ApiResponse<Record<string, any>>>(
      `/practice/sessions/${sessionId}/finish`
    )
    return response.data
  },
}
