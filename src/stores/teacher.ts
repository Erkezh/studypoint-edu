import { defineStore } from 'pinia'
import { ref } from 'vue'
import { teacherApi, type StudentInfo } from '@/api/teacher'

export const useTeacherStore = defineStore('teacher', () => {
  const students = ref<StudentInfo[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchStudents = async () => {
    loading.value = true
    error.value = null
    try {
      const { data } = await teacherApi.getStudents()
      students.value = data.data
      return data.data
    } catch (err: unknown) {
      const apiError = err as { response?: { data?: { message?: string } } }
      error.value = apiError.response?.data?.message || 'Оқушыларды жүктеу мүмкін болмады'
      throw err
    } finally {
      loading.value = false
    }
  }

  const createStudent = async (payload: { first_name: string, last_name: string, grade_id: number, classroom_id?: string }) => {
    loading.value = true
    error.value = null
    try {
      const { data } = await teacherApi.createStudent(payload)
      // fetch immediately afterwards or push
      await fetchStudents()
      return data.data
    } catch (err: unknown) {
      const apiError = err as { response?: { data?: { message?: string } } }
      error.value = apiError.response?.data?.message || 'Оқушыны құру мүмкін болмады'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    students,
    loading,
    error,
    fetchStudents,
    createStudent
  }
})
