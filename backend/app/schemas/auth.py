from __future__ import annotations

import uuid
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.enums import UserRole
from app.schemas.user import UserMeResponse


class AuthRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128, examples=["Password123!"])
    full_name: str = Field(min_length=1, max_length=255, examples=["Jane Doe"])
    role: UserRole = Field(default=UserRole.STUDENT)
    grade_level: int = Field(ge=-1, le=12, examples=[5])
    school: str | None = Field(default=None, max_length=255)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if v.lower() == v or v.upper() == v:
            raise ValueError("Password must include mixed case letters")
        if not any(ch.isdigit() for ch in v):
            raise ValueError("Password must include a digit")
        return v


class ChildRegistrationData(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    grade_level: int = Field(ge=-1, le=12)


class AuthRegisterFamilyRequest(BaseModel):
    parent_email: EmailStr
    parent_password: str = Field(min_length=8, max_length=128)
    parent_name: str = Field(min_length=1, max_length=255)
    children: list[ChildRegistrationData] = Field(min_length=1, max_length=10)

    @field_validator("parent_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if v.lower() == v or v.upper() == v:
            raise ValueError("Password must include mixed case letters")
        if not any(ch.isdigit() for ch in v):
            raise ValueError("Password must include a digit")
        return v


class AuthLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthRefreshRequest(BaseModel):
    refresh_token: str


class SwitchProfileRequest(BaseModel):
    child_id: uuid.UUID


class LogoutRequest(BaseModel):
    refresh_token: str


class AuthTokensResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserMeResponse


class ChildProfileResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    grade_level: int
    school: str | None

class AuthChildrenResponse(BaseModel):
    children: list[ChildProfileResponse]
