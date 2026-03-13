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
}

export const teacherApi = {
  createStudent(payload: CreateStudentPayload) {
    return apiClient.post<{ data: CreateStudentResponse }>('/teacher/students', payload)
  },

  getStudents() {
    return apiClient.get<{ data: StudentInfo[] }>('/teacher/students')
  }
}
