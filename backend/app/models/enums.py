from __future__ import annotations

import enum


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"
    PARENT = "PARENT"


class QuestionType(str, enum.Enum):
    MCQ = "MCQ"
    NUMERIC = "NUMERIC"
    TEXT = "TEXT"
    MULTI_SELECT = "MULTI_SELECT"
    INTERACTIVE = "INTERACTIVE"  # Интерактивные задания с кодом (deprecated: используйте PLUGIN)
    PLUGIN = "PLUGIN"  # Интерактивное задание — iframe плагина из /static/plugins


class SubscriptionPlan(str, enum.Enum):
    FREE = "FREE"
    PREMIUM = "PREMIUM"


class AssignmentStatus(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class PracticeZone(str, enum.Enum):
    LEARNING = "LEARNING"
    REFINING = "REFINING"
    CHALLENGE = "CHALLENGE"


class MistakeType(str, enum.Enum):
    WRONG = "WRONG"
    INVALID_FORMAT = "INVALID_FORMAT"
    TIMEOUT = "TIMEOUT"
