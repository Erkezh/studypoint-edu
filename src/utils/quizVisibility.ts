import type { QuizResponse } from '@/api/quiz'

export type QuizVisibilityMode = 'ALWAYS' | 'SCORE_ONLY' | 'HIDDEN'

/**
 * Calculates effective visibility mode for a student for a given quiz response & user ID.
 * If the quiz deadline has passed or teacher manually ended it, uses `ended_result_visibility`.
 * Otherwise uses `result_visibility`.
 */
export function getQuizEffectiveVisibility(
  quiz: QuizResponse | null | undefined,
  studentId?: string | null
): QuizVisibilityMode {
  if (!quiz) return 'HIDDEN'

  // Find assignment for this student (or fallback to first assignment)
  const assignment = studentId
    ? quiz.assignments?.find(a => String(a.student_id) === String(studentId))
    : quiz.assignments?.[0]

  // Quiz is considered ended if assignment has an end_at date that is in the past
  const isEnded = assignment?.end_at ? new Date(assignment.end_at) <= new Date() : false

  if (isEnded) {
    return (quiz.ended_result_visibility as QuizVisibilityMode) || 'ALWAYS'
  } else {
    return (quiz.result_visibility as QuizVisibilityMode) || 'ALWAYS'
  }
}
