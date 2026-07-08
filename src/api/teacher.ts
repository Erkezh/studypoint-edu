import apiClient from './client'

interface CreateStudentPayload {
  first_name: string
  last_name: string
  grade_id: number
  classroom_id?: string
}

interface CreateStudentResponse {
  id: string
  full_name: string
  username: string
  password: string
}

export interface StudentInfo {
  id: string
  full_name: string
  username: string
  classrooms: string[]
  grade_level: number | null
  password?: string
}

export const teacherApi = {
  createStudent(payload: CreateStudentPayload) {
    return apiClient.post<{ data: CreateStudentResponse }>('/teacher/students', payload)
  },

  getStudents() {
    return apiClient.get<{ data: StudentInfo[] }>('/teacher/students')
  },

  getStudentAnalytics(studentId: string, includeQuestions = true) {
    return apiClient.get<{ data: Record<string, unknown> }>(`/teacher/students/${studentId}/analytics`, {
      params: {
        include_questions: includeQuestions,
      },
    })
  },

  getTeacherQuickviewAnalytics(includeQuestions = false) {
    return apiClient.get<{ data: Record<string, unknown> }>('/teacher/analytics/quickview', {
      params: {
        include_questions: includeQuestions,
      },
    })
  },

  getTeacherQuickviewQuestions() {
    return apiClient.get<{ data: Array<Record<string, unknown>> }>('/teacher/analytics/quickview/questions')
  },

  resetStudentPassword(studentId: string) {
    return apiClient.post<{ data: { username: string; password: string } }>(`/teacher/students/${studentId}/reset-password`, {})
  },

  deleteStudent(studentId: string) {
    return apiClient.delete<{ data: { deleted: string } }>(`/teacher/students/${studentId}`)
  },

  getLiveStudents() {
    return apiClient.get<{
      data: {
        active_count: number
        inactive_count: number
        needs_help_count: number
        total_students: number
        inactive_students: Array<{
          student_id: string
          full_name: string
        }>
        students: Array<{
          student_id: string
          full_name: string
          skill_name: string
          smartscore: number
          correct: number
          wrong: number
          questions_answered: number
          last_active_seconds_ago: number
        }>
      }
    }>('/teacher/live-students')
  },

  getGradeTopics(gradeNum: number) {
    return apiClient.get<{ data: Array<{ id: number; title: string; description: string }> }>(`/teacher/catalog/grades/${gradeNum}/topics`)
  },

  getTopicQuestions(topicId: number) {
    return apiClient.get<{ data: Array<{ id: number; type: string; prompt: string; level: number; explanation: string }> }>(`/teacher/catalog/topics/${topicId}/questions`)
  },

  getSkillQuestions(skillId: number) {
    return apiClient.get<{ data: Array<{ id: number; type: string; prompt: string; level: number; explanation: string; data?: Record<string, unknown>; correct_answer?: Record<string, unknown> }> }>(`/teacher/catalog/skills/${skillId}/questions`)
  },
}
