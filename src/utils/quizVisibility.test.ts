import { getQuizEffectiveVisibility } from './quizVisibility'
import type { QuizResponse } from '@/api/quiz'

function runTests() {
  console.log('=== Running Frontend quizVisibility Utility Tests ===')

  const mockQuizActive: QuizResponse = {
    id: 'quiz-1',
    name: 'Active Quiz',
    teacher_id: 'teacher-1',
    created_at: '2026-07-23T00:00:00Z',
    result_visibility: 'HIDDEN',
    ended_result_visibility: 'ALWAYS',
    question_order: 'FIXED',
    end_type: 'MANUAL',
    questions: [],
    assignments: [
      {
        id: 'assign-1',
        quiz_id: 'quiz-1',
        student_id: 'student-1',
        created_at: '2026-07-23T00:00:00Z',
        end_at: '2099-12-31T23:59:59Z' // In the future -> active
      }
    ]
  }

  const mockQuizEnded: QuizResponse = {
    id: 'quiz-2',
    name: 'Ended Quiz',
    teacher_id: 'teacher-1',
    created_at: '2026-07-23T00:00:00Z',
    result_visibility: 'HIDDEN',
    ended_result_visibility: 'SCORE_ONLY',
    question_order: 'FIXED',
    end_type: 'MANUAL',
    questions: [],
    assignments: [
      {
        id: 'assign-2',
        quiz_id: 'quiz-2',
        student_id: 'student-1',
        created_at: '2026-07-23T00:00:00Z',
        end_at: '2020-01-01T00:00:00Z' // In the past -> ended
      }
    ]
  }

  // Active quiz with HIDDEN result_visibility -> should return HIDDEN
  const vis1 = getQuizEffectiveVisibility(mockQuizActive, 'student-1')
  console.assert(vis1 === 'HIDDEN', `Expected HIDDEN, got ${vis1}`)
  console.log('✓ Test 1 Passed: Active quiz returns HIDDEN')

  // Ended quiz with SCORE_ONLY ended_result_visibility -> should return SCORE_ONLY
  const vis2 = getQuizEffectiveVisibility(mockQuizEnded, 'student-1')
  console.assert(vis2 === 'SCORE_ONLY', `Expected SCORE_ONLY, got ${vis2}`)
  console.log('✓ Test 2 Passed: Ended quiz returns SCORE_ONLY')

  console.log('=== Frontend quizVisibility Tests Passed! ===')
}

runTests()
