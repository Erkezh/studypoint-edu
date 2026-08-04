import apiClient from './client'

// apiClient already uses /api/v1 as its base URL.
const BASE_PREFIX = '/family'

export const familyApi = {
  getChildrenAnalytics: async () => {
    const { data } = await apiClient.get(`${BASE_PREFIX}/analytics`)
    return data.data
  },

  getChildAnalytics: async (childId: string, includeQuestions = true) => {
    const { data } = await apiClient.get(`${BASE_PREFIX}/children/${childId}/analytics`, {
      params: {
        include_questions: includeQuestions,
      },
    })
    return data.data
  },

  addChild: async (req: { name: string; grade_level: number }) => {
    const { data } = await apiClient.post(`${BASE_PREFIX}/children`, req)
    return data.data
  }
}
