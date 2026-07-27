import { describe, expect, it } from 'vitest'
import { getQuizEffectiveVisibility } from './quizVisibility'
import {
  QuizEndType,
  QuizQuestionOrder,
  QuizResultVisibility,
  type QuizResponse,
} from '@/api/quiz'

describe('getQuizEffectiveVisibility', () => {
  it('uses the active quiz visibility before the assignment ends', () => {
    const mockQuizActive: QuizResponse = {
      id: 'quiz-1',
      name: 'Active Quiz',
      teacher_id: 'teacher-1',
      created_at: '2026-07-23T00:00:00Z',
      result_visibility: QuizResultVisibility.HIDDEN,
      ended_result_visibility: QuizResultVisibility.ALWAYS,
      question_order: QuizQuestionOrder.FIXED,
      end_type: QuizEndType.MANUAL,
      questions: [],
      assignments: [
        {
          id: 'assign-1',
          quiz_id: 'quiz-1',
          student_id: 'student-1',
          created_at: '2026-07-23T00:00:00Z',
          end_at: '2099-12-31T23:59:59Z',
        },
      ],
    }

    expect(getQuizEffectiveVisibility(mockQuizActive, 'student-1')).toBe('HIDDEN')
  })

  it('uses ended visibility after the assignment deadline', () => {
    const mockQuizEnded: QuizResponse = {
      id: 'quiz-2',
      name: 'Ended Quiz',
      teacher_id: 'teacher-1',
      created_at: '2026-07-23T00:00:00Z',
      result_visibility: QuizResultVisibility.HIDDEN,
      ended_result_visibility: QuizResultVisibility.SCORE_ONLY,
      question_order: QuizQuestionOrder.FIXED,
      end_type: QuizEndType.MANUAL,
      questions: [],
      assignments: [
        {
          id: 'assign-2',
          quiz_id: 'quiz-2',
          student_id: 'student-1',
          created_at: '2026-07-23T00:00:00Z',
          end_at: '2020-01-01T00:00:00Z',
        },
      ],
    }

    expect(getQuizEffectiveVisibility(mockQuizEnded, 'student-1')).toBe('SCORE_ONLY')
  })
})
