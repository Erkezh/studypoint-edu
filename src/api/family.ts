import apiClient from './client'

const BASE_PREFIX = '/api/v1/family'

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
