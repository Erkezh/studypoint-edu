// TypeScript типы на основе OpenAPI спецификации
// Сгенерировано на основе http://localhost:8001/api/v1/openapi.json

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
  INTERACTIVE = 'INTERACTIVE', // Интерактивные задания с кодом (deprecated)
  PLUGIN = 'PLUGIN', // Интерактивное задание — iframe плагина
}

export enum SubscriptionPlan {
  FREE = 'FREE',
  PREMIUM = 'PREMIUM',
  FAMILY = 'FAMILY',
  CLASSROOM = 'CLASSROOM',
  SCHOOL = 'SCHOOL',
}

// API Response wrapper
export interface ApiResponse<T = unknown> {
  data: T | null
  meta?: {
    page?: number
    page_size?: number
    total?: number
    [key: string]: unknown
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

// Family Registration types
export interface ChildRegistrationData {
  name: string
  grade_level: number
}

export interface AuthRegisterFamilyRequest {
  parent_email: string
  parent_password: string
  parent_name: string
  children: ChildRegistrationData[]
}

export interface SwitchProfileRequest {
  target_user_id: string
}

export interface FamilyMemberResponse {
  id: string
  full_name: string
  role: UserRole
  grade_level?: number | null
  is_current: boolean
}

export interface AuthFamilyResponse {
  members: FamilyMemberResponse[]
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

export interface AdminUser {
  id: string
  email: string
  full_name: string
  role: UserRole
  is_active: boolean
}

export interface AdminUserUpdate {
  role?: UserRole
  is_active?: boolean
}

export interface StudentProfileResponse {
  grade_level: number
  school?: string | null
}

export type GameType = 'car' | 'character'

export interface GameSettings {
  active_game: GameType | null
  game_selected_at: string | null
  last_game_switch_at: string | null
  can_switch: boolean
  next_switch_available_at: string | null
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
  label: string
  title: string
  description: string
}

export interface TopicResponse {
  id: number
  slug: string
  title: string
  description: string
  icon: string | null
  order: number
  is_published: boolean
  parent_id: number | null
}

export interface SkillListItem {
  id: number
  subject_id: number
  grade_id: number
  topic_id: number | null
  topic_title: string | null
  code: string
  title: string
  difficulty: number
  tags: string[]
}

export interface SkillDetailResponse {
  id: number
  subject_id: number
  grade_id: number
  topic_id: number | null
  topic_title: string | null
  code: string
  title: string
  difficulty: number
  tags: string[]
  description: string
  example_url?: string | null
  video_url?: string | null
  is_published: boolean
}

export interface SkillStatsResponse {
  best_smartscore: number
  last_smartscore: number
  last_practiced_at?: string | null
  total_questions: number
  accuracy_percent: number
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
  state: Record<string, unknown>
  current_question?: QuestionPublic | null
}

export interface QuestionPublic {
  id: number
  skill_id: number
  type: QuestionType
  prompt: string
  data: Record<string, unknown>
  level: number
}

export interface PracticeSubmitRequest {
  question_id: number | string
  submitted_answer: Record<string, unknown>
  time_spent_sec: number
}

export interface GamificationReward {
  xp_gained: number
  coins_gained: number
  base_coins?: number
  combo_bonus: number
  combo_streak: number
  daily_streak?: number
  streak_bonus?: number
  milestone_coins?: number
  milestone_rewards?: Array<{ milestone: number; coins: number }>
  level_bonus?: number
  rewarded_levels?: number[]
  new_level: number
  level_up: boolean
  unlocked_vehicle?: GamificationVehicle | null
}

export interface GamificationVehicle {
  id: string
  name: string
  slug: string
  type?: string
  unlock_level: number
  level_required?: number
  unlock_xp: number
  xp_required?: number
  coin_price: number
  price?: number
  model_url?: string | null
  thumbnail_url?: string | null
  is_unlocked?: boolean
  is_owned?: boolean
  is_selected?: boolean
  locked_message?: string | null
  coins_needed?: number
}

export interface GamificationGarageItem {
  id: string
  vehicle_type: string
  item_type: string
  name: string
  slug: string
  coin_price: number
  unlock_level: number
  model_url?: string | null
  thumbnail_url?: string | null
  rarity: string
  is_owned?: boolean
}

export interface GamificationProfile {
  level: number
  xp: number
  coins: number
  combo_streak: number
  daily_streak: number
  streak?: number
  total_problems_solved: number
  next_level_xp: number
  owned_vehicles: string[]
  selected_vehicle: string
  active_vehicle?: GamificationVehicle | null
  vehicles: GamificationVehicle[]
  shop_items: GamificationGarageItem[]
}

export interface PracticeSubmitResponse {
  is_correct: boolean
  explanation?: string | null
  session: PracticeSessionResponse
  next_question?: QuestionPublic | null
  finished: boolean
  gained_xp?: number
  gained_coins?: number
  reward?: GamificationReward | null
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
export interface AnalyticsOverview {
  total_time_sec: number
  skills_practiced: number
  avg_accuracy_percent: number
  total_questions_answered: number
  total_skills_by_grade?: Record<string, number>
  [key: string]: unknown
}
export type AnalyticsSkills = Array<Record<string, unknown>>

// Notification types
export interface NotificationResponse {
  id: string
  user_id: string
  title: string
  content: string
  is_read: boolean
  created_at: string
}
