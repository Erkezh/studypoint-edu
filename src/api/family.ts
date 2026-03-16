import apiClient from './client'

const BASE_PREFIX = '/api/v1/family'

export const familyApi = {
  getChildrenAnalytics: async () => {
    const { data } = await apiClient.get(`${BASE_PREFIX}/analytics`)
    return data.data
  },

  addChild: async (req: { name: string; grade_level: number }) => {
    const { data } = await apiClient.post(`${BASE_PREFIX}/children`, req)
    return data.data
  }
}
