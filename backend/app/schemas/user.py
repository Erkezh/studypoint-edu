from __future__ import annotations

from pydantic import BaseModel, EmailStr

from app.models.enums import SubscriptionPlan, UserRole


class StudentProfileResponse(BaseModel):
    grade_level: int
    school: str | None = None


class SubscriptionResponse(BaseModel):
    plan: SubscriptionPlan
    is_active: bool


class UserMeResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    profile: StudentProfileResponse | None = None
    subscription: SubscriptionResponse | None = None

