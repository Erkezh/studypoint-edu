// TypeScript типы на основе OpenAPI спецификации
// Сгенерировано на основе http://localhost:8000/api/v1/openapi.json

export enum UserRole {
  ADMIN = 'ADMIN',
  TEACHER = 'TEACHER',
  STUDENT = 'STUDENT',
  PARENT = 'PARENT',
}

export enum QuestionType {
  MCQ = 'MCQ',
  NUMERIC = 'NUMERIC',
  TEXT = 'TEXT',
  MULTI_SELECT = 'MULTI_SELECT',
  INTERACTIVE = 'INTERACTIVE', // Интерактивные задания с кодом
}

export enum SubscriptionPlan {
  FREE = 'FREE',
  PREMIUM = 'PREMIUM',
}

// API Response wrapper
export interface ApiResponse<T = any> {
  data: T | null
  meta?: {
    page?: number
    page_size?: number
    total?: number
    [key: string]: any
  }
}

// Auth types
export interface AuthRegisterRequest {
  email: string
  password: string
  full_name: string
  role?: UserRole
  grade_level: number
  school?: string | null
}

export interface AuthLoginRequest {
  email: string
  password: string
}

export interface AuthRefreshRequest {
  refresh_token: string
}

export interface AuthTokensResponse {
  access_token: string
  refresh_token: string
  token_type?: string
  user: UserMeResponse
}

export interface LogoutRequest {
  refresh_token: string
}

// User types
export interface UserMeResponse {
  id: string
  email: string
  full_name: string
  role: UserRole
  is_active: boolean
  profile?: StudentProfileResponse | null
  subscription?: SubscriptionResponse | null
}

export interface StudentProfileResponse {
  grade_level: number
  school?: string | null
}

export interface SubscriptionResponse {
  plan: SubscriptionPlan
  is_active: boolean
}

// Catalog types
export interface SubjectResponse {
  id: number
  slug: string
  title: string
}

export interface GradeResponse {
  id: number
  number: number
  title: string
}

export interface SkillListItem {
  id: number
  subject_id: number
  grade_id: number
  code: string
  title: string
  difficulty: number
  tags: string[]
}

export interface SkillDetailResponse {
  id: number
  subject_id: number
  grade_id: number
  code: string
  title: string
  difficulty: number
  tags: string[]
  description: string
  example_url?: string | null
  video_url?: string | null
  is_published: boolean
}

// Practice types
export interface PracticeSessionCreateRequest {
  skill_id: number
}

export interface PracticeSessionResponse {
  id: string
  skill_id: number
  started_at: string
  finished_at: string | null
  questions_answered: number
  correct_count: number
  wrong_count: number
  smartscore: number
  time_elapsed_sec: number
  state: Record<string, any>
  current_question?: QuestionPublic | null
}

export interface QuestionPublic {
  id: number
  skill_id: number
  type: QuestionType
  prompt: string
  data: Record<string, any>
  level: number
}

export interface PracticeSubmitRequest {
  question_id: number
  submitted_answer: Record<string, any>
  time_spent_sec: number
}

export interface PracticeSubmitResponse {
  is_correct: boolean
  explanation?: string | null
  session: PracticeSessionResponse
  next_question?: QuestionPublic | null
  finished: boolean
}

// Classroom types
export interface ClassroomResponse {
  id: string
  title: string
  grade_id: number
}

// Assignment types
export interface AssignmentResponse {
  id: string
  classroom_id: string
  skill_id: number
  due_at: string | null
}

// Analytics types (используем generic dict, так как точная схема не указана в OpenAPI)
export type AnalyticsOverview = Record<string, any>
export type AnalyticsSkills = Array<Record<string, any>>
