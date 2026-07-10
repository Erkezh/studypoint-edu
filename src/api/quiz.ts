import apiClient from './client'

export enum QuizQuestionOrder {
    FIXED = 'FIXED',
    RANDOMIZED = 'RANDOMIZED'
}

export enum QuizResultVisibility {
    ALWAYS = 'ALWAYS',
    SCORE_ONLY = 'SCORE_ONLY',
    HIDDEN = 'HIDDEN'
}

export enum QuizEndType {
    MANUAL = 'MANUAL',
    SCHEDULED = 'SCHEDULED'
}

export interface QuizQuestionCreate {
    question_id: number
    position: number
    seed?: number | null
}

export interface QuizCreateRequest {
    name: string
    question_order: QuizQuestionOrder
    result_visibility: QuizResultVisibility
    end_type: QuizEndType
    questions: QuizQuestionCreate[]
}

export interface QuizResponse {
    id: string
    name: string
    teacher_id: string
    question_order: QuizQuestionOrder
    result_visibility: QuizResultVisibility
    end_type: QuizEndType
    created_at: string
    questions: Array<{
        id: string
        question_id: number
        position: number
        seed?: number | null
        question?: {
            id: number
            prompt: string
            type: string
            data?: Record<string, unknown>
            correct_answer?: Record<string, unknown>
            level?: number
        }
    }>
}

export interface QuizAssignmentCreate {
    quiz_id: string
    classroom_id?: string
    student_id?: string
    due_at?: string
    end_at?: string
}

export interface StudentQuizAssignmentResponse {
    id: string
    quiz_id: string
    quiz: QuizResponse
    due_at: string | null
    end_at: string | null
    created_at: string
}

export const quizApi = {
    createQuiz(payload: QuizCreateRequest) {
        return apiClient.post<{ data: QuizResponse }>('/teacher/quizzes', payload)
    },

    updateQuiz(quizId: string, payload: QuizCreateRequest) {
        return apiClient.put<{ data: QuizResponse }>(`/teacher/quizzes/${quizId}`, payload)
    },

    listQuizzes() {
        return apiClient.get<{ data: QuizResponse[] }>('/teacher/quizzes')
    },

    assignQuiz(payload: QuizAssignmentCreate) {
        return apiClient.post<{ data: unknown }>('/teacher/quizzes/assign', payload)
    },

    deleteQuiz(quizId: string) {
        return apiClient.delete<{ data: boolean }>(`/teacher/quizzes/${quizId}`)
    },

    listStudentAssignedQuizzes() {
        return apiClient.get<{ data: QuizResponse[] }>('/student/quizzes/all')
    }
}
