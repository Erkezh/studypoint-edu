import { defineStore } from 'pinia'
import { ref } from 'vue'
import { quizApi, type QuizResponse, type QuizCreateRequest, type QuizAssignmentCreate } from '@/api/quiz'
import { useAuthStore } from '@/stores/auth'

export const useQuizStore = defineStore('quiz', () => {
    const quizzes = ref<QuizResponse[]>([])
    const loading = ref(false)
    const error = ref<string | null>(null)

    const fetchQuizzes = async () => {
        loading.value = true
        error.value = null
        try {
            const authStore = useAuthStore()
            const resp = authStore.isTeacher
                ? await quizApi.listQuizzes()
                : await quizApi.listStudentAssignedQuizzes()
            quizzes.value = resp.data.data
        } catch (err: unknown) {
            const errorObj = err as { response?: { data?: { message?: string } }; message?: string }
            error.value = errorObj.response?.data?.message || errorObj.message || 'Failed to fetch quizzes'
            console.error(error.value)
        } finally {
            loading.value = false
        }
    }

    const createQuiz = async (payload: QuizCreateRequest) => {
        loading.value = true
        error.value = null
        try {
            const resp = await quizApi.createQuiz(payload)
            quizzes.value.unshift(resp.data.data)
            return resp.data.data
        } catch (err: unknown) {
            const errorObj = err as { response?: { data?: { message?: string } }; message?: string }
            error.value = errorObj.response?.data?.message || errorObj.message || 'Failed to create quiz'
            throw err
        } finally {
            loading.value = false
        }
    }

    const updateQuiz = async (quizId: string, payload: QuizCreateRequest) => {
        loading.value = true
        try {
            const resp = await quizApi.updateQuiz(quizId, payload)
            const idx = quizzes.value.findIndex(q => q.id === quizId)
            if (idx !== -1) {
                quizzes.value[idx] = resp.data.data
            }
            return resp.data.data
        } catch (err: unknown) {
            const errorObj = err as { response?: { data?: { message?: string } }; message?: string }
            error.value = errorObj.response?.data?.message || errorObj.message || 'Failed to update quiz'
            throw err
        } finally {
            loading.value = false
        }
    }

    const assignQuiz = async (payload: QuizAssignmentCreate) => {
        loading.value = true
        try {
            await quizApi.assignQuiz(payload)
        } catch (err: unknown) {
            const errorObj = err as { response?: { data?: { message?: string } }; message?: string }
            error.value = errorObj.response?.data?.message || errorObj.message || 'Failed to assign quiz'
            throw err
        } finally {
            loading.value = false
        }
    }

    const deleteQuiz = async (quizId: string) => {
        loading.value = true
        try {
            await quizApi.deleteQuiz(quizId)
            quizzes.value = quizzes.value.filter(q => q.id !== quizId)
        } catch (err: unknown) {
            const errorObj = err as { response?: { data?: { message?: string } }; message?: string }
            error.value = errorObj.response?.data?.message || errorObj.message || 'Failed to delete quiz'
            throw err
        } finally {
            loading.value = false
        }
    }

    const endQuizAssignment = async (assignmentId: string) => {
        loading.value = true
        try {
            await quizApi.endQuizAssignment(assignmentId)
            await fetchQuizzes() // Refresh quiz status
        } catch (err: unknown) {
            const errorObj = err as { response?: { data?: { message?: string } }; message?: string }
            error.value = errorObj.response?.data?.message || errorObj.message || 'Failed to end quiz assignment'
            throw err
        } finally {
            loading.value = false
        }
    }

    return {
        quizzes,
        loading,
        error,
        fetchQuizzes,
        createQuiz,
        updateQuiz,
        assignQuiz,
        deleteQuiz,
        endQuizAssignment
    }
})
